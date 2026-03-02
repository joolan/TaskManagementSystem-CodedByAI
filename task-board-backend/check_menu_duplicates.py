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
cursor.execute("SELECT id, name, parent_id FROM menus WHERE status = 1 ORDER BY id")
menus = cursor.fetchall()

print(f"\n数据库中的菜单数量: {len(menus)}")
print("\n菜单列表:")
for menu in menus:
    print(f"ID: {menu[0]}, 名称: {menu[1]}, 父级ID: {menu[2]}")

# 检查是否有重复的菜单ID
menu_ids = [menu[0] for menu in menus]
duplicates = [id for id in menu_ids if menu_ids.count(id) > 1]

if duplicates:
    print(f"\n警告：发现重复的菜单ID！")
    for dup in set(duplicates):
        print(f"ID: {dup}, 数量: {menu_ids.count(dup)}")
else:
    print(f"\n✓ 没有重复的菜单ID")

conn.close()
print("\n" + "=" * 50)