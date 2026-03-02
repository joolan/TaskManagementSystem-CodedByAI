#!/usr/bin/env python3
"""
检查特定菜单
"""
import sqlite3

db_path = "task-board-backend/task_board.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("检查ID为4的菜单...")
print("=" * 50)

# 查询ID为4的菜单
cursor.execute("SELECT * FROM menus WHERE id = 4")
menu = cursor.fetchone()

if menu:
    print(f"找到菜单：")
    print(f"ID: {menu[0]}")
    print(f"名称: {menu[1]}")
    print(f"父级ID: {menu[2]}")
    print(f"路径: {menu[3]}")
    print(f"组件: {menu[4]}")
    print(f"图标: {menu[5]}")
    print(f"排序: {menu[6]}")
    print(f"类型: {menu[7]}")
    print(f"外部URL: {menu[8]}")
    print(f"目标: {menu[9]}")
    print(f"状态: {menu[10]}")
    print(f"创建时间: {menu[11]}")
    print(f"更新时间: {menu[12]}")
else:
    print("未找到ID为4的菜单")

# 查询所有菜单
cursor.execute("SELECT id, name, parent_id, status FROM menus ORDER BY id")
menus = cursor.fetchall()

print(f"\n所有菜单列表:")
for menu in menus:
    print(f"ID: {menu[0]}, 名称: {menu[1]}, 父级ID: {menu[2]}, 状态: {menu[3]}")

conn.close()
print("\n" + "=" * 50)