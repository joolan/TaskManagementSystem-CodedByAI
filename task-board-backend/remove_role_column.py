import sqlite3

# 数据库文件路径
DB_PATH = 'task_board.db'

def remove_role_column():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查users表是否存在role字段
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        role_column_exists = any(col[1] == 'role' for col in columns)
        
        if role_column_exists:
            # 由于SQLite不支持直接DROP COLUMN，我们需要重建表
            # 1. 创建临时表
            cursor.execute("""
                CREATE TABLE users_temp AS
                SELECT id, username, password, name, email, created_at, last_login_at, failed_login_attempts, locked_until
                FROM users
            """)
            
            # 2. 删除原表
            cursor.execute("DROP TABLE users")
            
            # 3. 重命名临时表为原表名
            cursor.execute("ALTER TABLE users_temp RENAME TO users")
            
            # 4. 重新创建索引
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username)")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users(id)")
            
            print("成功从users表中删除role字段")
        else:
            print("users表中不存在role字段")
        
        # 提交更改
        conn.commit()
        
    except Exception as e:
        print(f"错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    remove_role_column()
