from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, Date, DateTime, Float, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = "sqlite:///./task_board.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)  # 最后登录时间
    failed_login_attempts = Column(Integer, default=0)  # 密码错误次数
    locked_until = Column(DateTime, nullable=True)  # 锁定截止时间

    # Relationships
    tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by")
    comments = relationship("Comment", back_populates="user")
    attachments = relationship("Attachment", back_populates="user")
    login_logs = relationship("LoginLog", back_populates="user")
    user_messages = relationship("UserMessage", back_populates="user")


# Association table for task assignees (many-to-many)
task_assignees = Table(
    'task_assignees',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
)

# Association table for task tags (many-to-many)
task_tags = Table(
    'task_tags',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# ReleaseTag model
class ReleaseTag(Base):
    __tablename__ = "release_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, nullable=False, default="#60a5fa")  # 默认蓝色
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    releases = relationship("Release", secondary="release_release_tags", back_populates="tags")


# RequirementTag model
class RequirementTag(Base):
    __tablename__ = "requirement_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, nullable=False, default="#60a5fa")  # 默认蓝色
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    requirements = relationship("Requirement", back_populates="tag")

# Release model
class Release(Base):
    __tablename__ = "releases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # 发版主题
    description = Column(Text)  # 发版详情
    status = Column(String, nullable=False)  # 计划中、已发版、延期中、已作废
    planned_release_date = Column(DateTime)  # 预计发版时间
    actual_release_date = Column(DateTime)  # 实际发版时间
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", backref="created_releases")
    tasks = relationship("Task", back_populates="release")
    tags = relationship("ReleaseTag", secondary="release_release_tags", back_populates="releases")
    follows = relationship("ReleaseFollow", back_populates="release", cascade="all, delete-orphan")

# ReleaseFollow model
class ReleaseFollow(Base):
    __tablename__ = "release_follows"

    id = Column(Integer, primary_key=True, index=True)
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    release = relationship("Release", back_populates="follows")
    user = relationship("User", backref="followed_releases")

# TaskFollow model
class TaskFollow(Base):
    __tablename__ = "task_follows"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="follows")
    user = relationship("User", backref="followed_tasks")

# Association table for release tags (many-to-many)
release_release_tags = Table(
    'release_release_tags',
    Base.metadata,
    Column('release_id', Integer, ForeignKey('releases.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('release_tags.id'), primary_key=True)
)


class Status(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    order_index = Column(Integer, nullable=False)
    color = Column(String, nullable=False)

    # Relationships
    tasks = relationship("Task", back_populates="status")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    color = Column(String, nullable=False, default="#60a5fa")  # 默认蓝色
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tasks = relationship("Task", secondary=task_tags, back_populates="tags")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status_id = Column(Integer, ForeignKey("statuses.id"))
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 保留单个负责人字段用于兼容
    priority = Column(String, nullable=False)  # high, medium, low
    due_date = Column(DateTime)
    actual_start_date = Column(DateTime)  # 实际开始日期
    actual_completion_date = Column(DateTime)  # 实际完成日期
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    created_by = Column(Integer, ForeignKey("users.id"))
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=True)  # 关联发版记录
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    status = relationship("Status", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks", foreign_keys=[assignee_id])
    assignees = relationship("User", secondary="task_assignees", backref="assigned_tasks")
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by])
    release = relationship("Release", back_populates="tasks")
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="task", cascade="all, delete-orphan")
    logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=task_tags, back_populates="tasks")
    follows = relationship("TaskFollow", back_populates="task", cascade="all, delete-orphan")
    hours = relationship("TaskHour", back_populates="task", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    is_anonymous = Column(Integer, default=0)
    pinned_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="comments")
    user = relationship("User", back_populates="comments")
    attachments = relationship("Attachment", back_populates="comment", cascade="all, delete-orphan")


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # 关联到评论
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="attachments")
    user = relationship("User", back_populates="attachments")
    comment = relationship("Comment", back_populates="attachments")


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LoginLog(Base):
    __tablename__ = "login_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String, nullable=False)
    user_agent = Column(Text, nullable=False)
    login_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False)  # success, failed

    # Relationships
    user = relationship("User", back_populates="login_logs")


class TaskLog(Base):
    __tablename__ = "task_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String, nullable=False)  # create, update, status_change, etc.
    title = Column(String, nullable=False)  # 日志标题
    content = Column(Text, nullable=False)  # 变更详情
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="logs")
    user = relationship("User", backref="task_logs")


class TaskHour(Base):
    __tablename__ = "task_hours"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hours = Column(Float, nullable=False)
    remark = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    task = relationship("Task", back_populates="hours")
    user = relationship("User", foreign_keys=[user_id])
    creator = relationship("User", foreign_keys=[created_by])


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    message_type = Column(String, nullable=False)  # task_message, system_message, defect_message, etc.
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    redirect_path = Column(String, nullable=True)  # 前端跳转路径，可以是内部路径或完整URL
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("User")
    user_messages = relationship("UserMessage", back_populates="message", cascade="all, delete-orphan")


class UserMessage(Base):
    __tablename__ = "user_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message_id = Column(Integer, ForeignKey("messages.id"))
    is_read = Column(Integer, default=0)  # 0=unread, 1=read
    read_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="user_messages")
    message = relationship("Message", back_populates="user_messages")


# Requirement model
class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(Integer, primary_key=True, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String, nullable=False)  # 需求来源
    name = Column(String, nullable=False)  # 需求名称
    tag_id = Column(Integer, ForeignKey("requirement_tags.id"), nullable=True)  # 需求标签
    description = Column(Text, nullable=False)  # 需求描述
    status = Column(String, nullable=False, default="草稿")  # 需求状态：草稿、待评审、已确认、已作废、已转任务
    priority = Column(String, nullable=False, default="中")  # 需求优先级：高、中、低
    planned_completion_date = Column(DateTime, nullable=True)  # 计划完成日期
    actual_completion_date = Column(DateTime, nullable=True)  # 实际完成日期
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # 转任务的任务ID
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", backref="created_requirements")
    tag = relationship("RequirementTag", back_populates="requirements")
    task = relationship("Task")


# Memo model
class Memo(Base):
    __tablename__ = "memos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # 备忘录名称
    content = Column(Text)  # 备忘录内容
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # 创建者
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", backref="created_memos")


# UserSession model
class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, nullable=False, unique=True, index=True)  # JWT token
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    login_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 1=active, 0=inactive

    # Relationships
    user = relationship("User", backref="sessions")


# Defect model
class Defect(Base):
    __tablename__ = "defects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False, default="草稿")
    release_id = Column(Integer, ForeignKey("releases.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by], backref="created_defects")
    assignee = relationship("User", foreign_keys=[assignee_id], backref="assigned_defects")
    release = relationship("Release", backref="defects")


# Menu model
class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("menus.id"), nullable=True)
    path = Column(String, nullable=True)  # 路由路径
    component = Column(String, nullable=True)  # 组件路径
    icon = Column(String, nullable=True)  # 菜单图标
    order_index = Column(Integer, default=0)  # 排序
    type = Column(String, nullable=False, default="menu")  # menu: 菜单, external: 外部链接, iframe: 内嵌iframe
    external_url = Column(String, nullable=True)  # 外部链接URL
    target = Column(String, nullable=True)  # 打开方式: _blank, _self
    status = Column(Integer, default=1)  # 1: 启用, 0: 禁用
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("Menu", remote_side=[id], backref="children")


# Role model
class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    status = Column(Integer, default=1)  # 1: 启用, 0: 禁用
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Permission model
class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    code = Column(String, nullable=False, unique=True)  # 权限编码
    description = Column(String, nullable=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=True)  # 关联的菜单
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# User-Role association table
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Role-Menu association table
role_menus = Table(
    'role_menus',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('menu_id', Integer, ForeignKey('menus.id'), primary_key=True)
)

# Role-Permission association table
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# User-Permission association table (for extra permissions)
user_permissions = Table(
    'user_permissions',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# User-Menu association table (for extra menus)
user_menus = Table(
    'user_menus',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('menu_id', Integer, ForeignKey('menus.id'), primary_key=True)
)

# Update User model relationships
User.roles = relationship("Role", secondary=user_roles, backref="users")
User.extra_permissions = relationship("Permission", secondary=user_permissions, backref="users")
User.extra_menus = relationship("Menu", secondary=user_menus, backref="users")
Role.menus = relationship("Menu", secondary=role_menus, backref="roles")
Role.permissions = relationship("Permission", secondary=role_permissions, backref="roles")


def update_db_structure():
    """Update database structure to include new columns"""
    from sqlalchemy import text
    db = SessionLocal()
    try:
        # Check if tasks table has actual_start_date column
        result = db.execute(text("PRAGMA table_info(tasks)")).fetchall()
        columns = [column[1] for column in result]
        
        # Add actual_start_date column if it doesn't exist
        if 'actual_start_date' not in columns:
            db.execute(text("ALTER TABLE tasks ADD COLUMN actual_start_date DATETIME"))
            print("Added actual_start_date column to tasks table")
        
        # Add actual_completion_date column if it doesn't exist
        if 'actual_completion_date' not in columns:
            db.execute(text("ALTER TABLE tasks ADD COLUMN actual_completion_date DATETIME"))
            print("Added actual_completion_date column to tasks table")
        
        # Check if users table has failed_login_attempts column
        result = db.execute(text("PRAGMA table_info(users)")).fetchall()
        user_columns = [column[1] for column in result]
        
        # Add failed_login_attempts column if it doesn't exist
        if 'failed_login_attempts' not in user_columns:
            db.execute(text("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER DEFAULT 0"))
            print("Added failed_login_attempts column to users table")
        
        # Add locked_until column if it doesn't exist
        if 'locked_until' not in user_columns:
            db.execute(text("ALTER TABLE users ADD COLUMN locked_until DATETIME"))
            print("Added locked_until column to users table")
        
        # Create tags table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='tags'"))
        if not result.fetchone():
            db.execute(text("""
                CREATE TABLE tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT NOT NULL DEFAULT '#60a5fa',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created tags table")
        
        # Create task_tags table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='task_tags'"))
        if not result.fetchone():
            db.execute(text("""
                CREATE TABLE task_tags (
                    task_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (task_id, tag_id),
                    FOREIGN KEY (task_id) REFERENCES tasks (id),
                    FOREIGN KEY (tag_id) REFERENCES tags (id)
                )
            """))
            print("Created task_tags table")
        
        # Create task_logs table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='task_logs'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE task_logs (
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
            """))
            print("Created task_logs table")
        
        # Create messages table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    task_id INTEGER,
                    release_id INTEGER,
                    created_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id),
                    FOREIGN KEY (release_id) REFERENCES releases (id),
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            """))
            print("Created messages table")
        else:
            # Check if messages table has release_id column
            result = db.execute(text("PRAGMA table_info(messages)")).fetchall()
            message_columns = [column[1] for column in result]
            if 'release_id' not in message_columns:
                db.execute(text("ALTER TABLE messages ADD COLUMN release_id INTEGER REFERENCES releases (id)"))
                print("Added release_id column to messages table")
        
        # Create user_messages table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_messages'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE user_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message_id INTEGER NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    read_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (message_id) REFERENCES messages (id)
                )
            """))
            print("Created user_messages table")
        
        # Create release_tags table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='release_tags'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE release_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT NOT NULL DEFAULT '#60a5fa',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created release_tags table")
        
        # Create releases table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='releases'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE releases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT NOT NULL,
                    planned_release_date DATETIME,
                    actual_release_date DATETIME,
                    created_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            """))
            print("Created releases table")
        
        # Add release_id column to tasks table if it doesn't exist
        result = db.execute(text("PRAGMA table_info(tasks)")).fetchall()
        task_columns = [column[1] for column in result]
        if 'release_id' not in task_columns:
            db.execute(text("ALTER TABLE tasks ADD COLUMN release_id INTEGER REFERENCES releases (id)"))
            print("Added release_id column to tasks table")
        
        # Create release_release_tags table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='release_release_tags'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE release_release_tags (
                    release_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (release_id, tag_id),
                    FOREIGN KEY (release_id) REFERENCES releases (id),
                    FOREIGN KEY (tag_id) REFERENCES release_tags (id)
                )
            """))
            print("Created release_release_tags table")
        
        # Create release_follows table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='release_follows'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE release_follows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    release_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (release_id) REFERENCES releases (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(release_id, user_id)
                )
            """))
            print("Created release_follows table")
        
        # Create task_follows table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='task_follows'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE task_follows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(task_id, user_id)
                )
            """))
            print("Created task_follows table")
        
        # Create requirement_tags table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='requirement_tags'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE requirement_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    color TEXT NOT NULL DEFAULT '#60a5fa',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created requirement_tags table")
        
        # Create requirements table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='requirements'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE requirements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    source TEXT NOT NULL,
                    name TEXT NOT NULL,
                    tag_id INTEGER,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT '草稿',
                    priority TEXT NOT NULL DEFAULT '中',
                    planned_completion_date DATETIME,
                    actual_completion_date DATETIME,
                    task_id INTEGER,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id),
                    FOREIGN KEY (tag_id) REFERENCES requirement_tags (id),
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )
            """))
            print("Created requirements table")
        
        # Create memos table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='memos'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE memos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    content TEXT,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            """))
            print("Created memos table")
        
        # Create user_sessions table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_sessions'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    ip_address TEXT,
                    user_agent TEXT,
                    login_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            db.execute(text("CREATE INDEX idx_user_sessions_token ON user_sessions(token)"))
            db.execute(text("CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id)"))
            print("Created user_sessions table")
        
        # Create task_hours table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='task_hours'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE task_hours (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    hours REAL NOT NULL,
                    remark TEXT,
                    created_by INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks (id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (created_by) REFERENCES users (id)
                )
            """))
            print("Created task_hours table")
        
        # Create menus table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='menus'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE menus (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    parent_id INTEGER REFERENCES menus (id),
                    path TEXT,
                    component TEXT,
                    icon TEXT,
                    order_index INTEGER DEFAULT 0,
                    type TEXT NOT NULL DEFAULT 'menu',
                    external_url TEXT,
                    target TEXT,
                    status INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created menus table")
        
        # Create roles table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='roles'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    status INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created roles table")
        
        # Create permissions table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='permissions'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    code TEXT NOT NULL UNIQUE,
                    description TEXT,
                    menu_id INTEGER REFERENCES menus (id),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("Created permissions table")
        
        # Create user_roles table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_roles'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE user_roles (
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, role_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (role_id) REFERENCES roles (id)
                )
            """))
            print("Created user_roles table")
        
        # Create role_menus table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='role_menus'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE role_menus (
                    role_id INTEGER NOT NULL,
                    menu_id INTEGER NOT NULL,
                    PRIMARY KEY (role_id, menu_id),
                    FOREIGN KEY (role_id) REFERENCES roles (id),
                    FOREIGN KEY (menu_id) REFERENCES menus (id)
                )
            """))
            print("Created role_menus table")
        
        # Create role_permissions table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='role_permissions'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE role_permissions (
                    role_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    PRIMARY KEY (role_id, permission_id),
                    FOREIGN KEY (role_id) REFERENCES roles (id),
                    FOREIGN KEY (permission_id) REFERENCES permissions (id)
                )
            """))
            print("Created role_permissions table")
        
        # Create user_permissions table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_permissions'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE user_permissions (
                    user_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, permission_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (permission_id) REFERENCES permissions (id)
                )
            """))
            print("Created user_permissions table")
        
        # Create user_menus table if it doesn't exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user_menus'")).fetchone()
        if not result:
            db.execute(text("""
                CREATE TABLE user_menus (
                    user_id INTEGER NOT NULL,
                    menu_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, menu_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (menu_id) REFERENCES menus (id)
                )
            """))
            print("Created user_menus table")
        
        # Check if system_settings table has max_sessions_per_user setting
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='system_settings'")).fetchone()
        if result:
            setting = db.execute(text("SELECT * FROM system_settings WHERE key = 'max_sessions_per_user'")).fetchone()
            if not setting:
                db.execute(text("""
                    INSERT INTO system_settings (key, value, description) 
                    VALUES ('max_sessions_per_user', '2', '同一时间相同用户仅允许在线个数，超过限制后后登录用户会将前面最早登录用户踢下线，确保同时在线数不超过此配置')
                """))
                print("Added max_sessions_per_user setting")
        
        # Update created_at and updated_at for existing system settings
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='system_settings'")).fetchone()
        if result:
            settings = db.execute(text("SELECT id, created_at, updated_at FROM system_settings")).fetchall()
            for setting in settings:
                if setting[1] is None:  # created_at is None
                    db.execute(text("UPDATE system_settings SET created_at = CURRENT_TIMESTAMP WHERE id = :id"), {"id": setting[0]})
                if setting[2] is None:  # updated_at is None
                    db.execute(text("UPDATE system_settings SET updated_at = CURRENT_TIMESTAMP WHERE id = :id"), {"id": setting[0]})
            print("Updated created_at and updated_at for system settings")
        
        db.commit()
    except Exception as e:
        print(f"Error updating database structure: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


def init_db():
    """Initialize database with default data"""
    # Update database structure first
    update_db_structure()
    
    db = SessionLocal()
    try:
        # Check if statuses already exist
        if db.query(Status).count() == 0:
            # Create default statuses
            default_statuses = [
                Status(name="待办", order_index=1, color="#94a3b8"),
                Status(name="进行中", order_index=2, color="#3b82f6"),
                Status(name="已完成", order_index=3, color="#10b981"),
                Status(name="已暂停", order_index=4, color="#f59e0b"),
                Status(name="已取消", order_index=5, color="#ef4444")
            ]
            db.add_all(default_statuses)
            db.commit()
            print("Created default statuses")

        # Check if tags already exist
        if db.query(Tag).count() == 0:
            # Create default tags
            default_tags = [
                Tag(name="前端", color="#60a5fa"),  # 蓝色
                Tag(name="后端", color="#34d399"),  # 绿色
                Tag(name="UI/UX", color="#f472b6"),  # 粉色
                Tag(name="Bug", color="#f87171"),  # 红色
                Tag(name="优化", color="#fbbf24"),  # 黄色
                Tag(name="文档", color="#a78bfa")   # 紫色
            ]
            db.add_all(default_tags)
            db.commit()
            print("Created default tags")

        # Unlock locked admin users (unlock only if first one if multiple)
        locked_admins = db.query(User).filter(
            User.username == "admin",
            User.locked_until.isnot(None)
        ).all()
        
        if locked_admins:
            # Unlock only the first admin
            admin_to_unlock = locked_admins[0]
            admin_to_unlock.failed_login_attempts = 0
            admin_to_unlock.locked_until = None
            db.commit()
            print(f"Unlocked admin user: {admin_to_unlock.username}")

        # Create admin user (password: admin123)
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            try:
                from auth import get_password_hash
                # Ensure password length is within bcrypt limit (72 bytes)
                password = "admin123"
                if len(password) > 72:
                    password = password[:72]
                hashed_password = get_password_hash(password)
                print(f"Admin hashed password: {hashed_password}")
                
                admin_user = User(
                    username="admin",
                    password=hashed_password,
                    name="管理员",
                    email="admin@example.com"
                )
                db.add(admin_user)
                db.commit()
                db.refresh(admin_user)
                print(f"Created admin user: {admin_user.username}")
            except Exception as e:
                print(f"Error creating admin user: {e}")
                import traceback
                traceback.print_exc()
                db.rollback()

        # Create test user (password: dev123)
        dev = db.query(User).filter(User.username == "dev").first()
        if not dev:
            try:
                from auth import get_password_hash
                # Ensure password length is within bcrypt limit (72 bytes)
                password = "dev123"
                if len(password) > 72:
                    password = password[:72]
                hashed_password = get_password_hash(password)
                print(f"Dev hashed password: {hashed_password}")
                
                test_user = User(
                    username="dev",
                    password=hashed_password,
                    name="开发人员",
                    email="dev@example.com"
                )
                db.add(test_user)
                db.commit()
                db.refresh(test_user)
                print(f"Created dev user: {test_user.username}")
            except Exception as e:
                print(f"Error creating dev user: {e}")
                import traceback
                traceback.print_exc()
                db.rollback()

        # Print all users for debugging
        all_users = db.query(User).all()
        print(f"Total users: {len(all_users)}")
        for user in all_users:
            print(f"User: {user.username}, Failed attempts: {user.failed_login_attempts}, Locked until: {user.locked_until}")

        # Initialize menu structure
        if db.query(Menu).count() == 0:
            # Create menu structure
            menus = [
                # System Management (一级菜单)
                Menu(
                    name="系统管理",
                    parent_id=None,
                    path="/system",
                    icon="Setting",
                    order_index=99,
                    type="menu"
                ),
                # System Settings (二级菜单)
                Menu(
                    name="系统设置",
                    parent_id=1,
                    path="/system-settings",
                    component="SystemSettings.vue",
                    icon="Tools",
                    order_index=1,
                    type="menu"
                ),
                # Menu Management (二级菜单)
                Menu(
                    name="菜单管理",
                    parent_id=1,
                    path="/menu-management",
                    component="MenuManagement.vue",
                    icon="Menu",
                    order_index=2,
                    type="menu"
                ),
                # User Role Management (二级菜单)
                Menu(
                    name="用户角色管理",
                    parent_id=1,
                    path="/user-role-management",
                    icon="UserFilled",
                    order_index=3,
                    type="menu"
                ),
                # User Management (三级菜单)
                Menu(
                    name="用户管理",
                    parent_id=4,
                    path="/users",
                    component="Users.vue",
                    icon="User",
                    order_index=1,
                    type="menu"
                ),
                # Role Management (三级菜单)
                Menu(
                    name="角色管理",
                    parent_id=4,
                    path="/role-management",
                    component="RoleManagement.vue",
                    icon="Avatar",
                    order_index=2,
                    type="menu"
                ),
                # Demo Menu (菜单层级演示)
                Menu(
                    name="菜单层级演示",
                    parent_id=None,
                    path="/menu-demo",
                    icon="DocumentCopy",
                    order_index=100,
                    type="menu"
                ),
                # Demo Submenu 1
                Menu(
                    name="二级菜单1",
                    parent_id=7,
                    path="/menu-demo/sub1",
                    icon="Folder",
                    order_index=1,
                    type="menu"
                ),
                # Demo Submenu 2
                Menu(
                    name="二级菜单2",
                    parent_id=7,
                    path="/menu-demo/sub2",
                    icon="Folder",
                    order_index=2,
                    type="menu"
                ),
                # Demo Submenu 1-1
                Menu(
                    name="三级菜单1",
                    parent_id=8,
                    path="/menu-demo/sub1/level3",
                    component="MenuDemoPage.vue",
                    icon="Files",
                    order_index=1,
                    type="menu"
                ),
                # Existing menus
                Menu(
                    name="任务看板",
                    parent_id=None,
                    path="/board",
                    component="Board.vue",
                    icon="Grid",
                    order_index=1,
                    type="menu"
                ),
                Menu(
                    name="工作台",
                    parent_id=None,
                    path="/dashboard",
                    component="Dashboard.vue",
                    icon="HomeFilled",
                    order_index=2,
                    type="menu"
                ),
                Menu(
                    name="任务管理",
                    parent_id=None,
                    path="/tasks",
                    component="Tasks.vue",
                    icon="Document",
                    order_index=3,
                    type="menu"
                ),
                Menu(
                    name="发版管理",
                    parent_id=None,
                    path="/releases",
                    component="Releases.vue",
                    icon="Flag",
                    order_index=4,
                    type="menu"
                ),
                Menu(
                    name="需求管理",
                    parent_id=None,
                    path="/requirements",
                    component="Requirements.vue",
                    icon="List",
                    order_index=5,
                    type="menu"
                ),
                Menu(
                    name="统计分析",
                    parent_id=None,
                    path="/stats",
                    component="Stats.vue",
                    icon="DataAnalysis",
                    order_index=6,
                    type="menu"
                )
            ]
            db.add_all(menus)
            db.commit()
            print("Created menu structure")

        # Initialize roles
        if db.query(Role).count() == 0:
            # Create roles
            roles = [
                Role(
                    name="开发角色",
                    description="开发人员角色"
                ),
                Role(
                    name="游客角色",
                    description="只读权限角色"
                )
            ]
            db.add_all(roles)
            db.commit()
            print("Created roles")

        # Check if system settings already exist
        if db.query(SystemSetting).count() == 0:
            # Create default system settings
            default_settings = [
                SystemSetting(
                    key="allow_registration",
                    value="false",
                    description="是否允许用户自助注册"
                ),
                SystemSetting(
                    key="site_name",
                    value="任务看板系统",
                    description="系统名称"
                )
            ]
            db.add_all(default_settings)
            db.commit()
            print("Created default system settings")

    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()
