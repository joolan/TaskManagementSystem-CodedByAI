from db import SessionLocal, Permission

# 创建数据库会话
db = SessionLocal()

try:
    # 定义需要添加的按钮权限
    # 格式: (权限名称, 权限编码, 菜单ID, 描述)
    button_permissions = [
        # 任务管理菜单 (ID: 13)
        ("创建任务", "task:create", 13, "创建新任务"),
        ("更新任务", "task:update", 13, "更新任务信息"),
        ("删除任务", "task:delete", 13, "删除任务"),
        ("更新任务状态", "task:update_status", 13, "更新任务状态"),
        ("分配任务", "task:assign", 13, "分配任务负责人"),
        ("关注任务", "task:follow", 13, "关注任务"),
        ("添加工时", "task:add_hours", 13, "添加任务工时"),
        
        # 用户管理菜单 (ID: 5)
        ("创建用户", "user:create", 5, "创建新用户"),
        ("更新用户", "user:update", 5, "更新用户信息"),
        ("删除用户", "user:delete", 5, "删除用户"),
        ("修改密码", "user:change_password", 5, "修改用户密码"),
        ("解锁用户", "user:unlock", 5, "解锁被锁定的用户"),
        ("踢出登录", "user:revoke_session", 5, "踢出用户登录会话"),
        
        # 角色管理菜单 (ID: 6)
        ("创建角色", "role:create", 6, "创建新角色"),
        ("更新角色", "role:update", 6, "更新角色信息"),
        ("删除角色", "role:delete", 6, "删除角色"),
        ("分配菜单权限", "role:assign_menus", 6, "为角色分配菜单权限"),
        ("分配按钮权限", "role:assign_permissions", 6, "为角色分配按钮权限"),
        
        # 发版管理菜单 (ID: 14)
        ("创建发版标签", "release_tag:create", 14, "创建新发版标签"),
        ("更新发版标签", "release_tag:update", 14, "更新发版标签"),
        ("删除发版标签", "release_tag:delete", 14, "删除发版标签"),
        ("创建发版记录", "release:create", 14, "创建新发版记录"),
        ("更新发版记录", "release:update", 14, "更新发版记录"),
        ("删除发版记录", "release:delete", 14, "删除发版记录"),
        ("关注发版", "release:follow", 14, "关注发版记录"),
        
        # 需求管理菜单 (ID: 15)
        ("创建需求标签", "requirement_tag:create", 15, "创建新需求标签"),
        ("更新需求标签", "requirement_tag:update", 15, "更新需求标签"),
        ("删除需求标签", "requirement_tag:delete", 15, "删除需求标签"),
        ("创建需求", "requirement:create", 15, "创建新需求"),
        ("更新需求", "requirement:update", 15, "更新需求信息"),
        ("删除需求", "requirement:delete", 15, "删除需求"),
        ("需求转任务", "requirement:convert", 15, "将需求转换为任务"),
        
        # 系统设置菜单 (ID: 2)
        ("备份数据库", "database:backup", 2, "备份系统数据库"),
        ("还原数据库", "database:restore", 2, "还原系统数据库"),
        
        # 菜单管理菜单 (ID: 3)
        ("创建菜单", "menu:create", 3, "创建新菜单"),
        ("更新菜单", "menu:update", 3, "更新菜单信息"),
        ("删除菜单", "menu:delete", 3, "删除菜单"),
        
        # 备忘录相关 (可以关联到工作台菜单 ID: 12)
        ("创建备忘录", "memo:create", 12, "创建新备忘录"),
        ("更新备忘录", "memo:update", 12, "更新备忘录"),
        ("删除备忘录", "memo:delete", 12, "删除备忘录"),
    ]
    
    # 批量添加权限
    added_count = 0
    for name, code, menu_id, description in button_permissions:
        # 检查权限是否已存在
        existing_perm = db.query(Permission).filter_by(code=code).first()
        if not existing_perm:
            new_perm = Permission(
                name=name,
                code=code,
                menu_id=menu_id,
                description=description
            )
            db.add(new_perm)
            added_count += 1
    
    # 提交更改
    db.commit()
    
    print(f'成功添加 {added_count} 个按钮权限到数据库中')
    
    # 打印添加的权限
    if added_count > 0:
        print('\n添加的权限列表:')
        print('-' * 100)
        print(f'{"ID":<5} {"名称":<20} {"编码":<30} {"菜单ID":<8} {"描述":<30}')
        print('-' * 100)
        
        # 查询刚添加的权限
        new_permissions = db.query(Permission).all()
        for perm in new_permissions:
            menu_id = perm.menu_id or ''
            description = perm.description or ''
            print(f'{perm.id:<5} {perm.name:<20} {perm.code:<30} {menu_id:<8} {description:<30}')
        
        print('-' * 100)
    
finally:
    # 关闭会话
    db.close()