import sqlite3

# 连接到数据库
conn = sqlite3.connect('task_board.db')
cursor = conn.cursor()

try:
    # 检查并添加 is_anonymous 字段到 comments 表
    cursor.execute("PRAGMA table_info(comments)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'is_anonymous' not in columns:
        cursor.execute("ALTER TABLE comments ADD COLUMN is_anonymous INTEGER DEFAULT 0")
        print("Added is_anonymous column to comments table")
    else:
        print("is_anonymous column already exists in comments table")
    
    if 'pinned_at' not in columns:
        cursor.execute("ALTER TABLE comments ADD COLUMN pinned_at TIMESTAMP")
        print("Added pinned_at column to comments table")
    else:
        print("pinned_at column already exists in comments table")
    
    # 创建 release_tags 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS release_tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        color TEXT NOT NULL DEFAULT '#60a5fa',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("Created release_tags table if not exists")
    
    # 创建 releases 表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS releases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        planned_release_date TIMESTAMP,
        actual_release_date TIMESTAMP,
        created_by INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (created_by) REFERENCES users (id)
    )
    """)
    print("Created releases table if not exists")
    
    # 创建 release_release_tags 关联表（多对多关系）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS release_release_tags (
        release_id INTEGER,
        release_tag_id INTEGER,
        PRIMARY KEY (release_id, release_tag_id),
        FOREIGN KEY (release_id) REFERENCES releases (id) ON DELETE CASCADE,
        FOREIGN KEY (release_tag_id) REFERENCES release_tags (id) ON DELETE CASCADE
    )
    """)
    print("Created release_release_tags table if not exists")
    
    # 在 tasks 表中添加 release_id 字段
    cursor.execute("PRAGMA table_info(tasks)")
    task_columns = [column[1] for column in cursor.fetchall()]
    
    if 'release_id' not in task_columns:
        cursor.execute("ALTER TABLE tasks ADD COLUMN release_id INTEGER")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_release_id ON tasks (release_id)")
        print("Added release_id column to tasks table")
    else:
        print("release_id column already exists in tasks table")
    
    # 提交更改
    conn.commit()
    print("Database updated successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    # 关闭连接
    conn.close()
