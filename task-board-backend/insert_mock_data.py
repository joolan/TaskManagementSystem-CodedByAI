import sqlite3
from datetime import datetime, timedelta
import json

# Database connection
conn = sqlite3.connect('task_board.db')
cursor = conn.cursor()

# Helper function to execute SQL with error handling
def execute_sql(sql, params=None):
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        return True
    except Exception as e:
        print(f"Error executing SQL: {e}")
        print(f"SQL: {sql}")
        if params:
            print(f"Params: {params}")
        conn.rollback()
        return False

# Create tables if they don't exist
def create_tables():
    # Create users table if it doesn't exist
    execute_sql("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login_at DATETIME,
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until DATETIME
        )
    """)
    
    # Create statuses table if it doesn't exist
    execute_sql("""
        CREATE TABLE IF NOT EXISTS statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            order_index INTEGER NOT NULL,
            color TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create tags table if it doesn't exist
    execute_sql("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            color TEXT NOT NULL DEFAULT '#60a5fa',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create tasks table if it doesn't exist
    execute_sql("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status_id INTEGER NOT NULL,
            assignee_id INTEGER,
            priority TEXT NOT NULL,
            due_date DATETIME,
            actual_start_date DATETIME,
            actual_completion_date DATETIME,
            estimated_hours REAL,
            actual_hours REAL,
            created_by INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (status_id) REFERENCES statuses (id),
            FOREIGN KEY (assignee_id) REFERENCES users (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    """)
    
    # Create task_tags table if it doesn't exist
    execute_sql("""
        CREATE TABLE IF NOT EXISTS task_tags (
            task_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (task_id, tag_id),
            FOREIGN KEY (task_id) REFERENCES tasks (id),
            FOREIGN KEY (tag_id) REFERENCES tags (id)
        )
    """)
    
    # Create task_logs table if it doesn't exist
    execute_sql("""
        CREATE TABLE IF NOT EXISTS task_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create task_assignees table if it doesn't exist
    execute_sql("""
        CREATE TABLE IF NOT EXISTS task_assignees (
            task_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (task_id, user_id),
            FOREIGN KEY (task_id) REFERENCES tasks (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)

# Insert mock users
def insert_users():
    # Check if users already exist
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        print("Users already exist, skipping...")
        return
    
    # Import passlib to generate proper password hashes
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    
    # Password hashing function (same as in auth.py)
    def get_password_hash(password):
        if len(password) > 72:
            password = password[:72]
        return pwd_context.hash(password)
    
    users = [
        {
            "username": "admin",
            "name": "管理员",
            "email": "admin@example.com",
            "password": get_password_hash("admin123"),  # admin123
            "role": "admin",
            "created_at": (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S'),
            "last_login_at": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            "username": "frontend",
            "name": "前端开发",
            "email": "frontend@example.com",
            "password": get_password_hash("admin123"),  # admin123
            "role": "pm",
            "created_at": (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d %H:%M:%S'),
            "last_login_at": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            "username": "backend",
            "name": "后端开发",
            "email": "backend@example.com",
            "password": get_password_hash("admin123"),  # admin123
            "role": "pm",
            "created_at": (datetime.now() - timedelta(days=9)).strftime('%Y-%m-%d %H:%M:%S'),
            "last_login_at": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    for user in users:
        execute_sql(
            "INSERT INTO users (username, name, email, password, role, created_at, last_login_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user["username"], user["name"], user["email"], user["password"], user["role"], user["created_at"], user["last_login_at"])
        )
    
    print("Inserted mock users")

# Insert mock statuses
def insert_statuses():
    # Check if statuses already exist
    cursor.execute("SELECT COUNT(*) FROM statuses")
    if cursor.fetchone()[0] > 0:
        print("Statuses already exist, skipping...")
        return
    
    statuses = [
        {"name": "待办", "order_index": 1, "color": "#94a3b8"},
        {"name": "进行中", "order_index": 2, "color": "#3b82f6"},
        {"name": "已完成", "order_index": 3, "color": "#10b981"},
        {"name": "已暂停", "order_index": 4, "color": "#f59e0b"},
        {"name": "已取消", "order_index": 5, "color": "#ef4444"}
    ]
    
    for status in statuses:
        execute_sql(
            "INSERT INTO statuses (name, order_index, color) VALUES (?, ?, ?)",
            (status["name"], status["order_index"], status["color"])
        )
    
    print("Inserted mock statuses")

# Insert mock tags
def insert_tags():
    # Check if tags already exist
    cursor.execute("SELECT COUNT(*) FROM tags")
    if cursor.fetchone()[0] > 0:
        print("Tags already exist, skipping...")
        return
    
    tags = [
        {"name": "前端", "color": "#60a5fa"},
        {"name": "后端", "color": "#10b981"},
        {"name": "UI/UX", "color": "#f472b6"},
        {"name": "测试", "color": "#fbbf24"},
        {"name": "优化", "color": "#a78bfa"},
        {"name": "文档", "color": "#6ee7b7"}
    ]
    
    for tag in tags:
        execute_sql(
            "INSERT INTO tags (name, color, created_at) VALUES (?, ?, ?)",
            (tag["name"], tag["color"], datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
    
    print("Inserted mock tags")

# Insert mock tasks
def insert_tasks():
    # Check if tasks already exist
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] > 0:
        print("Tasks already exist, skipping...")
        return
    
    # Mock tasks data
    tasks = [
        # 待办状态任务
        {
            "title": "设计项目首页UI界面",
            "description": "根据产品需求文档设计项目首页的UI界面，包括响应式布局和交互效果",
            "status_id": 1,
            "assignee_id": 2,
            "priority": "high",
            "due_date": (datetime.now() + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
            "estimated_hours": 8,
            "created_by": 1,
            "created_at": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            "tag_ids": [1, 3]
        },
        {
            "title": "实现用户注册功能",
            "description": "开发用户注册模块，包括表单验证、密码加密和邮箱验证",
            "status_id": 1,
            "assignee_id": 3,
            "priority": "medium",
            "due_date": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
            "estimated_hours": 10,
            "created_by": 1,
            "created_at": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            "tag_ids": [2]
        },
        {
            "title": "搭建项目数据库结构",
            "description": "设计并实现项目的数据库表结构，包括用户、任务、标签等表",
            "status_id": 1,
            "assignee_id": 3,
            "priority": "high",
            "due_date": (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            "estimated_hours": 12,
            "created_by": 1,
            "created_at": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            "tag_ids": [2]
        },
        # 进行中状态任务
        {
            "title": "开发项目API接口",
            "description": "实现项目所需的RESTful API接口，包括用户、任务、标签等资源的CRUD操作",
            "status_id": 2,
            "assignee_id": 3,
            "priority": "high",
            "due_date": (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S'),
            "actual_start_date": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            "estimated_hours": 20,
            "actual_hours": 8,
            "created_by": 1,
            "created_at": (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            "tag_ids": [2]
        },
        {
            "title": "开发任务管理界面",
            "description": "实现任务管理模块的前端界面，包括任务列表、创建、编辑、删除等功能",
            "status_id": 2,
            "assignee_id": 2,
            "priority": "medium",
            "due_date": (datetime.now() + timedelta(days=6)).strftime('%Y-%m-%d %H:%M:%S'),
            "actual_start_date": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            "estimated_hours": 16,
            "actual_hours": 6,
            "created_by": 1,
            "created_at": (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            "tag_ids": [1]
        },
        # 已完成状态任务
        {
            "title": "项目初始化配置",
            "description": "初始化项目结构，配置开发环境，安装必要的依赖包",
            "status_id": 3,
            "assignee_id": 1,
            "priority": "high",
            "due_date": (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'),
            "actual_start_date": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
            "actual_completion_date": (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d %H:%M:%S'),
            "estimated_hours": 8,
            "actual_hours": 6,
            "created_by": 1,
            "created_at": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d %H:%M:%S'),
            "tag_ids": [1, 2]
        },
        # 已暂停状态任务
        {
            "title": "开发用户个人中心",
            "description": "实现用户个人中心页面，包括个人信息管理、密码修改、头像上传等功能",
            "status_id": 4,
            "assignee_id": 2,
            "priority": "medium",
            "due_date": (datetime.now() + timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S'),
            "actual_start_date": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            "estimated_hours": 16,
            "actual_hours": 4,
            "created_by": 1,
            "created_at": (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            "tag_ids": [1]
        },
        # 已取消状态任务
        {
            "title": "开发移动端适配",
            "description": "为项目添加移动端适配，确保在手机和平板设备上正常显示",
            "status_id": 5,
            "assignee_id": 2,
            "priority": "low",
            "due_date": (datetime.now() + timedelta(days=12)).strftime('%Y-%m-%d %H:%M:%S'),
            "estimated_hours": 20,
            "created_by": 1,
            "created_at": (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            "tag_ids": [1, 3]
        }
    ]
    
    # Add more tasks to reach 30
    task_titles = [
        "实现任务搜索功能",
        "开发标签管理功能",
        "实现任务提醒功能",
        "设计任务详情页",
        "开发评论功能",
        "实现任务附件功能",
        "开发用户角色权限系统",
        "搭建项目版本控制系统",
        "配置项目CI/CD流程",
        "开发任务导出功能",
        "开发任务甘特图视图",
        "实现任务批量操作功能",
        "开发用户通知系统",
        "实现任务模板功能",
        "开发任务依赖关系功能",
        "优化任务加载性能",
        "编写项目技术文档",
        "实现任务归档功能",
        "开发任务统计报表",
        "优化数据库查询性能",
        "实现任务评论通知",
        "开发任务进度跟踪功能"
    ]
    
    descriptions = [
        "开发任务搜索功能，支持按标题、描述、标签等条件搜索",
        "实现标签的创建、编辑、删除等管理功能",
        "开发任务提醒功能，包括邮件通知、系统消息等",
        "设计任务详情页面，包括任务信息、评论、附件等功能",
        "实现任务评论功能，支持用户对任务进行评论和回复",
        "开发任务附件功能，支持上传、下载、预览附件",
        "实现基于角色的权限控制系统，包括管理员、普通用户等角色",
        "搭建Git版本控制系统，配置代码仓库，设置分支管理策略",
        "配置持续集成和持续部署流程，实现自动构建、测试、部署",
        "实现任务导出功能，支持导出为Excel、CSV等格式",
        "实现任务甘特图视图，直观展示任务的时间安排和依赖关系",
        "开发任务批量操作功能，支持批量修改状态、优先级、标签等",
        "实现用户通知系统，包括任务状态变更、评论回复等通知",
        "开发任务模板功能，支持创建和使用任务模板",
        "实现任务依赖关系功能，支持设置任务之间的依赖关系",
        "优化任务列表和详情页面的加载性能，减少加载时间",
        "编写详细的项目技术文档，包括架构设计、API文档、部署指南等",
        "实现任务归档功能，支持将已完成的任务归档",
        "开发任务统计报表，包括任务完成率、用户工作量等统计",
        "优化数据库查询性能，提高任务列表加载速度",
        "实现任务评论通知功能，当有新评论时通知相关用户",
        "开发任务进度跟踪功能，支持记录任务的实际进度"
    ]
    
    status_ids = [1, 2, 3, 4, 5] * 5
    assignee_ids = [2, 3, 1, 2, 3] * 5
    priorities = ["high", "medium", "low", "medium", "high"] * 5
    tag_ids_list = [[1], [2], [3], [1, 3], [2, 4], [5], [6], [1, 5], [2, 6], [3, 4]] * 3
    
    for i in range(len(task_titles)):
        task = {
            "title": task_titles[i],
            "description": descriptions[i],
            "status_id": status_ids[i % len(status_ids)],
            "assignee_id": assignee_ids[i % len(assignee_ids)],
            "priority": priorities[i % len(priorities)],
            "due_date": (datetime.now() + timedelta(days=5 + i)).strftime('%Y-%m-%d %H:%M:%S'),
            "estimated_hours": 8 + (i % 4),
            "created_by": 1,
            "created_at": (datetime.now() - timedelta(days=2 + (i % 3))).strftime('%Y-%m-%d %H:%M:%S'),
            "tag_ids": tag_ids_list[i % len(tag_ids_list)]
        }
        
        # Add actual start and completion dates for some tasks
        if task["status_id"] in [2, 3, 4]:
            task["actual_start_date"] = (datetime.now() - timedelta(days=1 + (i % 2))).strftime('%Y-%m-%d %H:%M:%S')
            task["actual_hours"] = 4 + (i % 4)
            
        if task["status_id"] == 3:
            task["actual_completion_date"] = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
            task["updated_at"] = task["actual_completion_date"]
        elif task["status_id"] in [2, 4]:
            task["updated_at"] = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            task["updated_at"] = task["created_at"]
        
        tasks.append(task)
    
    # Insert tasks and their tags
    for task in tasks:
        # Insert task
        sql = """
            INSERT INTO tasks (title, description, status_id, assignee_id, priority, due_date, 
                              actual_start_date, actual_completion_date, estimated_hours, actual_hours, 
                              created_by, created_at, updated_at) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            task["title"],
            task["description"],
            task["status_id"],
            task["assignee_id"],
            task["priority"],
            task.get("due_date"),
            task.get("actual_start_date"),
            task.get("actual_completion_date"),
            task.get("estimated_hours"),
            task.get("actual_hours"),
            task["created_by"],
            task["created_at"],
            task.get("updated_at", task["created_at"])
        )
        
        if execute_sql(sql, params):
            # Get the inserted task ID
            task_id = cursor.lastrowid
            
            # Insert task tags
            if "tag_ids" in task:
                for tag_id in task["tag_ids"]:
                    execute_sql(
                        "INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)",
                        (task_id, tag_id)
                    )
                
            # Insert multiple assignees if needed
            if "assignee_id" in task and task["assignee_id"]:
                execute_sql(
                    "INSERT INTO task_assignees (task_id, user_id) VALUES (?, ?)",
                    (task_id, task["assignee_id"])
                )
    
    print(f"Inserted {len(tasks)} mock tasks")

# Clear existing data
def clear_data():
    print("Clearing existing data...")
    
    # Clear task_assignees table
    execute_sql("DELETE FROM task_assignees")
    
    # Clear task_tags table
    execute_sql("DELETE FROM task_tags")
    
    # Clear task_logs table
    execute_sql("DELETE FROM task_logs")
    
    # Clear tasks table
    execute_sql("DELETE FROM tasks")
    
    # Clear tags table
    execute_sql("DELETE FROM tags")
    
    # Clear statuses table
    execute_sql("DELETE FROM statuses")
    
    # Clear users table
    execute_sql("DELETE FROM users")
    
    # Reset auto-increment counters
    execute_sql("DELETE FROM sqlite_sequence WHERE name='users'")
    execute_sql("DELETE FROM sqlite_sequence WHERE name='statuses'")
    execute_sql("DELETE FROM sqlite_sequence WHERE name='tags'")
    execute_sql("DELETE FROM sqlite_sequence WHERE name='tasks'")
    execute_sql("DELETE FROM sqlite_sequence WHERE name='task_logs'")
    
    print("Data cleared successfully!")

# Main function
def main():
    print("Creating tables...")
    create_tables()
    
    # Clear existing data
    clear_data()
    
    print("Inserting mock users...")
    insert_users()
    
    print("Inserting mock statuses...")
    insert_statuses()
    
    print("Inserting mock tags...")
    insert_tags()
    
    print("Inserting mock tasks...")
    insert_tasks()
    
    print("Mock data insertion completed!")

if __name__ == "__main__":
    main()
    conn.close()
