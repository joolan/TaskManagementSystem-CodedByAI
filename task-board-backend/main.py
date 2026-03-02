from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from sqlalchemy.orm import Session
import copy

from db import init_db, engine, Base, get_db
from auth import get_current_user
from routes import auth, tasks, comments, attachments, stats, settings, uploads, logs, releases, requirements, database, memos, menus, roles, permissions, messages, defects


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Task Board API",
    description="API for Task Board System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(comments.router, prefix="/api", tags=["comments"])
app.include_router(attachments.router, prefix="/api", tags=["attachments"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(uploads.router, prefix="/api", tags=["uploads"])
app.include_router(logs.router, prefix="/api", tags=["logs"])
app.include_router(messages.router, prefix="/api", tags=["messages"])
app.include_router(releases.router, prefix="/api/releases", tags=["releases"])
app.include_router(requirements.router, prefix="/api/requirements", tags=["requirements"])
app.include_router(database.router, prefix="/api", tags=["database"])
app.include_router(memos.router, prefix="/api/memos", tags=["memos"])
app.include_router(menus.router, prefix="/api/menus", tags=["menus"])
app.include_router(roles.router, prefix="/api/roles", tags=["roles"])
app.include_router(permissions.router, prefix="/api/permissions", tags=["permissions"])
app.include_router(defects.router, prefix="/api/defects", tags=["defects"])


@app.get("/")
async def root():
    return {"message": "Welcome to Task Board API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# 直接在main.py中添加菜单相关接口
from db import Menu, role_menus
from schemas import MenuResponse
from typing import List

@app.get("/api/menus", response_model=List[MenuResponse])
async def get_menus(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取菜单列表"""
    menus = db.query(Menu).filter(Menu.status == 1).order_by(Menu.order_index).all()
    return menus


@app.get("/api/menus/tree")
async def get_menu_tree(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取菜单树结构"""
    # 获取所有启用的菜单
    all_menus = db.query(Menu).filter(Menu.status == 1).order_by(Menu.order_index).all()
    
    # 构建菜单树 - 使用字典避免重复
    menu_dict = {}
    for menu in all_menus:
        menu_dict[menu.id] = {
            "id": menu.id,
            "name": menu.name,
            "parent_id": menu.parent_id,
            "path": menu.path,
            "component": menu.component,
            "icon": menu.icon,
            "order_index": menu.order_index,
            "type": menu.type,
            "external_url": menu.external_url,
            "target": menu.target,
            "status": menu.status,
            "created_at": menu.created_at,
            "updated_at": menu.updated_at,
            "children": []
        }
    
    # 构建父子关系
    root_menus = []
    for menu_id, menu in menu_dict.items():
        if menu["parent_id"] is None:
            root_menus.append(copy.deepcopy(menu))
        else:
            parent = menu_dict.get(menu["parent_id"])
            if parent:
                # 检查是否已经添加过这个子菜单，避免重复
                if menu_id not in [child["id"] for child in parent["children"]]:
                    parent["children"].append(copy.deepcopy(menu))
    
    return root_menus


@app.get("/api/menus/user", response_model=List[MenuResponse])
async def get_user_menus(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取用户可访问的菜单"""
    # 超级管理员拥有所有菜单权限
    if current_user.username == "admin":
        # 获取所有启用的菜单
        all_menus = db.query(Menu).filter(Menu.status == 1).order_by(Menu.order_index).all()
    else:
        # 获取用户角色的菜单权限
        user_role_menu_ids = set()
        
        # 从角色中获取菜单权限
        for role in current_user.roles:
            role_menu_ids = db.query(role_menus.c.menu_id).filter(role_menus.c.role_id == role.id).all()
            for (menu_id,) in role_menu_ids:
                user_role_menu_ids.add(menu_id)
        
        # 从用户额外权限中获取菜单权限
        for permission in current_user.extra_permissions:
            if permission.menu_id:
                user_role_menu_ids.add(permission.menu_id)
        
        # 获取用户可访问的菜单
        if user_role_menu_ids:
            all_menus = db.query(Menu).filter(
                Menu.id.in_(user_role_menu_ids),
                Menu.status == 1
            ).order_by(Menu.order_index).all()
        else:
            all_menus = []
    
    # 构建菜单树 - 使用字典避免重复
    menu_dict = {}
    for menu in all_menus:
        menu_dict[menu.id] = {
            "id": menu.id,
            "name": menu.name,
            "parent_id": menu.parent_id,
            "path": menu.path,
            "component": menu.component,
            "icon": menu.icon,
            "order_index": menu.order_index,
            "type": menu.type,
            "external_url": menu.external_url,
            "target": menu.target,
            "status": menu.status,
            "created_at": menu.created_at,
            "updated_at": menu.updated_at,
            "children": []
        }
    
    # 构建父子关系
    root_menus = []
    for menu_id, menu in menu_dict.items():
        if menu["parent_id"] is None:
            root_menus.append(menu)
        else:
            parent = menu_dict.get(menu["parent_id"])
            if parent:
                # 检查是否已经添加过这个子菜单，避免重复
                if menu_id not in [child["id"] for child in parent["children"]]:
                    parent["children"].append(menu)
    
    return root_menus


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
