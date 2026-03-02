from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from db import get_db, User, Comment, Task
from schemas import CommentCreate, Comment as CommentSchema, CommentWithUser, Attachment
from auth import get_current_active_user, get_admin_user

router = APIRouter()


@router.get("/tasks/{task_id}/comments", response_model=List[CommentWithUser])
async def get_task_comments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get comments for a task"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get comments with attachments preloaded, ordered by pinned_at (descending) then created_at (descending)
    comments = db.query(Comment).options(
        joinedload(Comment.user),
        joinedload(Comment.attachments)
    ).filter(Comment.task_id == task_id).order_by(
        Comment.pinned_at.desc().nulls_last(),
        Comment.created_at.desc()
    ).all()
    
    # Convert to schema with user details
    return [
        CommentWithUser(
            id=comment.id,
            task_id=comment.task_id,
            user_id=None if comment.is_anonymous else comment.user_id,
            content=comment.content,
            created_at=comment.created_at,
            user=comment.user if not comment.is_anonymous else None,
            attachments=[
                Attachment(
                    id=attachment.id,
                    task_id=attachment.task_id,
                    user_id=None if comment.is_anonymous else attachment.user_id,
                    filename=attachment.filename,
                    file_path=attachment.file_path,
                    created_at=attachment.created_at
                )
                for attachment in comment.attachments
            ],
            is_anonymous=bool(comment.is_anonymous),
            pinned_at=comment.pinned_at
        )
        for comment in comments
    ]


@router.post("/tasks/{task_id}/comments", response_model=CommentWithUser)
async def add_task_comment(
    task_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a comment to a task"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user is viewer role (viewers cannot post comments)
    # 由于已移除role字段，此检查不再需要
    # 权限检查将通过权限切片进行
    
    # Create comment
    db_comment = Comment(
        task_id=task_id,
        user_id=current_user.id,
        content=comment.content,
        is_anonymous=1 if comment.is_anonymous else 0
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Associate attachments with comment
    if comment.attachment_ids:
        from db import Attachment
        attachments = db.query(Attachment).filter(Attachment.id.in_(comment.attachment_ids)).all()
        for attachment in attachments:
            attachment.comment_id = db_comment.id
        db.commit()
    
    # Send messages to task assignees
    # Get all assignees (from both assignee_id and task_assignees table)
    assignee_ids = set()
    
    # Add main assignee
    if task.assignee_id:
        assignee_ids.add(task.assignee_id)
    
    # Add multiple assignees from association table
    if task.assignees:
        for assignee in task.assignees:
            assignee_ids.add(assignee.id)
    
    # Remove current user from recipients (don't send message to self)
    if current_user.id in assignee_ids:
        assignee_ids.remove(current_user.id)
    
    # Send message if there are recipients
    if assignee_ids:
        from routes.messages import send_message_to_users
        
        # Truncate comment content to 100 characters
        truncated_content = comment.content[:100] + "..." if len(comment.content) > 100 else comment.content
        
        message_data = {
            'message_type': 'task_message',
            'title': f"{task.title} 有新评论了",
            'content': f"评论内容：{truncated_content}",
            'redirect_path': f"/task/{task_id}"
        }
        
        send_message_to_users(
            db=db,
            message_data=message_data,
            user_ids=list(assignee_ids),
            created_by=current_user.id if not db_comment.is_anonymous else None
        )
    
    # Return comment with user details
    # Get the comment again with attachments loaded
    updated_comment = db.query(Comment).options(
        joinedload(Comment.user),
        joinedload(Comment.attachments)
    ).filter(Comment.id == db_comment.id).first()
    
    return CommentWithUser(
        id=updated_comment.id,
        task_id=updated_comment.task_id,
        user_id=None if updated_comment.is_anonymous else updated_comment.user_id,
        content=updated_comment.content,
        created_at=updated_comment.created_at,
        user=updated_comment.user if not updated_comment.is_anonymous else None,
        attachments=[
            Attachment(
                id=attachment.id,
                task_id=attachment.task_id,
                user_id=None if updated_comment.is_anonymous else attachment.user_id,
                filename=attachment.filename,
                file_path=attachment.file_path,
                created_at=attachment.created_at
            )
            for attachment in updated_comment.attachments
        ],
        is_anonymous=bool(updated_comment.is_anonymous),
        pinned_at=updated_comment.pinned_at
    )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a comment"""
    # Find comment
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check permissions (only comment creator or admin can delete)
    if not (
        current_user.id == comment.user_id or
        current_user.username == "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete comment
    db.delete(comment)
    db.commit()
    
    return None


@router.put("/comments/{comment_id}/pin", response_model=CommentWithUser)
async def pin_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Pin a comment (admin only)"""
    # Find comment
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Toggle pin status
    if comment.pinned_at:
        comment.pinned_at = None
    else:
        comment.pinned_at = datetime.utcnow()
    
    db.commit()
    db.refresh(comment)
    
    # Get comment again with attachments loaded
    updated_comment = db.query(Comment).options(
        joinedload(Comment.user),
        joinedload(Comment.attachments)
    ).filter(Comment.id == comment.id).first()
    
    return CommentWithUser(
        id=updated_comment.id,
        task_id=updated_comment.task_id,
        user_id=None if updated_comment.is_anonymous else updated_comment.user_id,
        content=updated_comment.content,
        created_at=updated_comment.created_at,
        user=updated_comment.user if not updated_comment.is_anonymous else None,
        attachments=[
            Attachment(
                id=attachment.id,
                task_id=attachment.task_id,
                user_id=None if updated_comment.is_anonymous else attachment.user_id,
                filename=attachment.filename,
                file_path=attachment.file_path,
                created_at=attachment.created_at
            )
            for attachment in updated_comment.attachments
        ],
        is_anonymous=bool(updated_comment.is_anonymous),
        pinned_at=updated_comment.pinned_at
    )
