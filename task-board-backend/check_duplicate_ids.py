from db import get_db, Menu, Permission

db = next(get_db())

menus = db.query(Menu.id).all()
permissions = db.query(Permission.id).all()

menu_ids = [m[0] for m in menus]
perm_ids = [p[0] for p in permissions]

print('Menu IDs:', menu_ids)
print('Permission IDs:', perm_ids)

duplicate_ids = set(menu_ids) & set(perm_ids)
print('Duplicate IDs:', duplicate_ids if duplicate_ids else 'None')

db.close()
