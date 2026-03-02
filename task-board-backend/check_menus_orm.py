from db import SessionLocal, Menu

# 创建数据库会话
db = SessionLocal()

try:
    # 查询所有菜单并按ID排序
    menus = db.query(Menu).order_by(Menu.id).all()
    
    print('现有菜单结构:')
    print('-' * 100)
    print(f'{"ID":<5} {"名称":<20} {"父ID":<8} {"路径":<30} {"图标":<20} {"类型":<10}')
    print('-' * 100)
    
    for menu in menus:
        path = menu.path or ''
        icon = menu.icon or ''
        parent_id = menu.parent_id or ''
        print(f'{menu.id:<5} {menu.name:<20} {parent_id:<8} {path:<30} {icon:<20} {menu.type:<10}')
    
    print('-' * 100)
    print(f'总菜单数: {len(menus)}')
    
finally:
    # 关闭会话
    db.close()