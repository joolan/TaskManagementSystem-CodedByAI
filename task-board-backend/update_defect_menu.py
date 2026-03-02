from db import SessionLocal, Menu

db = SessionLocal()
try:
    # 找到缺陷管理菜单
    defect_menu = db.query(Menu).filter(Menu.name == "缺陷管理").first()
    if defect_menu:
        print(f"找到缺陷管理菜单: id={defect_menu.id}, name={defect_menu.name}, parent_id={defect_menu.parent_id}")
        # 修改为一级菜单
        defect_menu.parent_id = None
        db.commit()
        print("缺陷管理菜单已修改为一级菜单")
    else:
        print("未找到缺陷管理菜单")
    
    # 再次查看菜单结构
    print("\n修改后的菜单结构:")
    menus = db.query(Menu).all()
    for menu in menus:
        print(f'id: {menu.id}, name: {menu.name}, parent_id: {menu.parent_id}, path: {menu.path}')
finally:
    db.close()
