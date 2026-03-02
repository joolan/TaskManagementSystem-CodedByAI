from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db, Permission
from schemas import PermissionCreate, PermissionUpdate, PermissionResponse
from typing import List
from auth import get_current_user, check_permission

router = APIRouter(tags=["permissions"])


def require_permission(permission_code: str):
    """Create a dependency that requires a specific permission"""
    async def dependency(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        return await check_permission(permission_code, current_user, db)
    return dependency


@router.get("", response_model=List[PermissionResponse])
async def get_permissions(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("permission:list"))
):
    """获取权限列表"""
    permissions = db.query(Permission).all()
    return permissions


@router.post("", response_model=PermissionResponse)
async def create_permission(
    permission: PermissionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("permission:create"))
):
    """创建权限"""
    # 创建权限
    db_permission = Permission(**permission.dict())
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission


@router.put("/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: int,
    permission: PermissionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("permission:update"))
):
    """更新权限"""
    # 查找权限
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not db_permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    
    # 更新权限
    for key, value in permission.dict(exclude_unset=True).items():
        setattr(db_permission, key, value)
    
    db.commit()
    db.refresh(db_permission)
    return db_permission


@router.delete("/{permission_id}")
async def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """删除权限"""
    # 检查权限
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="权限不足")
    
    # 查找权限
    db_permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not db_permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    
    # 删除权限
    db.delete(db_permission)
    db.commit()
    
    return {"message": "权限删除成功"}


@router.get("/tree")
async def get_permission_tree(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取权限树结构"""
    # 获取所有权限
    all_permissions = db.query(Permission).all()
    
    # 构建权限树（按模块分组）
    permission_dict = {}
    for perm in all_permissions:
        # 按code的第一部分分组（例如 "user:read" -> "user"）
        module = perm.code.split(':')[0] if ':' in perm.code else 'other'
        
        if module not in permission_dict:
            permission_dict[module] = {
                "id": f"module-{module}",
                "name": f"{module}模块",
                "code": module,
                "description": f"{module}相关权限",
                "children": []
            }
        
        permission_dict[module]["children"].append({
            "id": perm.id,
            "name": perm.name,
            "code": perm.code,
            "description": perm.description
        })
    
    return list(permission_dict.values())
