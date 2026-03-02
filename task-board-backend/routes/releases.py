from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import pandas as pd
import io

from db import get_db, User, Task, Status, Release, ReleaseTag, ReleaseFollow, Message, UserMessage, Defect
from schemas import (
    ReleaseCreate, ReleaseUpdate, Release as ReleaseSchema, 
    ReleaseWithDetails, ReleaseTagCreate, 
    ReleaseTag as ReleaseTagSchema
)
from auth import get_current_user, get_current_active_user, get_pm_or_admin_user, check_permission

router = APIRouter()


def require_permission(permission_code: str):
    """Create a dependency that requires a specific permission"""
    async def dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        return await check_permission(permission_code, current_user, db)
    return dependency


async def get_non_viewer_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Get current user who is not a viewer"""
    # 由于已移除role字段，此函数不再需要特殊检查
    # 权限检查将通过权限切片进行
    return current_user


# ReleaseTag endpoints


@router.get("/tags", response_model=List[ReleaseTagSchema])
async def get_release_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all release tags"""
    tags = db.query(ReleaseTag).all()
    return tags


@router.post("/tags", response_model=ReleaseTagSchema)
async def create_release_tag(
    tag: ReleaseTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("release_tag:create"))
):
    """Create a new release tag"""
    existing_tag = db.query(ReleaseTag).filter(ReleaseTag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Release tag with this name already exists"
        )
    db_tag = ReleaseTag(
        name=tag.name,
        color=tag.color
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.put("/tags/{tag_id}", response_model=ReleaseTagSchema)
async def update_release_tag(
    tag_id: int,
    tag: ReleaseTagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("release_tag:update"))
):
    """Update a release tag"""
    db_tag = db.query(ReleaseTag).filter(ReleaseTag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release tag not found"
        )
    # Check if name is already used by another tag
    existing_tag = db.query(ReleaseTag).filter(
        ReleaseTag.name == tag.name,
        ReleaseTag.id != tag_id
    ).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Release tag with this name already exists"
        )
    db_tag.name = tag.name
    db_tag.color = tag.color
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_release_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("release_tag:delete"))
):
    """Delete release tag by ID"""
    # Find tag
    tag = db.query(ReleaseTag).filter(ReleaseTag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release tag not found"
        )
    
    # Delete tag
    db.delete(tag)
    db.commit()
    
    return None


# Release endpoints


@router.get("", response_model=dict)
async def get_releases(
    status: Optional[str] = Query(None, description="Filter by status"),
    follow_status: Optional[str] = Query(None, description="Filter by follow status: all, followed, unfollowed"),
    search: Optional[str] = Query(None, description="Search by title or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=1000, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get releases with optional filters and pagination"""
    query = db.query(Release).options(
        joinedload(Release.tasks).joinedload(Task.status),
        joinedload(Release.tasks).joinedload(Task.assignee),
        joinedload(Release.tasks).joinedload(Task.assignees),
        joinedload(Release.tasks).joinedload(Task.tags),
        joinedload(Release.tasks).joinedload(Task.creator),
        joinedload(Release.creator),
        joinedload(Release.tags)
    )
    
    # Apply filters
    if status:
        # Split comma-separated string into list of statuses
        statuses = [s.strip() for s in status.split(',')]
        query = query.filter(Release.status.in_(statuses))
    if follow_status:
        if follow_status == "followed":
            # Filter releases that the current user is following
            query = query.join(ReleaseFollow, Release.id == ReleaseFollow.release_id).filter(
                ReleaseFollow.user_id == current_user.id
            )
        elif follow_status == "unfollowed":
            # Filter releases that the current user is not following
            followed_release_ids = db.query(ReleaseFollow.release_id).filter(
                ReleaseFollow.user_id == current_user.id
            ).subquery()
            query = query.filter(~Release.id.in_(followed_release_ids))
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Release.title.ilike(search_term)) |
            (Release.description.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    releases = query.offset(offset).limit(page_size).all()
    
    # Convert to schema with details
    release_list = []
    for release in releases:
        # 查询该发版的缺陷数
        defect_count = db.query(Defect).filter(Defect.release_id == release.id).count()
        
        release_list.append(
            ReleaseWithDetails(
                id=release.id,
                title=release.title,
                description=release.description,
                status=release.status,
                planned_release_date=release.planned_release_date,
                actual_release_date=release.actual_release_date,
                task_ids=[task.id for task in release.tasks],
                tag_ids=[tag.id for tag in release.tags],
                created_by=release.created_by,
                creator=release.creator,
                tasks=release.tasks,
                tags=release.tags,
                defect_count=defect_count,
                created_at=release.created_at,
                updated_at=release.updated_at
            )
        )
    
    # Return paginated response
    return {
        "items": release_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.post("", response_model=ReleaseWithDetails)
async def create_release(
    release: ReleaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("release:create"))
):
    """Create a new release"""
    # Create release
    db_release = Release(
        title=release.title,
        description=release.description,
        status=release.status,
        planned_release_date=release.planned_release_date,
        actual_release_date=release.actual_release_date,
        created_by=current_user.id
    )
    db.add(db_release)
    db.commit()
    db.refresh(db_release)
    
    # Add tasks if provided
    if release.task_ids:
        # Only allow tasks that are not already associated with a release
        tasks = db.query(Task).filter(
            Task.id.in_(release.task_ids),
            Task.release_id.is_(None)
        ).all()
        
        # Check if release status is "已发版" and any task is not completed
        if release.status == "已发版":
            completed_status = db.query(Status).filter(Status.name == "已完成").first()
            if completed_status:
                for task in tasks:
                    if task.status_id != completed_status.id:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="关联任务中存在未完成任务，发版状态不可选已完成！"
                        )
        
        for task in tasks:
            task.release_id = db_release.id
        
        db.commit()
        db.refresh(db_release)
    
    # Add tags if provided
    if release.tag_ids:
        tags = db.query(ReleaseTag).filter(ReleaseTag.id.in_(release.tag_ids)).all()
        db_release.tags = tags
        db.commit()
        db.refresh(db_release)
    
    # Return release with details
    return ReleaseWithDetails(
        id=db_release.id,
        title=db_release.title,
        description=db_release.description,
        status=db_release.status,
        planned_release_date=db_release.planned_release_date,
        actual_release_date=db_release.actual_release_date,
        task_ids=[task.id for task in db_release.tasks],
        tag_ids=[tag.id for tag in db_release.tags],
        created_by=db_release.created_by,
        creator=db_release.creator,
        tasks=db_release.tasks,
        tags=db_release.tags,
        created_at=db_release.created_at,
        updated_at=db_release.updated_at
    )


@router.get("/available-tasks")
async def get_available_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_non_viewer_user)
):
    """Get tasks that are not associated with any release"""
    # Query tasks with no release
    tasks = db.query(Task).filter(
        Task.release_id.is_(None)
    ).all()
    
    # Build clean response
    task_list = []
    for task in tasks:
        # Get status information
        status = db.query(Status).filter(Status.id == task.status_id).first()
        status_info = {
            "id": status.id if status else None,
            "name": status.name if status else "未知",
            "color": status.color if status else "#999999",
            "order_index": status.order_index if status else 0
        }
        
        # Get assignee information if exists
        assignee_info = None
        if task.assignee_id:
            assignee = db.query(User).filter(User.id == task.assignee_id).first()
            if assignee:
                assignee_info = {
                    "id": assignee.id,
                    "username": assignee.username,
                    "name": assignee.name
                }
        
        # Get creator information
        creator_info = None
        creator = db.query(User).filter(User.id == task.created_by).first()
        if creator:
            creator_info = {
                "id": creator.id,
                "username": creator.username,
                "name": creator.name
            }
        
        # Get assignees information
        assignees_info = []
        for assignee in task.assignees:
            assignees_info.append({
                "id": assignee.id,
                "username": assignee.username,
                "name": assignee.name
            })
        
        # Get tags information
        tags_info = []
        for tag in task.tags:
            tags_info.append({
                "id": tag.id,
                "name": tag.name,
                "color": tag.color
            })
        
        # Build task dictionary
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "status_id": task.status_id,
            "status": status_info,
            "assignee_id": task.assignee_id,
            "assignee": assignee_info,
            "assignee_ids": [a.id for a in task.assignees],
            "assignees": assignees_info,
            "priority": task.priority,
            "creator": creator_info,
            "tags": tags_info,
            "created_by": task.created_by,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }
        
        task_list.append(task_dict)
    
    return task_list


@router.get("/export")
async def export_releases(
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by title or description"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("release:export"))
):
    """Export releases with optional filters to Excel file"""
    query = db.query(Release).options(
        joinedload(Release.tasks).joinedload(Task.status),
        joinedload(Release.tasks).joinedload(Task.assignee),
        joinedload(Release.tasks).joinedload(Task.assignees),
        joinedload(Release.tasks).joinedload(Task.tags),
        joinedload(Release.tasks).joinedload(Task.creator),
        joinedload(Release.creator),
        joinedload(Release.tags)
    )
    
    # Apply filters
    if status:
        # Split comma-separated string into list of statuses
        statuses = [s.strip() for s in status.split(',')]
        query = query.filter(Release.status.in_(statuses))
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Release.title.ilike(search_term)) |
            (Release.description.ilike(search_term))
        )
    
    # Get all releases without pagination
    releases = query.all()
    
    # Prepare data for export
    data = []
    for release in releases:
        # Collect task IDs and statuses
        task_info = []
        for task in release.tasks:
            task_status = task.status.name if task.status else "未知"
            task_info.append(f"{task.id}({task_status})")
        tasks_str = ", ".join(task_info) if task_info else "无"
        
        # Collect tags names
        tag_names = [tag.name for tag in release.tags]
        tags_str = ", ".join(tag_names) if tag_names else "无"
        
        # Prepare row data
        row = {
            "发版ID": release.id,
            "发版标题": release.title,
            "发版描述": release.description,
            "发版状态": release.status,
            "计划发版日期": release.planned_release_date.strftime("%Y-%m-%d") if release.planned_release_date else "",
            "实际发版日期": release.actual_release_date.strftime("%Y-%m-%d") if release.actual_release_date else "",
            "关联任务": tasks_str,
            "标签": tags_str,
            "创建人": release.creator.name if release.creator else "",
            "创建时间": release.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "更新时间": release.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='发版列表', index=False)
    output.seek(0)
    
    # Return as streaming response
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=releases_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )


@router.get("/{release_id}", response_model=ReleaseWithDetails)
async def get_release(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get release by ID"""
    release = db.query(Release).options(
        joinedload(Release.tasks).joinedload(Task.status),
        joinedload(Release.tasks).joinedload(Task.assignee),
        joinedload(Release.tasks).joinedload(Task.assignees),
        joinedload(Release.tasks).joinedload(Task.tags),
        joinedload(Release.tasks).joinedload(Task.creator),
        joinedload(Release.creator),
        joinedload(Release.tags)
    ).filter(Release.id == release_id).first()
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found"
        )
    
    # 查询该发版的缺陷数
    defect_count = db.query(Defect).filter(Defect.release_id == release.id).count()
    
    # Return release with details
    return ReleaseWithDetails(
        id=release.id,
        title=release.title,
        description=release.description,
        status=release.status,
        planned_release_date=release.planned_release_date,
        actual_release_date=release.actual_release_date,
        task_ids=[task.id for task in release.tasks],
        tag_ids=[tag.id for tag in release.tags],
        created_by=release.created_by,
        creator=release.creator,
        tasks=release.tasks,
        tags=release.tags,
        defect_count=defect_count,
        created_at=release.created_at,
        updated_at=release.updated_at
    )


@router.put("/{release_id}", response_model=ReleaseWithDetails)
async def update_release(
    release_id: int,
    release_update: ReleaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("release:update"))
):
    """Update release by ID"""
    # Find release
    release = db.query(Release).filter(Release.id == release_id).first()
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found"
        )
    
    # Store old status for notification
    old_status = release.status
    
    # Update release
    update_data = release_update.model_dump(exclude_unset=True)
    
    # Handle task_ids separately
    task_ids = update_data.pop('task_ids', None)
    
    # Handle tag_ids separately
    tag_ids = update_data.pop('tag_ids', None)
    
    # Update other fields
    for field, value in update_data.items():
        setattr(release, field, value)
    
    # Update tasks if provided
    if task_ids is not None:
        # First clear existing task associations
        for task in release.tasks:
            task.release_id = None
        
        # Then add new tasks (including existing ones from this release)
        if task_ids:
            tasks = db.query(Task).filter(
                Task.id.in_(task_ids),
                (Task.release_id.is_(None)) | (Task.release_id == release_id)
            ).all()
            
            # Check if release status is "已发版" and any task is not completed
            if update_data.get('status') == "已发版":
                completed_status = db.query(Status).filter(Status.name == "已完成").first()
                if completed_status:
                    for task in tasks:
                        if task.status_id != completed_status.id:
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="关联任务中存在未完成任务，发版状态不可选已完成！"
                            )
            
            for task in tasks:
                task.release_id = release.id
    
    # Update tags if provided
    if tag_ids is not None:
        tags = db.query(ReleaseTag).filter(ReleaseTag.id.in_(tag_ids)).all()
        release.tags = tags
    
    db.commit()
    db.refresh(release)
    
    # Check if status changed and send notification
    if 'status' in update_data and old_status != release.status:
        # Check if status changed to/from "已发版"
        if (old_status == "已发版" and release.status != "已发版") or \
           (old_status != "已发版" and release.status == "已发版"):
            # Get all followers of this release
            followers = db.query(ReleaseFollow).filter(
                ReleaseFollow.release_id == release_id
            ).all()
            
            if followers:
                # Create message
                message = Message(
                    message_type="release_message",
                    title=f"发版状态变更通知",
                    content=f"发版记录「{release.title}」的状态已从「{old_status}」变更为「{release.status}」",
                    redirect_path=f"/release/{release_id}",
                    created_by=current_user.id,
                    created_at=datetime.utcnow()
                )
                db.add(message)
                db.commit()
                db.refresh(message)
                
                # Create user messages for all followers
                user_messages = []
                for follow in followers:
                    # Don't send notification to the user who made the change
                    if follow.user_id != current_user.id:
                        user_message = UserMessage(
                            user_id=follow.user_id,
                            message_id=message.id,
                            is_read=0,
                            read_at=None
                        )
                        user_messages.append(user_message)
                
                if user_messages:
                    db.add_all(user_messages)
                    db.commit()
    
    # Return updated release with details
    return ReleaseWithDetails(
        id=release.id,
        title=release.title,
        description=release.description,
        status=release.status,
        planned_release_date=release.planned_release_date,
        actual_release_date=release.actual_release_date,
        task_ids=[task.id for task in release.tasks],
        tag_ids=[tag.id for tag in release.tags],
        created_by=release.created_by,
        creator=release.creator,
        tasks=release.tasks,
        tags=release.tags,
        created_at=release.created_at,
        updated_at=release.updated_at
    )


@router.delete("/{release_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_release(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("release:delete"))
):
    """Delete release by ID"""
    # Find release
    release = db.query(Release).filter(Release.id == release_id).first()
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found"
        )
    
    # Clear task associations
    for task in release.tasks:
        task.release_id = None
    
    # Delete release
    db.delete(release)
    db.commit()
    
    return None


# Release follow endpoints


@router.post("/{release_id}/follow")
async def follow_release(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("release:follow"))
):
    """Follow a release"""
    # Check if release exists
    release = db.query(Release).filter(Release.id == release_id).first()
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found"
        )
    
    # Check if already following
    existing_follow = db.query(ReleaseFollow).filter(
        ReleaseFollow.release_id == release_id,
        ReleaseFollow.user_id == current_user.id
    ).first()
    
    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this release"
        )
    
    # Create follow
    follow = ReleaseFollow(
        release_id=release_id,
        user_id=current_user.id
    )
    db.add(follow)
    db.commit()
    
    return {"message": "Successfully followed release"}


@router.delete("/{release_id}/follow")
async def unfollow_release(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Unfollow a release"""
    # Check if release exists
    release = db.query(Release).filter(Release.id == release_id).first()
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found"
        )
    
    # Find and delete follow
    follow = db.query(ReleaseFollow).filter(
        ReleaseFollow.release_id == release_id,
        ReleaseFollow.user_id == current_user.id
    ).first()
    
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not following this release"
        )
    
    db.delete(follow)
    db.commit()
    
    return {"message": "Successfully unfollowed release"}


@router.get("/{release_id}/follow-status")
async def get_follow_status(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get follow status for a release"""
    # Check if release exists
    release = db.query(Release).filter(Release.id == release_id).first()
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found"
        )
    
    # Check if following
    follow = db.query(ReleaseFollow).filter(
        ReleaseFollow.release_id == release_id,
        ReleaseFollow.user_id == current_user.id
    ).first()
    
    return {"is_following": follow is not None}


@router.get("/{release_id}/followers")
async def get_release_followers(
    release_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all followers of a release"""
    # Check if release exists
    release = db.query(Release).filter(Release.id == release_id).first()
    if not release:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Release not found"
        )
    
    # Get all followers
    followers = db.query(ReleaseFollow).options(
        joinedload(ReleaseFollow.user)
    ).filter(
        ReleaseFollow.release_id == release_id
    ).all()
    
    # Return follower list
    return [
        {
            "id": follow.id,
            "user_id": follow.user_id,
            "user_name": follow.user.name if follow.user else None,
            "created_at": follow.created_at
        }
        for follow in followers
    ]
