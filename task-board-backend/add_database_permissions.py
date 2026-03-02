import sqlite3

# 数据库文件路径
DB_PATH = 'task_board.db'

# 要添加的权限
new_permissions = [
    ('database:list_backups', '数据库备份列表查看', 1),
    ('database:delete_backup', '数据库备份删除', 1)
]

def add_permissions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查权限表是否存在
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                menu_id INTEGER,
                FOREIGN KEY (menu_id) REFERENCES menus(id)
            )
        """)
        
        # 检查并添加权限
        for code, name, menu_id in new_permissions:
            # 检查权限是否已存在
            cursor.execute("SELECT id FROM permissions WHERE code = ?", (code,))
            existing = cursor.fetchone()
            
            if not existing:
                # 添加新权限
                cursor.execute(
                    "INSERT INTO permissions (code, name, menu_id) VALUES (?, ?, ?)",
                    (code, name, menu_id)
                )
                print(f"添加权限: {code} - {name}")
            else:
                print(f"权限已存在: {code}")
        
        # 提交更改
        conn.commit()
        print("权限添加完成")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_permissions()
