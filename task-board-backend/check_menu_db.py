#!/usr/bin/env python3
"""
检查数据库中的菜单数据
"""
import sqlite3

db_path = "task-board-backend/task_board.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("检查数据库中的菜单数据...")
print("=" * 50)

# 查询所有菜单
cursor.execute("SELECT id, name, parent_id, order_index FROM menus WHERE status = 1 ORDER BY order_index")
menus = cursor.fetchall()

print(f"\n数据库中的菜单数量: {len(menus)}")
print("\n菜单列表:")
for menu in menus:
    print(f"ID: {menu[0]}, 名称: {menu[1]}, 父级ID: {menu[2]}, 排序: {menu[3]}")

# 检查是否有重复的ID
menu_ids = [menu[0] for menu in menus]
duplicates = [id for id in menu_ids if menu_ids.count(id) > 1]

if duplicates:
    print(f"\n警告：发现重复的菜单ID: {set(duplicates)}")
else:
    print(f"\n✓ 没有重复的菜单ID")

# 检查parent_id引用是否正确
print(f"\n检查parent_id引用:")
for menu in menus:
    menu_id, name, parent_id = menu[0], menu[1], menu[2]
    if parent_id is not None:
        parent_exists = any(m[0] == parent_id for m in menus)
        if not parent_exists:
            print(f"警告：菜单 '{name}' (ID: {menu_id}) 的父级ID {parent_id} 不存在")

conn.close()
print("\n" + "=" * 50)