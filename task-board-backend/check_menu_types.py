from db import get_db, Menu

db = next(get_db())

menus = db.query(Menu.id, Menu.name, Menu.type).all()

print('Menu Types:')
for menu in menus:
    print(f'ID: {menu[0]}, Name: {menu[1]}, Type: {menu[2]}')

db.close()
