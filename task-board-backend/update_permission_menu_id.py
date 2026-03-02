#!/usr/bin/env python3
"""
更新导出权限的menu_id
运行方式: python update_permission_menu_id.py
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal, Permission, Menu

def update_permission_menu_ids():
    """更新导出权限的menu_id"""
    db = SessionLocal()
    try:
        # 查询菜单ID
        menus = db.query(Menu).all()
        menu_dict = {menu.name: menu.id for menu in menus}
        
        print("当前菜单列表:")
        for name, menu_id in menu_dict.items():
            print(f"  - {menu_id}: {name}")
        
        # 权限与菜单的映射关系
        permission_menu_mapping = {
            "defect:export": "缺陷管理",
            "task:export": "任务管理",
            "release:export": "发版管理",
            "requirement:export": "需求管理"
        }
        
        print("\n更新权限的menu_id:")
        for perm_code, menu_name in permission_menu_mapping.items():
            # 查找权限
            permission = db.query(Permission).filter(Permission.code == perm_code).first()
            if not permission:
                print(f"  ⚠️ 权限不存在: {perm_code}")
                continue
            
            # 查找菜单ID
            menu_id = menu_dict.get(menu_name)
            if not menu_id:
                print(f"  ⚠️ 菜单不存在: {menu_name}")
                continue
            
            # 更新menu_id
            old_menu_id = permission.menu_id
            permission.menu_id = menu_id
            print(f"  ✓ {perm_code}: menu_id {old_menu_id} -> {menu_id} ({menu_name})")
        
        db.commit()
        print("\n更新完成!")
        
        # 显示更新后的权限
        print("\n更新后的权限列表:")
        all_permissions = db.query(Permission).order_by(Permission.code).all()
        for perm in all_permissions:
            menu_name = menu_dict.get(perm.menu_id, "未关联") if perm.menu_id else "未关联"
            print(f"  - {perm.code}: {perm.name} (menu_id: {perm.menu_id}, 菜单: {menu_name})")

    except Exception as e:
        db.rollback()
        print(f"更新失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    update_permission_menu_ids()
