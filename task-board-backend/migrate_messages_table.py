from db import engine
from sqlalchemy import text

def migrate_messages_table():
    """Migrate messages table to use redirect_path instead of task_id and release_id"""
    
    with engine.connect() as conn:
        # 检查当前表结构
        result = conn.execute(text("PRAGMA table_info(messages)"))
        columns = [row[1] for row in result]
        
        print("当前messages表列:", columns)
        
        # 1. 添加redirect_path列（如果不存在）
        if 'redirect_path' not in columns:
            conn.execute(text("ALTER TABLE messages ADD COLUMN redirect_path VARCHAR"))
            conn.commit()
            print("成功添加redirect_path列")
        else:
            print("redirect_path列已存在")
        
        # 2. 迁移数据：将task_id转换为redirect_path
        if 'task_id' in columns:
            # 更新任务消息的redirect_path
            conn.execute(text("""
                UPDATE messages 
                SET redirect_path = '/task/' || task_id 
                WHERE task_id IS NOT NULL AND (redirect_path IS NULL OR redirect_path = '')
            """))
            conn.commit()
            print("已迁移任务消息的跳转路径")
        
        # 3. 迁移数据：将release_id转换为redirect_path
        if 'release_id' in columns:
            # 更新发版消息的redirect_path
            conn.execute(text("""
                UPDATE messages 
                SET redirect_path = '/release/' || release_id 
                WHERE release_id IS NOT NULL AND (redirect_path IS NULL OR redirect_path = '')
            """))
            conn.commit()
            print("已迁移发版消息的跳转路径")
        
        # 注意：SQLite不支持DROP COLUMN，所以我们保留旧列但不使用它们
        # 新的代码将只使用redirect_path字段
        
        print("数据库迁移完成")

if __name__ == "__main__":
    migrate_messages_table()
