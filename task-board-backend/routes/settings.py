from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import get_db, SystemSetting, RequirementTag, User
from schemas import (
    SystemSetting as SystemSettingSchema, 
    SystemSettingUpdate,
    RequirementTagCreate, 
    RequirementTag as RequirementTagSchema
)
from auth import get_admin_user, get_current_active_user

router = APIRouter()


async def get_non_viewer_user(current_user: str = Depends(get_current_active_user)) -> str:
    """Get current user who is not a viewer"""
    # 由于已移除role字段，此函数不再需要特殊检查
    # 权限检查将通过权限切片进行
    return current_user


@router.get("/settings", response_model=list[SystemSettingSchema])
async def get_settings(current_user: str = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Get all system settings (admin only)"""
    settings = db.query(SystemSetting).all()
    return settings


@router.get("/settings/{setting_key}", response_model=SystemSettingSchema)
async def get_setting(setting_key: str, current_user: str = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Get a specific system setting by key (admin only)"""
    setting = db.query(SystemSetting).filter(SystemSetting.key == setting_key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    return setting


@router.put("/settings/{setting_key}", response_model=SystemSettingSchema)
async def update_setting(setting_key: str, setting_data: SystemSettingUpdate, current_user: str = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Update a system setting by key (admin only)"""
    setting = db.query(SystemSetting).filter(SystemSetting.key == setting_key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    # Update setting
    setting.value = setting_data.value
    if setting_data.description:
        setting.description = setting_data.description
    
    db.commit()
    db.refresh(setting)
    return setting


@router.post("/settings", response_model=SystemSettingSchema)
async def create_setting(setting_data: dict, current_user: str = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Create a new system setting (admin only)"""
    # Check if setting already exists
    existing_setting = db.query(SystemSetting).filter(SystemSetting.key == setting_data.get("key")).first()
    if existing_setting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setting with this key already exists"
        )
    
    # Create new setting
    new_setting = SystemSetting(
        key=setting_data.get("key"),
        value=setting_data.get("value"),
        description=setting_data.get("description")
    )
    
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    return new_setting


@router.delete("/settings/{setting_key}")
async def delete_setting(setting_key: str, current_user: str = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Delete a system setting by key (admin only)"""
    setting = db.query(SystemSetting).filter(SystemSetting.key == setting_key).first()
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    db.delete(setting)
    db.commit()
    return {"detail": "Setting deleted successfully"}


# RequirementTag endpoints


@router.get("/requirement-tags", response_model=list[RequirementTagSchema])
async def get_requirement_tags(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_active_user)
):
    """Get all requirement tags"""
    tags = db.query(RequirementTag).all()
    return tags


@router.post("/requirement-tags", response_model=RequirementTagSchema)
async def create_requirement_tag(
    tag: RequirementTagCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_non_viewer_user)
):
    """Create a new requirement tag"""
    existing_tag = db.query(RequirementTag).filter(RequirementTag.name == tag.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requirement tag with this name already exists"
        )
    db_tag = RequirementTag(
        name=tag.name,
        color=tag.color
    )
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.put("/requirement-tags/{tag_id}", response_model=RequirementTagSchema)
async def update_requirement_tag(
    tag_id: int,
    tag: RequirementTagCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_non_viewer_user)
):
    """Update a requirement tag"""
    db_tag = db.query(RequirementTag).filter(RequirementTag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement tag not found"
        )
    # Check if name is already used by another tag
    existing_tag = db.query(RequirementTag).filter(
        RequirementTag.name == tag.name,
        RequirementTag.id != tag_id
    ).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requirement tag with this name already exists"
        )
    db_tag.name = tag.name
    db_tag.color = tag.color
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.delete("/requirement-tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_requirement_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_non_viewer_user)
):
    """Delete requirement tag by ID"""
    # Find tag
    tag = db.query(RequirementTag).filter(RequirementTag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requirement tag not found"
        )
    
    # Delete tag
    db.delete(tag)
    db.commit()
    
    return None
