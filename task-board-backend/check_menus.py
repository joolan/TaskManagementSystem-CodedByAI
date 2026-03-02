from db import SessionLocal, Menu

db = SessionLocal()
try:
    menus = db.query(Menu).all()
    print("当前菜单结构:")
    for menu in menus:
        print(f'id: {menu.id}, name: {menu.name}, parent_id: {menu.parent_id}, path: {menu.path}')
finally:
    db.close()
