from sqlalchemy import text
from db import SessionLocal, Menu, Permission

def create_defect_menu_and_permissions():
    """创建缺陷管理菜单和权限"""
    db = SessionLocal()
    try:
        # 查询系统管理菜单
        system_menu = db.query(Menu).filter(Menu.name == "系统管理").first()
        
        if not system_menu:
            print("未找到系统管理菜单，请先创建系统管理菜单")
            return
        
        # 检查是否已存在缺陷管理菜单
        existing_defect_menu = db.query(Menu).filter(Menu.name == "缺陷管理").first()
        if existing_defect_menu:
            print("缺陷管理菜单已存在，跳过创建")
            defect_menu = existing_defect_menu
        else:
            # 创建缺陷管理菜单
            defect_menu = Menu(
                name="缺陷管理",
                parent_id=system_menu.id,
                path="/defects",
                component="Defects.vue",
                icon="Warning",
                order_index=5,
                type="menu"
            )
            db.add(defect_menu)
            db.commit()
            db.refresh(defect_menu)
            print(f"创建缺陷管理菜单成功，ID: {defect_menu.id}")
        
        # 创建缺陷管理权限
        permissions = [
            {
                "name": "查看缺陷列表",
                "code": "defect:list",
                "description": "查看缺陷列表权限"
            },
            {
                "name": "创建缺陷",
                "code": "defect:create",
                "description": "创建缺陷权限"
            },
            {
                "name": "编辑缺陷",
                "code": "defect:update",
                "description": "编辑缺陷权限"
            },
            {
                "name": "删除缺陷",
                "code": "defect:delete",
                "description": "删除缺陷权限"
            }
        ]
        
        for perm_data in permissions:
            existing_perm = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
            if existing_perm:
                print(f"权限 {perm_data['code']} 已存在，跳过创建")
            else:
                permission = Permission(
                    name=perm_data["name"],
                    code=perm_data["code"],
                    description=perm_data["description"],
                    menu_id=defect_menu.id
                )
                db.add(permission)
                db.commit()
                print(f"创建权限 {perm_data['code']} 成功")
        
        print("缺陷管理菜单和权限创建完成")
        
    except Exception as e:
        print(f"创建缺陷管理菜单和权限失败: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_defect_menu_and_permissions()
