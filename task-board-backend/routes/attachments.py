from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
import uuid

from db import get_db, User, Attachment, Task
from schemas import Attachment as AttachmentSchema, AttachmentWithUser
from auth import get_current_active_user

router = APIRouter()

# Create upload directory if it doesn't exist
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Get file extension
def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


@router.get("/tasks/{task_id}/attachments", response_model=List[AttachmentWithUser])
async def get_task_attachments(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get attachments for a task"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Get attachments
    attachments = db.query(Attachment).filter(Attachment.task_id == task_id).all()
    
    # Convert to schema with user details
    return [
        AttachmentWithUser(
            id=attachment.id,
            task_id=attachment.task_id,
            user_id=attachment.user_id,
            user=attachment.user,
            filename=attachment.filename,
            file_path=attachment.file_path,
            created_at=attachment.created_at
        )
        for attachment in attachments
    ]


@router.post("/tasks/{task_id}/attachments", response_model=AttachmentWithUser)
async def upload_task_attachment(
    task_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload an attachment to a task"""
    # Check if task exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Save file with unique name
    original_filename = file.filename
    file_extension = get_file_extension(original_filename)
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create attachment record with original filename
    db_attachment = Attachment(
        task_id=task_id,
        user_id=current_user.id,
        filename=original_filename,  # Store original filename for display
        file_path=file_path
    )
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    
    # Return attachment with user details
    return AttachmentWithUser(
        id=db_attachment.id,
        task_id=db_attachment.task_id,
        user_id=db_attachment.user_id,
        user=db_attachment.user,
        filename=db_attachment.filename,
        file_path=db_attachment.file_path,
        created_at=db_attachment.created_at
    )


@router.delete("/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete an attachment"""
    # Find attachment
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # Check permissions (only attachment uploader or admin can delete)
    if not (
        current_user.id == attachment.user_id or
        current_user.username == "admin"
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Delete file
    if os.path.exists(attachment.file_path):
        try:
            os.remove(attachment.file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")
    
    # Delete attachment record
    db.delete(attachment)
    db.commit()
    
    return None


@router.get("/attachments/{attachment_id}/download")
async def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Download an attachment"""
    # Find attachment
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found"
        )
    
    # Check if file exists
    if not os.path.exists(attachment.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Return file as response
    from fastapi.responses import FileResponse
    return FileResponse(
        path=attachment.file_path,
        filename=attachment.filename,
        media_type="application/octet-stream"
    )
