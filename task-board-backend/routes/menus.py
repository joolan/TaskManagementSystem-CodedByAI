from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db, Menu, User, role_menus, Permission
from schemas import MenuCreate, MenuUpdate, MenuResponse
from typing import List
from auth import get_current_user, check_permission

router = APIRouter(tags=["menus"])


def require_permission(permission_code: str):
    """Create a dependency that requires a specific permission"""
    async def dependency(
        current_user = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        return await check_permission(permission_code, current_user, db)
    return dependency


@router.get("", response_model=List[MenuResponse])
async def get_menus(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("menu:list"))
):
    """获取菜单列表（仅启用的菜单）"""
    menus = db.query(Menu).filter(Menu.status == 1).order_by(Menu.order_index).all()
    return menus


@router.get("/all", response_model=List[MenuResponse])
async def get_all_menus(
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("menu:list"))
):
    """获取所有菜单（包括禁用的菜单）"""
    menus = db.query(Menu).order_by(Menu.order_index).all()
    return menus


@router.post("", response_model=MenuResponse)
async def create_menu(
    menu: MenuCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("menu:create"))
):
    """创建菜单"""
    # 创建菜单
    db_menu = Menu(**menu.dict())
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    return db_menu


@router.get("/tree")
async def get_menu_tree(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取菜单树结构"""
    # 获取所有启用的菜单
    menus = db.query(Menu).filter(Menu.status == 1).order_by(Menu.order_index).all()
    
    # 获取所有权限
    permissions = db.query(Permission).all()
    # 按菜单ID组织权限
    menu_permissions = {}
    for perm in permissions:
        if perm.menu_id:
            if perm.menu_id not in menu_permissions:
                menu_permissions[perm.menu_id] = []
            menu_permissions[perm.menu_id].append({
                "id": perm.id,
                "name": perm.name,
                "code": perm.code,
                "description": perm.description,
                "menu_id": perm.menu_id
            })
    
    # 构建菜单树
    menu_dict = {}
    for menu in menus:
        menu_dict[menu.id] = {
            "id": menu.id,
            "name": menu.name,
            "path": menu.path,
            "icon": menu.icon,
            "type": menu.type,
            "order_index": menu.order_index,
            "parent_id": menu.parent_id,
            "children": [],
            "permissions": menu_permissions.get(menu.id, [])
        }
    
    # 构建父子关系
    menu_tree = []
    for menu_id, menu_item in menu_dict.items():
        parent_id = menu_item["parent_id"]
        if parent_id is None:
            # 根菜单
            menu_tree.append(menu_item)
        else:
            # 子菜单
            if parent_id in menu_dict:
                menu_dict[parent_id]["children"].append(menu_item)
    
    # 对菜单树中的每个层级按order_index排序
    def sort_menu_tree(menus):
        # 对当前层级的菜单按order_index排序
        menus.sort(key=lambda x: x["order_index"])
        # 对每个菜单的子菜单递归排序
        for menu in menus:
            if menu.get("children"):
                sort_menu_tree(menu["children"])
    
    sort_menu_tree(menu_tree)
    
    return menu_tree


@router.get("/parent-options")
async def get_parent_menu_options(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取上级菜单选项（返回两级菜单，用于下拉选择）"""
    # 获取所有菜单（包括隐藏的）
    all_menus = db.query(Menu).order_by(Menu.order_index).all()
    
    # 构建菜单字典
    menu_dict = {}
    for menu in all_menus:
        menu_dict[menu.id] = {
            "id": menu.id,
            "name": menu.name,
            "path": menu.path,
            "icon": menu.icon,
            "type": menu.type,
            "order_index": menu.order_index,
            "parent_id": menu.parent_id,
            "children": []
        }
    
    # 构建两级菜单树（只包含根菜单和一级子菜单）
    menu_tree = []
    for menu in all_menus:
        menu_item = menu_dict[menu.id]
        if menu.parent_id is None:
            # 根菜单（第一级）
            # 添加该根菜单的子菜单（第二级）
            for child_menu in all_menus:
                if child_menu.parent_id == menu.id:
                    menu_item["children"].append(menu_dict[child_menu.id])
            menu_tree.append(menu_item)
    
    # 排序
    menu_tree.sort(key=lambda x: x["order_index"])
    for menu in menu_tree:
        menu["children"].sort(key=lambda x: x["order_index"])
    
    return menu_tree


@router.get("/all-tree")
async def get_all_menu_tree(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取完整菜单树（返回三级菜单，用于判断菜单层级关系）"""
    # 获取所有菜单（包括隐藏的）
    all_menus = db.query(Menu).order_by(Menu.order_index).all()
    
    # 构建菜单字典
    menu_dict = {}
    for menu in all_menus:
        menu_dict[menu.id] = {
            "id": menu.id,
            "name": menu.name,
            "path": menu.path,
            "icon": menu.icon,
            "type": menu.type,
            "order_index": menu.order_index,
            "parent_id": menu.parent_id,
            "children": []
        }
    
    # 构建三级菜单树（包含根菜单、一级子菜单、二级子菜单）
    menu_tree = []
    for menu in all_menus:
        menu_item = menu_dict[menu.id]
        if menu.parent_id is None:
            # 根菜单（第一级）
            # 添加该根菜单的子菜单（第二级）
            for child_menu in all_menus:
                if child_menu.parent_id == menu.id:
                    child_item = menu_dict[child_menu.id]
                    # 添加二级子菜单（第三级）
                    for grandchild_menu in all_menus:
                        if grandchild_menu.parent_id == child_menu.id:
                            child_item["children"].append(menu_dict[grandchild_menu.id])
                    menu_item["children"].append(child_item)
            menu_tree.append(menu_item)
    
    # 排序
    menu_tree.sort(key=lambda x: x["order_index"])
    for menu in menu_tree:
        menu["children"].sort(key=lambda x: x["order_index"])
        for child in menu["children"]:
            child["children"].sort(key=lambda x: x["order_index"])
    
    return menu_tree


@router.get("/user")
async def get_user_menus(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取用户可访问的菜单"""
    # 管理员获取所有菜单
    if current_user.username == "admin":
        menus = db.query(Menu).filter(Menu.status == 1).order_by(Menu.order_index).all()
    else:
        # 普通用户获取分配的菜单
        # 从用户角色中获取菜单
        user_menus = set()
        for role in current_user.roles:
            for menu in role.menus:
                if menu.status == 1:
                    user_menus.add(menu)
        # 从用户额外权限中获取菜单
        for menu in current_user.extra_menus:
            if menu.status == 1:
                user_menus.add(menu)
        
        # 从用户角色中获取权限所属的菜单
        for role in current_user.roles:
            for permission in role.permissions:
                if permission.menu_id:
                    menu = db.query(Menu).filter(Menu.id == permission.menu_id, Menu.status == 1).first()
                    if menu:
                        user_menus.add(menu)
        # 从用户额外权限中获取权限所属的菜单
        for permission in current_user.extra_permissions:
            if permission.menu_id:
                menu = db.query(Menu).filter(Menu.id == permission.menu_id, Menu.status == 1).first()
                if menu:
                    user_menus.add(menu)
        
        # 获取所有菜单的上级菜单
        all_menus = set(user_menus)
        for menu in list(all_menus):
            # 递归获取上级菜单
            current_menu = menu
            while current_menu.parent_id:
                parent_menu = db.query(Menu).filter(Menu.id == current_menu.parent_id, Menu.status == 1).first()
                if parent_menu:
                    all_menus.add(parent_menu)
                    current_menu = parent_menu
                else:
                    break
        
        menus = list(all_menus)
    
    # 构建菜单树
    menu_dict = {}
    for menu in menus:
        menu_dict[menu.id] = {
            "id": menu.id,
            "name": menu.name,
            "path": menu.path,
            "component": menu.component,
            "icon": menu.icon,
            "type": menu.type,
            "order_index": menu.order_index,
            "parent_id": menu.parent_id,
            "children": []
        }
    
    # 构建父子关系
    menu_tree = []
    for menu_id, menu_item in menu_dict.items():
        parent_id = menu_item["parent_id"]
        if parent_id is None:
            # 根菜单
            menu_tree.append(menu_item)
        else:
            # 子菜单
            if parent_id in menu_dict:
                menu_dict[parent_id]["children"].append(menu_item)
    
    # 对菜单树中的每个层级按order_index排序
    def sort_menu_tree(menus):
        # 对当前层级的菜单按order_index排序
        menus.sort(key=lambda x: x["order_index"])
        # 对每个菜单的子菜单递归排序
        for menu in menus:
            if menu.get("children"):
                sort_menu_tree(menu["children"])
    
    sort_menu_tree(menu_tree)
    
    return menu_tree


def get_menu_depth(menu_id: int, menu_dict: dict, visited: set = None) -> int:
    """获取菜单的深度（从根菜单到当前菜单的层级数）"""
    if visited is None:
        visited = set()
    
    if menu_id in visited:
        return 0  # 防止循环引用
    
    visited.add(menu_id)
    
    if menu_id not in menu_dict:
        return 0
    
    menu = menu_dict[menu_id]
    if menu.parent_id is None:
        return 1
    
    parent_depth = get_menu_depth(menu.parent_id, menu_dict, visited)
    return parent_depth + 1 if parent_depth > 0 else 1


def get_max_children_depth(menu_id: int, menu_dict: dict, visited: set = None) -> int:
    """获取菜单的最大子菜单深度"""
    if visited is None:
        visited = set()
    
    if menu_id in visited:
        return 0  # 防止循环引用
    
    visited.add(menu_id)
    
    max_depth = 0
    for menu in menu_dict.values():
        if menu.parent_id == menu_id:
            child_depth = get_max_children_depth(menu.id, menu_dict, visited.copy())
            max_depth = max(max_depth, child_depth + 1)
    
    return max_depth


@router.put("/{menu_id}", response_model=MenuResponse)
async def update_menu(
    menu_id: int,
    menu: MenuUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("menu:update"))
):
    """更新菜单"""
    # 查找菜单
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    # 获取更新后的数据
    update_data = menu.dict(exclude_unset=True)
    new_parent_id = update_data.get("parent_id")
    
    # 校验1：父菜单不能是自己
    if new_parent_id == menu_id:
        raise HTTPException(status_code=400, detail="父菜单不能是当前菜单本身")
    
    # 校验2：父菜单层级 + 当前菜单子菜单层级 <= 3
    if new_parent_id is not None:
        # 获取所有菜单
        all_menus = db.query(Menu).all()
        menu_dict = {m.id: m for m in all_menus}
        
        # 获取新父菜单的深度
        parent_depth = get_menu_depth(new_parent_id, menu_dict)
        
        # 获取当前菜单的最大子菜单深度
        children_depth = get_max_children_depth(menu_id, menu_dict)
        
        # 总深度 = 父菜单深度 + 1（当前菜单）+ 子菜单深度
        total_depth = parent_depth + 1 + children_depth
        
        if total_depth > 3:
            raise HTTPException(status_code=400, detail=f"设置此父菜单会导致菜单层级超过3级（当前层级：{total_depth}）")
    
    # 更新菜单
    for key, value in update_data.items():
        setattr(db_menu, key, value)
    
    db.commit()
    db.refresh(db_menu)
    return db_menu


@router.delete("/{menu_id}")
async def delete_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("menu:delete"))
):
    """删除菜单（软删除）"""
    # 查找菜单
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    # 软删除
    db_menu.status = 0
    db.commit()
    
    return {"message": "菜单删除成功"}


@router.get("/{menu_id}", response_model=MenuResponse)
async def get_menu(
    menu_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_permission("menu:list"))
):
    """获取菜单详情"""
    # 查找菜单
    db_menu = db.query(Menu).filter(Menu.id == menu_id).first()
    if not db_menu:
        raise HTTPException(status_code=404, detail="菜单不存在")
    
    return db_menu