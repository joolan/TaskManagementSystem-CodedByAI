from db import get_db, User, Role, Menu, SessionLocal

# 获取数据库会话
db = SessionLocal()

# 查找用户id=5的用户
user = db.query(User).filter(User.id == 5).first()
print(f"User: {user.username}")

# 检查用户的角色
print("Roles:")
for role in user.roles:
    print(f"  - {role.name}")
    # 检查角色的菜单权限
    print("    Menus:")
    for menu in role.menus:
        print(f"      - {menu.name} (id: {menu.id})")

# 检查用户的额外菜单权限
print("Extra menus:")
for menu in user.extra_menus:
    print(f"  - {menu.name} (id: {menu.id})")

# 关闭数据库会话
db.close()