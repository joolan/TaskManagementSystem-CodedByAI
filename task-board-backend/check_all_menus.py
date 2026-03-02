#!/usr/bin/env python3
"""
检查数据库中的所有菜单记录
"""
import sqlite3

db_path = "task-board-backend/task_board.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("检查数据库中的所有菜单记录...")
print("=" * 50)

# 查询所有菜单
cursor.execute("SELECT id, name, parent_id FROM menus ORDER BY id")
menus = cursor.fetchall()

print(f"\n数据库中的菜单数量: {len(menus)}")
print("\n菜单列表:")
for menu in menus:
    print(f"ID: {menu[0]}, 名称: {menu[1]}, 父级ID: {menu[2]}")

# 检查是否有重复的菜单ID
cursor.execute("SELECT id, COUNT(*) FROM menus GROUP BY id HAVING COUNT(*) > 1")
duplicates = cursor.fetchall()

if duplicates:
    print(f"\n警告：发现重复的菜单ID！")
    for dup in duplicates:
        print(f"ID: {dup[0]}, 数量: {dup[1]}")
else:
    print(f"\n✓ 没有重复的菜单ID")

# 检查ID为4的菜单的子菜单
cursor.execute("SELECT id, name, parent_id FROM menus WHERE parent_id = 4")
children_of_4 = cursor.fetchall()

print(f"\nID为4（用户角色管理）的子菜单:")
for child in children_of_4:
    print(f"ID: {child[0]}, 名称: {child[1]}, 父级ID: {child[2]}")

# 检查ID为3的菜单的子菜单
cursor.execute("SELECT id, name, parent_id FROM menus WHERE parent_id = 3")
children_of_3 = cursor.fetchall()

print(f"\nID为3（菜单管理）的子菜单:")
for child in children_of_3:
    print(f"ID: {child[0]}, 名称: {child[1]}, 父级ID: {child[2]}")

conn.close()
print("\n" + "=" * 50)