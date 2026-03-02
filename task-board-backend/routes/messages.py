from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

from db import get_db, User, Message, UserMessage, Task
from schemas import MessageCreate, MessageWithStatus
from auth import get_current_active_user

router = APIRouter()


def send_message_to_users(db: Session, message_data: dict, user_ids: List[int], created_by: Optional[int] = None):
    """Send message to multiple users"""
    # Create message
    db_message = Message(
        message_type=message_data['message_type'],
        title=message_data['title'],
        content=message_data['content'],
        redirect_path=message_data.get('redirect_path'),
        created_by=created_by,
        created_at=datetime.utcnow()
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    # Create user messages
    user_messages = []
    for user_id in user_ids:
        user_message = UserMessage(
            user_id=user_id,
            message_id=db_message.id,
            is_read=0,
            read_at=None
        )
        user_messages.append(user_message)
    
    db.add_all(user_messages)
    db.commit()
    
    return db_message


@router.get("/messages", response_model=List[MessageWithStatus])
async def get_user_messages(
    is_read: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user messages with optional read status filter"""
    query = db.query(UserMessage).options(
        joinedload(UserMessage.message)
    ).filter(UserMessage.user_id == current_user.id)
    
    if is_read is not None:
        query = query.filter(UserMessage.is_read == (1 if is_read else 0))
    
    user_messages = query.order_by(UserMessage.id.desc()).all()
    
    # Convert to schema
    return [
        MessageWithStatus(
            id=um.message.id,
            message_type=um.message.message_type,
            title=um.message.title,
            content=um.message.content,
            redirect_path=um.message.redirect_path,
            created_by=um.message.created_by,
            created_at=um.message.created_at,
            is_read=bool(um.is_read),
            read_at=um.read_at
        )
        for um in user_messages
    ]


@router.get("/messages/unread-count", response_model=dict)
async def get_unread_message_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get count of unread messages for current user"""
    count = db.query(UserMessage).filter(
        UserMessage.user_id == current_user.id,
        UserMessage.is_read == 0
    ).count()
    
    return {"unread_count": count}


@router.put("/messages/{message_id}/read", response_model=MessageWithStatus)
async def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Mark message as read"""
    user_message = db.query(UserMessage).filter(
        UserMessage.user_id == current_user.id,
        UserMessage.message_id == message_id
    ).first()
    
    if not user_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    user_message.is_read = 1
    user_message.read_at = datetime.utcnow()
    db.commit()
    db.refresh(user_message)
    
    # Return updated message
    return MessageWithStatus(
        id=user_message.message.id,
        message_type=user_message.message.message_type,
        title=user_message.message.title,
        content=user_message.message.content,
        redirect_path=user_message.message.redirect_path,
        created_by=user_message.message.created_by,
        created_at=user_message.message.created_at,
        is_read=bool(user_message.is_read),
        read_at=user_message.read_at
    )


@router.post("/messages", response_model=None)
async def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create and send message to multiple users"""
    message_data = {
        'message_type': message.message_type,
        'title': message.title,
        'content': message.content,
        'redirect_path': message.redirect_path
    }
    
    db_message = send_message_to_users(
        db=db,
        message_data=message_data,
        user_ids=message.user_ids,
        created_by=current_user.id
    )
    
    return db_message
