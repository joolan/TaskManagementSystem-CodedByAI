#!/usr/bin/env python3
"""
调试菜单树构建逻辑
"""
import sqlite3

db_path = "task-board-backend/task_board.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("调试菜单树构建逻辑...")
print("=" * 50)

# 查询所有菜单
cursor.execute("SELECT id, name, parent_id FROM menus WHERE status = 1 ORDER BY id")
menus = cursor.fetchall()

print(f"\n数据库中的菜单数量: {len(menus)}")
print("\n菜单列表:")
for menu in menus:
    print(f"ID: {menu[0]}, 名称: {menu[1]}, 父级ID: {menu[2]}")

# 模拟构建菜单树的过程
print("\n\n模拟构建菜单树...")

menu_dict = {}
for menu in menus:
    menu_dict[menu[0]] = {
        "id": menu[0],
        "name": menu[1],
        "parent_id": menu[2],
        "children": []
    }

print(f"\nmenu_dict中的菜单数量: {len(menu_dict)}")
print(f"menu_dict的keys: {list(menu_dict.keys())}")

# 构建父子关系
root_menus = []
for menu_id, menu in menu_dict.items():
    print(f"\n处理菜单 ID: {menu_id}, 名称: {menu['name']}, 父级ID: {menu['parent_id']}")
    if menu["parent_id"] is None:
        print(f"  -> 添加到根菜单")
        root_menus.append(menu)
    else:
        parent = menu_dict.get(menu["parent_id"])
        if parent:
            print(f"  -> 找到父菜单: {parent['name']}")
            # 检查是否已经添加过这个子菜单，避免重复
            existing_children_ids = [child["id"] for child in parent["children"]]
            print(f"  -> 父菜单当前的子菜单IDs: {existing_children_ids}")
            if menu_id not in existing_children_ids:
                print(f"  -> 添加子菜单 {menu['name']} 到父菜单 {parent['name']}")
                parent["children"].append(menu)
            else:
                print(f"  -> 警告：子菜单 {menu['name']} 已经存在于父菜单 {parent['name']} 中！")
        else:
            print(f"  -> 警告：找不到父菜单 ID: {menu['parent_id']}")

print(f"\n\n最终根菜单数量: {len(root_menus)}")
print("\n根菜单:")
for root in root_menus:
    print(f"  - {root['name']} (ID: {root['id']})")
    if root["children"]:
        print(f"    子菜单:")
        for child in root["children"]:
            print(f"      - {child['name']} (ID: {child['id']})")
            if child["children"]:
                print(f"        子子菜单:")
                for grandchild in child["children"]:
                    print(f"          - {grandchild['name']} (ID: {grandchild['id']})")

conn.close()
print("\n" + "=" * 50)