from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from db import get_db, User, Task, TaskLog
from schemas import TaskLog as TaskLogSchema, TaskLogCreate, TaskLogWithUser
from auth import get_current_active_user

router = APIRouter()


@router.get("/tasks/{task_id}/logs", response_model=List[TaskLogWithUser])
async def get_task_logs(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get logs for a task"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get logs (ordered by created_at descending)
    logs = db.query(TaskLog).filter(TaskLog.task_id == task_id).order_by(TaskLog.created_at.desc()).all()
    
    # Convert to schema with user details
    return [
        TaskLogWithUser(
            id=log.id,
            task_id=log.task_id,
            user_id=log.user_id,
            user=log.user,
            action_type=log.action_type,
            title=log.title,
            content=log.content,
            created_at=log.created_at
        )
        for log in logs
    ]


@router.post("/tasks/{task_id}/logs", response_model=TaskLogWithUser)
async def create_task_log(
    task_id: int,
    log_data: TaskLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a log for a task"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Create log
    db_log = TaskLog(
        task_id=task_id,
        user_id=current_user.id,
        action_type=log_data.action_type,
        title=log_data.title,
        content=log_data.content
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    
    # Return log with user details
    return TaskLogWithUser(
        id=db_log.id,
        task_id=db_log.task_id,
        user_id=db_log.user_id,
        user=db_log.user,
        action_type=db_log.action_type,
        title=db_log.title,
        content=db_log.content,
        created_at=db_log.created_at
    )
