from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime
import pandas as pd
import io

from db import get_db, User, Task, Status, Requirement, RequirementTag, Tag, TaskLog
from schemas import (
    RequirementCreate, RequirementUpdate, Requirement as RequirementSchema, 
    RequirementWithDetails, TaskCreate, RequirementTag as RequirementTagSchema
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
async def get_requirements(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    created_by: Optional[int] = Query(None, description="Filter by creator ID"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=1000, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get requirements with optional filters and pagination"""
    query = db.query(Requirement).options(
        joinedload(Requirement.creator),
        joinedload(Requirement.tag),
        joinedload(Requirement.task)
    )
    
    # Apply filters
    if status:
        # Split comma-separated string into list of statuses
        statuses = [s.strip() for s in status.split(',')]
        query = query.filter(Requirement.status.in_(statuses))
    if priority:
        query = query.filter(Requirement.priority == priority)
    if tag_id:
        query = query.filter(Requirement.tag_id == tag_id)
    if created_by:
        query = query.filter(Requirement.created_by == created_by)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Requirement.name.ilike(search_term)) |
            (Requirement.description.ilike(search_term)) |
            (Requirement.source.ilike(search_term))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    requirements = query.offset(offset).limit(page_size).all()
    
    # Convert to schema with details
    requirement_list = [
        RequirementWithDetails(
            id=req.id,
            created_by=req.created_by,
            created_at=req.created_at,
            updated_at=req.updated_at,
            source=req.source,
            name=req.name,
            tag_id=req.tag_id,
            description=req.description,
            status=req.status,
            priority=req.priority,
            planned_completion_date=req.planned_completion_date,
            actual_completion_date=req.actual_completion_date,
            task_id=req.task_id,
            creator=req.creator,
            tag=req.tag,
            task=req.task
        )
        for req in requirements
    ]
    
    # Return paginated response
    return {
        "items": requirement_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.post("", response_model=RequirementWithDetails)
async def create_requirement(
    requirement: RequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("requirement:create"))
):
    """Create a new requirement"""
    # Create requirement
    db_requirement = Requirement(
        source=requirement.source,
        name=requirement.name,
        tag_id=requirement.tag_id,
        description=requirement.description,
        status=requirement.status,
        priority=requirement.priority,
        planned_completion_date=requirement.planned_completion_date,
        actual_completion_date=requirement.actual_completion_date,
        created_by=current_user.id
    )
    db.add(db_requirement)
    db.commit()
    db.refresh(db_requirement)
    
    # Return requirement with details
    return RequirementWithDetails(
        id=db_requirement.id,
        created_by=db_requirement.created_by,
        created_at=db_requirement.created_at,
        updated_at=db_requirement.updated_at,
        source=db_requirement.source,
        name=db_requirement.name,
        tag_id=db_requirement.tag_id,
        description=db_requirement.description,
        status=db_requirement.status,
        priority=db_requirement.priority,
        planned_completion_date=db_requirement.planned_completion_date,
        actual_completion_date=db_requirement.actual_completion_date,
        task_id=db_requirement.task_id,
        creator=db_requirement.creator,
        tag=db_requirement.tag,
        task=db_requirement.task
    )


@router.get("/export")
async def export_requirements(
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    created_by: Optional[int] = Query(None, description="Filter by creator ID"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("requirement:export"))
):
    """Export requirements with optional filters to Excel file"""
    query = db.query(Requirement).options(
        joinedload(Requirement.creator),
        joinedload(Requirement.tag),
        joinedload(Requirement.task)
    )
    
    # Apply filters
    if status:
        # Split comma-separated string into list of statuses
        statuses = [s.strip() for s in status.split(',')]
        query = query.filter(Requirement.status.in_(statuses))
    if priority:
        query = query.filter(Requirement.priority == priority)
    if tag_id:
        query = query.filter(Requirement.tag_id == tag_id)
    if created_by:
        query = query.filter(Requirement.created_by == created_by)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Requirement.name.ilike(search_term)) |
            (Requirement.description.ilike(search_term)) |
            (Requirement.source.ilike(search_term))
        )
    
    # Get all requirements without pagination
    requirements = query.all()
    
    # Prepare data for export
    data = []
    for req in requirements:
        # Get tag name if exists
        tag_name = req.tag.name if req.tag else "无"
        
        # Get task information if exists
        task_info = f"{req.task.id} - {req.task.title}" if req.task else "无"
        
        # Prepare row data
        row = {
            "需求ID": req.id,
            "需求来源": req.source,
            "需求名称": req.name,
            "需求标签": tag_name,
            "需求描述": req.description,
            "需求状态": req.status,
            "需求优先级": req.priority,
            "计划完成日期": req.planned_completion_date.strftime("%Y-%m-%d") if req.planned_completion_date else "",
            "实际完成日期": req.actual_completion_date.strftime("%Y-%m-%d") if req.actual_completion_date else "",
            "转任务ID": req.task_id,
            "关联任务": task_info,
            "创建人": req.creator.name if req.creator else "",
            "创建时间": req.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "更新时间": req.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='需求列表', index=False)
    output.seek(0)
    
    # Return as streaming response
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=requirements_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )


@router.get("/{requirement_id}", response_model=RequirementWithDetails)
async def get_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get requirement by ID"""
    requirement = db.query(Requirement).options(
        joinedload(Requirement.creator),
        joinedload(Requirement.tag),
        joinedload(Requirement.task)
    ).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    # Return requirement with details
    return RequirementWithDetails(
        id=requirement.id,
        created_by=requirement.created_by,
        created_at=requirement.created_at,
        updated_at=requirement.updated_at,
        source=requirement.source,
        name=requirement.name,
        tag_id=requirement.tag_id,
        description=requirement.description,
        status=requirement.status,
        priority=requirement.priority,
        planned_completion_date=requirement.planned_completion_date,
        actual_completion_date=requirement.actual_completion_date,
        task_id=requirement.task_id,
        creator=requirement.creator,
        tag=requirement.tag,
        task=requirement.task
    )


@router.put("/{requirement_id}", response_model=RequirementWithDetails)
async def update_requirement(
    requirement_id: int,
    requirement_update: RequirementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("requirement:update"))
):
    """Update requirement by ID"""
    # Find requirement
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    # Check if requirement is already in '已转任务' status
    if requirement.status == "已转任务":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update requirement that has been converted to task"
        )
    
    # Check if trying to set status to '已转任务'
    if requirement_update.status == "已转任务":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot directly set status to '已转任务', use the 'convert to task' function instead"
        )
    
    # Update requirement
    update_data = requirement_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(requirement, field, value)
    
    db.commit()
    db.refresh(requirement)
    
    # Return updated requirement with details
    return RequirementWithDetails(
        id=requirement.id,
        created_by=requirement.created_by,
        created_at=requirement.created_at,
        updated_at=requirement.updated_at,
        source=requirement.source,
        name=requirement.name,
        tag_id=requirement.tag_id,
        description=requirement.description,
        status=requirement.status,
        priority=requirement.priority,
        planned_completion_date=requirement.planned_completion_date,
        actual_completion_date=requirement.actual_completion_date,
        task_id=requirement.task_id,
        creator=requirement.creator,
        tag=requirement.tag,
        task=requirement.task
    )


@router.delete("/{requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_requirement(
    requirement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("requirement:delete"))
):
    """Delete requirement by ID"""
    # Find requirement
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    # Delete requirement
    db.delete(requirement)
    db.commit()
    
    return None


@router.post("/{requirement_id}/convert-to-task", response_model=dict)
async def convert_requirement_to_task(
    requirement_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("requirement:convert"))
):
    """Convert requirement to task"""
    # Find requirement
    requirement = db.query(Requirement).filter(Requirement.id == requirement_id).first()
    if not requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement not found"
        )
    
    # Check if requirement is already in '已转任务' status
    if requirement.status == "已转任务":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requirement has already been converted to task"
        )
    
    # Create task
    db_task = Task(
        title=task_data.title or requirement.name,
        description=task_data.description or requirement.description,
        status_id=task_data.status_id,
        assignee_id=task_data.assignee_id,
        priority=task_data.priority or requirement.priority,
        due_date=task_data.due_date or requirement.planned_completion_date,
        actual_start_date=task_data.actual_start_date,
        actual_completion_date=task_data.actual_completion_date or requirement.actual_completion_date,
        estimated_hours=task_data.estimated_hours,
        actual_hours=task_data.actual_hours,
        created_by=current_user.id
    )
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Add multiple assignees if provided
    if task_data.assignee_ids:
        assignees = db.query(User).filter(User.id.in_(task_data.assignee_ids)).all()
        db_task.assignees = assignees
        db.commit()
        db.refresh(db_task)
    
    # Add task tags if provided
    if task_data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(task_data.tag_ids)).all()
        db_task.tags = tags
        db.commit()
        db.refresh(db_task)
    
    # Create task log to record that this task was created from a requirement
    task_log = TaskLog(
        task_id=db_task.id,
        user_id=current_user.id,
        action_type="create",
        title="从需求转任务创建",
        content=f"任务从需求「{requirement.name}」（ID: {requirement.id}）转任务创建"
    )
    db.add(task_log)
    db.commit()
    
    # Update requirement status to '已转任务' and set task_id
    requirement.status = "已转任务"
    requirement.task_id = db_task.id
    db.commit()
    
    return {
        "message": "Requirement successfully converted to task",
        "task_id": db_task.id,
        "requirement_id": requirement_id
    }


@router.get("/tags/available", response_model=list[RequirementTagSchema])
async def get_available_requirement_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all available requirement tags"""
    tags = db.query(RequirementTag).all()
    return tags
