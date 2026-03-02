from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db, Role, Menu, Permission
from schemas import RoleCreate, RoleUpdate, RoleResponse
from typing import List
from auth import get_current_user, check_permission

router = APIRouter(tags=["roles"])


def require_permission(permission_code: str):
    """Create a dependency that requires a specific permission"""
    async def dependency(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        return await check_permission(permission_code, current_user, db)
    return dependency


@router.get("", response_model=List[RoleResponse])
async def get_roles(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("role:list"))
):
    """获取角色列表"""
    roles = db.query(Role).filter(Role.status == 1).all()
    return roles


@router.post("", response_model=RoleResponse)
async def create_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("role:create"))
):
    """创建角色"""
    # 创建角色
    db_role = Role(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role: RoleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("role:update"))
):
    """更新角色"""
    # 查找角色
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 更新角色
    for key, value in role.dict(exclude_unset=True).items():
        setattr(db_role, key, value)
    
    db.commit()
    db.refresh(db_role)
    return db_role


@router.delete("/{role_id}")
async def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("role:delete"))
):
    """删除角色（软删除）"""
    # 查找角色
    db_role = db.query(Role).filter(Role.id == role_id).first()
    if not db_role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 软删除
    db_role.status = 0
    db.commit()
    
    return {"message": "角色删除成功"}


@router.post("/{role_id}/menus")
async def assign_menus_to_role(
    role_id: int,
    menu_ids: List[int],
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("role:assign_menus"))
):
    """为角色分配菜单权限"""
    # 查找角色
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 清除现有菜单权限
    role.menus.clear()
    
    # 分配新菜单权限
    for menu_id in menu_ids:
        menu = db.query(Menu).filter(Menu.id == menu_id).first()
        if menu:
            role.menus.append(menu)
    
    try:
        db.commit()
        # 刷新角色对象，确保会话缓存中的角色对象与数据库保持一致
        db.refresh(role)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"菜单权限分配失败: {str(e)}")
    
    return {"message": "菜单权限分配成功"}


@router.post("/{role_id}/permissions")
async def assign_permissions_to_role(
    role_id: int,
    permission_ids: List[int],
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("role:assign_permissions"))
):
    """为角色分配按钮权限"""
    # 查找角色
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 清除现有权限
    role.permissions.clear()
    
    # 分配新权限
    for permission_id in permission_ids:
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if permission:
            role.permissions.append(permission)
    
    try:
        db.commit()
        # 刷新角色对象，确保会话缓存中的角色对象与数据库保持一致
        db.refresh(role)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"按钮权限分配失败: {str(e)}")
    
    return {"message": "按钮权限分配成功"}


@router.get("/{role_id}/menus")
async def get_role_menus(
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取角色的菜单权限"""
    # 查找角色
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 刷新角色对象，确保从数据库中重新加载数据
    db.refresh(role)
    
    return role.menus


@router.get("/{role_id}/permissions")
async def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取角色的按钮权限"""
    # 查找角色
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    # 刷新角色对象，确保从数据库中重新加载数据
    db.refresh(role)
    
    return role.permissions
