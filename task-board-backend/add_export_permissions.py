#!/usr/bin/env python3
"""
添加导出相关权限到数据库
运行方式: python add_export_permissions.py
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal, Permission, Menu

def add_export_permissions():
    """添加导出相关权限"""
    db = SessionLocal()
    try:
        # 定义需要添加的权限
        permissions = [
            # 缺陷导出权限
            {
                "name": "缺陷导出",
                "code": "defect:export",
                "description": "导出缺陷数据到Excel"
            },
            # 任务导出权限（如果还没有的话）
            {
                "name": "任务导出",
                "code": "task:export",
                "description": "导出任务数据到Excel"
            },
            # 发版导出权限（如果还没有的话）
            {
                "name": "发版导出",
                "code": "release:export",
                "description": "导出发版数据到Excel"
            },
            # 需求导出权限（如果还没有的话）
            {
                "name": "需求导出",
                "code": "requirement:export",
                "description": "导出需求数据到Excel"
            },
        ]

        added_count = 0
        for perm_data in permissions:
            # 检查权限是否已存在
            existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
            if existing:
                print(f"权限已存在: {perm_data['code']} - {perm_data['name']}")
                continue

            # 创建新权限
            new_permission = Permission(
                name=perm_data["name"],
                code=perm_data["code"],
                description=perm_data["description"]
            )
            db.add(new_permission)
            added_count += 1
            print(f"添加权限: {perm_data['code']} - {perm_data['name']}")

        db.commit()
        print(f"\n成功添加 {added_count} 个权限")

        # 显示所有权限
        print("\n当前所有权限列表:")
        all_permissions = db.query(Permission).order_by(Permission.code).all()
        for perm in all_permissions:
            print(f"  - {perm.code}: {perm.name}")

    except Exception as e:
        db.rollback()
        print(f"添加权限失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_export_permissions()
