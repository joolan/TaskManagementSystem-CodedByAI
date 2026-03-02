#!/usr/bin/env python3
"""
检查菜单重复问题
"""
import sqlite3

db_path = "task-board-backend/task_board.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("检查菜单数据...")
print("=" * 50)

# 查询所有菜单
cursor.execute("SELECT id, name, parent_id FROM menus WHERE status = 1 ORDER BY id")
menus = cursor.fetchall()

print(f"\n数据库中的菜单数量: {len(menus)}")
print("\n菜单列表:")
for menu in menus:
    print(f"ID: {menu[0]}, 名称: {menu[1]}, 父级ID: {menu[2]}")

# 检查是否有重复的菜单
cursor.execute("SELECT id, name, COUNT(*) FROM menus GROUP BY id, name HAVING COUNT(*) > 1")
duplicates = cursor.fetchall()

if duplicates:
    print(f"\n警告：发现重复的菜单！")
    for dup in duplicates:
        print(f"ID: {dup[0]}, 名称: {dup[1]}, 数量: {dup[2]}")
else:
    print(f"\n✓ 没有重复的菜单")

# 检查parent_id引用
print(f"\n检查parent_id引用:")
for menu in menus:
    menu_id, name, parent_id = menu[0], menu[1], menu[2]
    if parent_id is not None:
        parent_exists = any(m[0] == parent_id for m in menus)
        if not parent_exists:
            print(f"警告：菜单 '{name}' (ID: {menu_id}) 的父级ID {parent_id} 不存在")

conn.close()
print("\n" + "=" * 50)