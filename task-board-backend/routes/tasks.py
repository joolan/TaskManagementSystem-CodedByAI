from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import pandas as pd
import io

from db import get_db, User, Task, Status, TaskLog, Tag, TaskFollow, Message, UserMessage, TaskHour
from schemas import (
    TaskCreate, TaskUpdate, TaskStatusUpdate, TaskAssigneeUpdate,
    Task as TaskSchema, TaskWithDetails, Tag as TagSchema, TagCreate,
    TaskHourCreate, TaskHour as TaskHourSchema, TaskHourWithDetails, TaskHoursStats,
    UserBasic
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


@router.get("", response_model=dict)
async def get_tasks(
    status_id: Optional[str] = Query(None, description="Filter by status IDs (comma-separated)"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    follow_status: Optional[str] = Query(None, description="Filter by follow status: all, followed, unfollowed"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search by title or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(1000, ge=1, le=1000, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get tasks with optional filters and pagination"""
    query = db.query(Task)
    
    # Apply filters
    if status_id:
        # Split comma-separated string into list of integers
        status_ids = [int(id.strip()) for id in status_id.split(',')]
        query = query.filter(Task.status_id.in_(status_ids))
    if assignee_id:
        # Filter by primary assignee or any of the multiple assignees
        query = query.filter(
            (Task.assignee_id == assignee_id) |
            (Task.assignees.any(User.id == assignee_id))
        )
    if follow_status:
        if follow_status == "followed":
            # Filter tasks that the current user is following
            query = query.join(TaskFollow, Task.id == TaskFollow.task_id).filter(
                TaskFollow.user_id == current_user.id
            )
        elif follow_status == "unfollowed":
            # Filter tasks that the current user is not following
            followed_task_ids = db.query(TaskFollow.task_id).filter(
                TaskFollow.user_id == current_user.id
            ).subquery()
            query = query.filter(~Task.id.in_(followed_task_ids))
    if priority:
        query = query.filter(Task.priority == priority)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Task.title.ilike(search_term)) |
            (Task.description.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Apply pagination with preloaded relationships
    from sqlalchemy.orm import joinedload
    tasks = query.options(
        joinedload(Task.status),
        joinedload(Task.assignee),
        joinedload(Task.assignees),
        joinedload(Task.creator),
        joinedload(Task.tags),
        joinedload(Task.release)  # 预加载关联的发版记录
    ).offset(offset).limit(page_size).all()
    
    # Convert to schema with details
    task_list = [
        TaskWithDetails(
            id=task.id,
            title=task.title,
            description=task.description,
            status_id=task.status_id,
            status=task.status,
            assignee_id=task.assignee_id,
            assignee=task.assignee,
            assignee_ids=[assignee.id for assignee in task.assignees],
            assignees=task.assignees,
            priority=task.priority,
            due_date=task.due_date,
            actual_start_date=task.actual_start_date,
            actual_completion_date=task.actual_completion_date,
            estimated_hours=task.estimated_hours,
            actual_hours=task.actual_hours,
            tag_ids=[tag.id for tag in task.tags],
            tags=task.tags,
            release_id=task.release_id,
            release=task.release,  # 包含关联的发版记录
            created_by=task.created_by,
            creator=task.creator,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
        for task in tasks
    ]
    
    # Return paginated response
    return {
        "items": task_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.post("", response_model=TaskWithDetails)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("task:create"))
):
    """Create a new task"""
    # Check if status exists
    status = db.query(Status).filter(Status.id == task.status_id).first()
    if not status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status ID"
        )
    
    # Check if assignee exists if provided
    if task.assignee_id:
        assignee = db.query(User).filter(User.id == task.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid assignee ID"
            )
    
    # Create task
    db_task = Task(
        title=task.title,
        description=task.description,
        status_id=task.status_id,
        assignee_id=task.assignee_id,
        priority=task.priority,
        due_date=task.due_date,
        actual_start_date=task.actual_start_date,
        actual_completion_date=task.actual_completion_date,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        created_by=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Create task creation log
    log_title = "任务创建"
    log_content = f"创建了新任务: {task.title}\n"
    log_content += f"描述: {task.description if task.description else '无'}\n"
    log_content += f"状态: {status.name}\n"
    log_content += f"优先级: {task.priority}\n"
    
    if task.due_date:
        log_content += f"预计完成时间: {task.due_date}\n"
    
    if task.assignee_id:
        assignee = db.query(User).filter(User.id == task.assignee_id).first()
        log_content += f"负责人: {assignee.name if assignee else '未分配'}\n"
    
    if task.estimated_hours:
        log_content += f"预估工时: {task.estimated_hours} 小时\n"
    
    # Create task log
    db_log = TaskLog(
        task_id=db_task.id,
        user_id=current_user.id,
        action_type="create",
        title=log_title,
        content=log_content
    )
    db.add(db_log)
    db.commit()
    
    # Add multiple assignees if provided
    if task.assignee_ids:
        assignees = db.query(User).filter(User.id.in_(task.assignee_ids)).all()
        db_task.assignees = assignees
        db.commit()
        db.refresh(db_task)
    
    # Add tags if provided
    if task.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(task.tag_ids)).all()
        db_task.tags = tags
        db.commit()
        db.refresh(db_task)
    
    # Return task with details
    return TaskWithDetails(
        id=db_task.id,
        title=db_task.title,
        description=db_task.description,
        status_id=db_task.status_id,
        status=db_task.status,
        assignee_id=db_task.assignee_id,
        assignee=db_task.assignee,
        assignee_ids=[assignee.id for assignee in db_task.assignees],
        assignees=db_task.assignees,
        priority=db_task.priority,
        due_date=db_task.due_date,
        actual_start_date=db_task.actual_start_date,
        actual_completion_date=db_task.actual_completion_date,
        estimated_hours=db_task.estimated_hours,
        actual_hours=db_task.actual_hours,
        tag_ids=[tag.id for tag in db_task.tags],
        tags=db_task.tags,
        release_id=db_task.release_id,
        created_by=db_task.created_by,
        creator=db_task.creator,
        created_at=db_task.created_at,
        updated_at=db_task.updated_at
    )


@router.get("/export")
async def export_tasks(
    status_id: Optional[str] = Query(None, description="Filter by status IDs (comma-separated)"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee ID"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    search: Optional[str] = Query(None, description="Search by title or description"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("task:export"))
):
    """Export tasks with optional filters to Excel file"""
    query = db.query(Task).options(
        joinedload(Task.status),
        joinedload(Task.assignee),
        joinedload(Task.assignees),
        joinedload(Task.creator),
        joinedload(Task.tags)
    )
    
    # Apply filters
    if status_id:
        # Split comma-separated string into list of integers
        status_ids = [int(id.strip()) for id in status_id.split(',')]
        query = query.filter(Task.status_id.in_(status_ids))
    if assignee_id:
        # Filter by primary assignee or any of the multiple assignees
        query = query.filter(
            (Task.assignee_id == assignee_id) |
            (Task.assignees.any(User.id == assignee_id))
        )
    if priority:
        query = query.filter(Task.priority == priority)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Task.title.ilike(search_term)) |
            (Task.description.ilike(search_term))
        )
    
    # Get all tasks without pagination
    tasks = query.all()
    
    # Prepare data for export
    data = []
    for task in tasks:
        # Collect assignees names
        assignee_names = []
        if task.assignee:
            assignee_names.append(task.assignee.name)
        for assignee in task.assignees:
            if assignee != task.assignee:
                assignee_names.append(assignee.name)
        assignees_str = ", ".join(assignee_names) if assignee_names else "未分配"
        
        # Collect tags names
        tag_names = [tag.name for tag in task.tags]
        tags_str = ", ".join(tag_names) if tag_names else "无"
        
        # Prepare row data
        row = {
            "任务ID": task.id,
            "任务标题": task.title,
            "任务描述": task.description,
            "任务状态": task.status.name if task.status else "",
            "负责人": assignees_str,
            "优先级": task.priority,
            "截止日期": task.due_date.strftime("%Y-%m-%d") if task.due_date else "",
            "实际开始日期": task.actual_start_date.strftime("%Y-%m-%d") if task.actual_start_date else "",
            "实际完成日期": task.actual_completion_date.strftime("%Y-%m-%d") if task.actual_completion_date else "",
            "预估工时": task.estimated_hours,
            "实际工时": task.actual_hours,
            "标签": tags_str,
            "创建人": task.creator.name if task.creator else "",
            "创建时间": task.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "更新时间": task.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='任务列表', index=False)
    output.seek(0)
    
    # Return as streaming response
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=tasks_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )


@router.get("/{task_id}", response_model=TaskWithDetails)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Return task with details
    return TaskWithDetails(
        id=task.id,
        title=task.title,
        description=task.description,
        status_id=task.status_id,
        status=task.status,
        assignee_id=task.assignee_id,
        assignee=task.assignee,
        assignee_ids=[assignee.id for assignee in task.assignees],
        assignees=task.assignees,
        priority=task.priority,
        due_date=task.due_date,
        actual_start_date=task.actual_start_date,
        actual_completion_date=task.actual_completion_date,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        tag_ids=[tag.id for tag in task.tags],
        tags=task.tags,
        release_id=task.release_id,
        created_by=task.created_by,
        creator=task.creator,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put("/{task_id}", response_model=TaskWithDetails)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("task:update"))
):
    """Update task by ID"""
    # Find task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions (only creator, assignee, or admin/pm can update)
    if not (
        current_user.id == task.created_by or
        current_user.id == task.assignee_id or
        current_user.username == "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if status exists if updating
    if task_update.status_id:
        new_status = db.query(Status).filter(Status.id == task_update.status_id).first()
        if not new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status ID"
            )
    
    # Check if assignee exists if updating
    if task_update.assignee_id:
        assignee = db.query(User).filter(User.id == task_update.assignee_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid assignee ID"
            )
    
    # Save old task values for logging
    old_values = {
        'title': task.title,
        'description': task.description,
        'status_id': task.status_id,
        'assignee_id': task.assignee_id,
        'priority': task.priority,
        'due_date': task.due_date,
        'actual_start_date': task.actual_start_date,
        'actual_completion_date': task.actual_completion_date,
        'estimated_hours': task.estimated_hours,
        'actual_hours': task.actual_hours,
        'assignee_ids': [assignee.id for assignee in task.assignees],
        'tag_ids': [tag.id for tag in task.tags]
    }
    
    # Update task
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Handle assignee_ids separately
    assignee_ids = update_data.pop('assignee_ids', None)
    
    # Handle tag_ids separately
    tag_ids = update_data.pop('tag_ids', None)
    
    # Update other fields
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # Update multiple assignees if provided
    if assignee_ids is not None:
        assignees = db.query(User).filter(User.id.in_(assignee_ids)).all()
        task.assignees = assignees
    
    # Update tags if provided
    if tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
        task.tags = tags
    
    db.commit()
    db.refresh(task)
    
    # Create task log if there are changes
    changes = []
    
    # Compare old and new values
    if task.title != old_values['title']:
        changes.append(f"标题: {old_values['title']} → {task.title}")
    
    if task.status_id != old_values['status_id']:
        old_status = db.query(Status).filter(Status.id == old_values['status_id']).first()
        new_status = db.query(Status).filter(Status.id == task.status_id).first()
        changes.append(f"状态: {old_status.name if old_status else old_values['status_id']} → {new_status.name if new_status else task.status_id}")
        
        # Check if we need to send notifications
        # Send notification if status changed to completed or from completed to other status
        old_status_name = old_status.name if old_status else ""
        new_status_name = new_status.name if new_status else ""
        
        if (old_status_name != "已完成" and new_status_name == "已完成") or \
           (old_status_name == "已完成" and new_status_name != "已完成"):
            
            # Get all task followers
            followers = db.query(User).join(TaskFollow).filter(
                TaskFollow.task_id == task_id
            ).all()
            
            # Create message regardless of whether there are followers
            # This ensures the message is created in the database
            message = Message(
                message_type="task_message",
                title="任务消息",
                content=f"任务「{task.title}」的状态已从「{old_status_name}」变更为「{new_status_name}」",
                redirect_path=f"/task/{task_id}",
                created_by=current_user.id
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            
            # Create user messages for all followers
            if followers:
                for follower in followers:
                    user_message = UserMessage(
                        user_id=follower.id,
                        message_id=message.id
                    )
                    db.add(user_message)
                
                db.commit()
    
    if task.assignee_id != old_values['assignee_id']:
        old_assignee = db.query(User).filter(User.id == old_values['assignee_id']).first()
        new_assignee = db.query(User).filter(User.id == task.assignee_id).first()
        changes.append(f"负责人: {old_assignee.name if old_assignee else '未分配'} → {new_assignee.name if new_assignee else '未分配'}")
    
    if task.priority != old_values['priority']:
        priority_map = {'high': '高', 'medium': '中', 'low': '低'}
        changes.append(f"优先级: {priority_map.get(old_values['priority'], old_values['priority'])} → {priority_map.get(task.priority, task.priority)}")
    
    if task.due_date != old_values['due_date']:
        old_date = old_values['due_date'].strftime('%Y-%m-%d') if old_values['due_date'] else '未设置'
        new_date = task.due_date.strftime('%Y-%m-%d') if task.due_date else '未设置'
        changes.append(f"预计完成时间: {old_date} → {new_date}")
    
    if task.actual_start_date != old_values['actual_start_date']:
        old_date = old_values['actual_start_date'].strftime('%Y-%m-%d') if old_values['actual_start_date'] else '未设置'
        new_date = task.actual_start_date.strftime('%Y-%m-%d') if task.actual_start_date else '未设置'
        changes.append(f"实际开始日期: {old_date} → {new_date}")
    
    if task.actual_completion_date != old_values['actual_completion_date']:
        old_date = old_values['actual_completion_date'].strftime('%Y-%m-%d') if old_values['actual_completion_date'] else '未设置'
        new_date = task.actual_completion_date.strftime('%Y-%m-%d') if task.actual_completion_date else '未设置'
        changes.append(f"实际完成日期: {old_date} → {new_date}")
    
    if task.estimated_hours != old_values['estimated_hours']:
        old_hours = old_values['estimated_hours'] or '未设置'
        new_hours = task.estimated_hours or '未设置'
        changes.append(f"预估工时: {old_hours} 小时 → {new_hours} 小时")
    
    if task.actual_hours != old_values['actual_hours']:
        old_hours = old_values['actual_hours'] or '未设置'
        new_hours = task.actual_hours or '未设置'
        changes.append(f"实际工时: {old_hours} 小时 → {new_hours} 小时")
    
    # Compare assignees
    new_assignee_ids = [assignee.id for assignee in task.assignees]
    if set(new_assignee_ids) != set(old_values['assignee_ids']):
        old_assignees = db.query(User).filter(User.id.in_(old_values['assignee_ids'])).all()
        new_assignees = db.query(User).filter(User.id.in_(new_assignee_ids)).all()
        old_names = ', '.join([a.name for a in old_assignees]) or '未分配'
        new_names = ', '.join([a.name for a in new_assignees]) or '未分配'
        changes.append(f"多个负责人: {old_names} → {new_names}")
    
    # Compare tags
    new_tag_ids = [tag.id for tag in task.tags]
    if set(new_tag_ids) != set(old_values['tag_ids']):
        old_tags = db.query(Tag).filter(Tag.id.in_(old_values['tag_ids'])).all()
        new_tags = db.query(Tag).filter(Tag.id.in_(new_tag_ids)).all()
        old_names = ', '.join([t.name for t in old_tags]) or '无'
        new_names = ', '.join([t.name for t in new_tags]) or '无'
        changes.append(f"标签: {old_names} → {new_names}")
    
    # Add description change summary to changes if description changed
    description_changed = task.description != old_values['description']
    description_details = None
    if description_changed:
        description_details = {
            'old': old_values['description'] or '',
            'new': task.description or ''
        }
    
    # Create log for all changes if any
    if changes or description_changed:
        # Create structured content with description and other changes
        import json
        log_content = {
            'description': description_details,
            'changes': changes
        }
        content = json.dumps(log_content, ensure_ascii=False)
        log_title = "任务更新"
        
        # Create task log
        db_log = TaskLog(
            task_id=task.id,
            user_id=current_user.id,
            action_type="update",
            title=log_title,
            content=content
        )
        db.add(db_log)
        db.commit()
    
    # Return updated task with details
    return TaskWithDetails(
        id=task.id,
        title=task.title,
        description=task.description,
        status_id=task.status_id,
        status=task.status,
        assignee_id=task.assignee_id,
        assignee=task.assignee,
        assignee_ids=[assignee.id for assignee in task.assignees],
        assignees=task.assignees,
        priority=task.priority,
        due_date=task.due_date,
        actual_start_date=task.actual_start_date,
        actual_completion_date=task.actual_completion_date,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        tag_ids=[tag.id for tag in task.tags],
        tags=task.tags,
        release_id=task.release_id,
        created_by=task.created_by,
        creator=task.creator,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("task:delete"))
):
    """Delete task by ID"""
    # Find task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Delete task
    db.delete(task)
    db.commit()
    
    return None


# Tag management endpoints


@router.get("/tags/all", response_model=List[TagSchema])
async def get_all_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_non_viewer_user)
):
    """Get all tags"""
    tags = db.query(Tag).all()
    return tags


@router.post("/tags", response_model=TagSchema)
async def create_tag(
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("tag:create"))
):
    """Create a new tag"""
    existing_tag = db.query(Tag).filter(Tag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists"
        )
    db_tag = Tag(
        name=tag.name,
        color=tag.color
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.put("/tags/{tag_id}", response_model=TagSchema)
async def update_tag(
    tag_id: int,
    tag: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("tag:update"))
):
    """Update a tag"""
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    # Check if name is already used by another tag
    existing_tag = db.query(Tag).filter(
        Tag.name == tag.name,
        Tag.id != tag_id
    ).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists"
        )
    db_tag.name = tag.name
    db_tag.color = tag.color
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("tag:delete"))
):
    """Delete tag by ID"""
    # Find tag
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Delete tag
    db.delete(tag)
    db.commit()
    
    return None


@router.put("/{task_id}/status", response_model=TaskWithDetails)
async def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("task:update_status"))
):
    """Update task status"""
    # Find task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check permissions (only creator, assignee, or admin/pm can update)
    if not (
        current_user.id == task.created_by or
        current_user.id == task.assignee_id or
        current_user.username == "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if status exists
    new_status = db.query(Status).filter(Status.id == status_update.status_id).first()
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status ID"
        )
    
    # Get old status
    # First get the old status from the database to ensure it's loaded
    old_status = db.query(Status).filter(Status.id == task.status_id).first()
    old_status_name = old_status.name if old_status else ""
    
    # Update status
    task.status_id = status_update.status_id
    db.commit()
    db.refresh(task)
    
    # Check if we need to send notifications
    # Send notification if status changed to completed or from completed to other status
    if (old_status_name != "已完成" and new_status.name == "已完成") or \
       (old_status_name == "已完成" and new_status.name != "已完成"):
        
        # Get all task followers
        followers = db.query(User).join(TaskFollow).filter(
            TaskFollow.task_id == task_id
        ).all()
        
        # Create message regardless of whether there are followers
        # This ensures the message is created in the database
        message = Message(
            message_type="task_message",
            title="任务消息",
            content=f"任务「{task.title}」的状态已从「{old_status_name}」变更为「{new_status.name}」",
            redirect_path=f"/task/{task_id}",
            created_by=current_user.id
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Create user messages for all followers
        if followers:
            for follower in followers:
                user_message = UserMessage(
                    user_id=follower.id,
                    message_id=message.id
                )
                db.add(user_message)
            
            db.commit()
    
    # Return updated task with details
    return TaskWithDetails(
        id=task.id,
        title=task.title,
        description=task.description,
        status_id=task.status_id,
        status=task.status,
        assignee_id=task.assignee_id,
        assignee=task.assignee,
        assignee_ids=[assignee.id for assignee in task.assignees],
        assignees=task.assignees,
        priority=task.priority,
        due_date=task.due_date,
        actual_start_date=task.actual_start_date,
        actual_completion_date=task.actual_completion_date,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        tag_ids=[tag.id for tag in task.tags],
        tags=task.tags,
        release_id=task.release_id,
        created_by=task.created_by,
        creator=task.creator,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.put("/{task_id}/assignee", response_model=TaskWithDetails)
async def update_task_assignee(
    task_id: int,
    assignee_update: TaskAssigneeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("task:assign"))
):
    """Update task assignee"""
    # Find task
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if assignee exists
    assignee = db.query(User).filter(User.id == assignee_update.assignee_id).first()
    if not assignee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assignee ID"
        )
    
    # Update assignee
    task.assignee_id = assignee_update.assignee_id
    db.commit()
    db.refresh(task)
    
    # Return updated task with details
    return TaskWithDetails(
        id=task.id,
        title=task.title,
        description=task.description,
        status_id=task.status_id,
        status=task.status,
        assignee_id=task.assignee_id,
        assignee=task.assignee,
        assignee_ids=[assignee.id for assignee in task.assignees],
        assignees=task.assignees,
        priority=task.priority,
        due_date=task.due_date,
        actual_start_date=task.actual_start_date,
        actual_completion_date=task.actual_completion_date,
        estimated_hours=task.estimated_hours,
        actual_hours=task.actual_hours,
        tag_ids=[tag.id for tag in task.tags],
        tags=task.tags,
        release_id=task.release_id,
        created_by=task.created_by,
        creator=task.creator,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


# Task follow endpoints

@router.post("/{task_id}/follow")
async def follow_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("task:follow"))
):
    """Follow a task"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if already following
    existing_follow = db.query(TaskFollow).filter(
        TaskFollow.task_id == task_id,
        TaskFollow.user_id == current_user.id
    ).first()
    
    if existing_follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this task"
        )
    
    # Create follow
    follow = TaskFollow(
        task_id=task_id,
        user_id=current_user.id
    )
    db.add(follow)
    db.commit()
    
    return {"message": "Successfully followed task"}


@router.delete("/{task_id}/follow")
async def unfollow_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Unfollow a task"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if following
    follow = db.query(TaskFollow).filter(
        TaskFollow.task_id == task_id,
        TaskFollow.user_id == current_user.id
    ).first()
    
    if not follow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not following this task"
        )
    
    # Delete follow
    db.delete(follow)
    db.commit()
    
    return {"message": "Successfully unfollowed task"}


@router.get("/{task_id}/follow-status")
async def get_task_follow_status(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get task follow status for current user"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if following
    follow = db.query(TaskFollow).filter(
        TaskFollow.task_id == task_id,
        TaskFollow.user_id == current_user.id
    ).first()
    
    return {"is_following": follow is not None}


@router.get("/{task_id}/followers")
async def get_task_followers(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get task followers"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get followers
    followers = db.query(User).join(TaskFollow).filter(
        TaskFollow.task_id == task_id
    ).all()
    
    # Return followers with user info
    follower_list = [
        {
            "id": user.id,
            "username": user.username,
            "name": user.name
        }
        for user in followers
    ]
    
    return {"followers": follower_list}


# Task hour endpoints

@router.post("/{task_id}/hours", response_model=List[TaskHourWithDetails])
async def add_task_hours(
    task_id: int,
    hour_data: TaskHourCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("task:add_hours"))
):
    """Add work hours to a task (can add for multiple users at once)"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    users = db.query(User).filter(User.id.in_(hour_data.user_ids)).all()
    if len(users) != len(hour_data.user_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some users not found"
        )
    
    task_hours = []
    for user_id in hour_data.user_ids:
        task_hour = TaskHour(
            task_id=task_id,
            user_id=user_id,
            hours=hour_data.hours,
            remark=hour_data.remark,
            created_by=current_user.id
        )
        db.add(task_hour)
        task_hours.append(task_hour)
    
    db.commit()
    
    # Create task log for hour reporting
    log_title = "工时填报"
    user_names = ", ".join([user.name for user in users])
    log_content = f"填报了工时: {hour_data.hours} 小时\n"
    log_content += f"涉及人员: {user_names}\n"
    if hour_data.remark:
        log_content += f"备注: {hour_data.remark}\n"
    
    db_log = TaskLog(
        task_id=task_id,
        user_id=current_user.id,
        action_type="update",
        title=log_title,
        content=log_content
    )
    db.add(db_log)
    db.commit()
    
    result = []
    for th in task_hours:
        db.refresh(th)
        user = db.query(User).filter(User.id == th.user_id).first()
        creator = db.query(User).filter(User.id == th.created_by).first()
        result.append(TaskHourWithDetails(
            id=th.id,
            task_id=th.task_id,
            user_id=th.user_id,
            hours=th.hours,
            remark=th.remark,
            created_by=th.created_by,
            created_at=th.created_at,
            user=UserBasic(id=user.id, username=user.username, name=user.name),
            creator=UserBasic(id=creator.id, username=creator.username, name=creator.name)
        ))
    
    return result


@router.get("/{task_id}/hours", response_model=TaskHoursStats)
async def get_task_hours(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all work hours for a task with total hours"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task_hours = db.query(TaskHour).filter(TaskHour.task_id == task_id).order_by(TaskHour.created_at.desc()).all()
    
    total_hours = sum(th.hours for th in task_hours) if task_hours else 0.0
    
    hours_list = []
    for th in task_hours:
        user = db.query(User).filter(User.id == th.user_id).first()
        creator = db.query(User).filter(User.id == th.created_by).first()
        hours_list.append(TaskHourWithDetails(
            id=th.id,
            task_id=th.task_id,
            user_id=th.user_id,
            hours=th.hours,
            remark=th.remark,
            created_by=th.created_by,
            created_at=th.created_at,
            user=UserBasic(id=user.id, username=user.username, name=user.name),
            creator=UserBasic(id=creator.id, username=creator.username, name=creator.name)
        ))
    
    return TaskHoursStats(
        total_hours=total_hours,
        hours_list=hours_list
    )
