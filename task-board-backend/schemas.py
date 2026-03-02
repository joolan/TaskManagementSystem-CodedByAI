from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date, datetime
from typing import Optional, List


# Role schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class Role(RoleBase):
    id: int
    status: int = 1
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    username: str
    name: str
    email: EmailStr
    role: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    last_login_at: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    session_count: int = 0
    roles: List[Role] = []

    class Config:
        from_attributes = True


class UserResponse(User):
    token: Optional[str] = None
    roles: List[Role] = []


# 简化版用户schema，用于公共查询接口
class UserBasic(BaseModel):
    id: int
    username: str
    name: str

    class Config:
        from_attributes = True


# Status schemas
class StatusBase(BaseModel):
    name: str
    order_index: int
    color: str


class StatusCreate(StatusBase):
    pass


class Status(StatusBase):
    id: int

    class Config:
        from_attributes = True


# Tag schemas
class TagBase(BaseModel):
    name: str
    color: str


class TagCreate(TagBase):
    pass


class Tag(TagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Task schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status_id: int
    assignee_id: Optional[int] = None
    assignee_ids: Optional[List[int]] = None
    priority: str
    due_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    tag_ids: Optional[List[int]] = None  # 任务标签ID列表
    release_id: Optional[int] = None  # 关联的发版记录ID
    
    @field_validator('due_date', 'actual_start_date', 'actual_completion_date', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status_id: Optional[int] = None
    assignee_id: Optional[int] = None
    assignee_ids: Optional[List[int]] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    actual_start_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    tag_ids: Optional[List[int]] = None  # 任务标签ID列表
    
    @field_validator('due_date', 'actual_start_date', 'actual_completion_date', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class TaskStatusUpdate(BaseModel):
    status_id: int


class TaskAssigneeUpdate(BaseModel):
    assignee_id: int


class Task(TaskBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskWithDetails(Task):
    status: Optional[Status] = None
    assignee: Optional[User] = None
    assignees: List[User] = []
    creator: Optional[User] = None
    tags: List[Tag] = []  # 任务标签列表
    release: Optional['Release'] = None  # 关联的发版记录（使用字符串类型引用，避免循环导入）

    class Config:
        from_attributes = True


# Attachment schemas
class AttachmentBase(BaseModel):
    filename: str
    file_path: str


class AttachmentCreate(AttachmentBase):
    pass


class Attachment(AttachmentBase):
    id: int
    task_id: int
    user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AttachmentWithUser(Attachment):
    user: User


# Comment schemas
class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    attachment_ids: Optional[List[int]] = []
    is_anonymous: Optional[bool] = False


class Comment(CommentBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class CommentWithUser(BaseModel):
    id: int
    task_id: int
    user_id: Optional[int] = None
    content: str
    created_at: datetime
    user: Optional[User] = None
    attachments: List[Attachment] = []
    is_anonymous: Optional[bool] = False
    pinned_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Message schemas
class MessageBase(BaseModel):
    message_type: str
    title: str
    content: str
    redirect_path: Optional[str] = None


class MessageCreate(MessageBase):
    user_ids: List[int]  # Recipients


class Message(MessageBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserMessageBase(BaseModel):
    user_id: int
    message_id: int
    is_read: bool
    read_at: Optional[datetime] = None


class UserMessage(UserMessageBase):
    id: int
    message: Message

    class Config:
        from_attributes = True


class MessageWithStatus(BaseModel):
    id: int
    message_type: str
    title: str
    content: str
    redirect_path: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    is_read: bool
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Stats schemas
class TaskStatusStats(BaseModel):
    status_name: str
    count: int
    color: str


class UserWorkloadStats(BaseModel):
    user_id: int
    username: str
    name: str
    task_count: int
    estimated_hours: float
    actual_hours: float


class ProjectProgressStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    completion_rate: float
    overdue_tasks: int


# System Setting schemas
class SystemSettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SystemSettingCreate(SystemSettingBase):
    pass


class SystemSettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None


class SystemSetting(SystemSettingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Login Log schemas
class LoginLogBase(BaseModel):
    user_id: int
    ip_address: str
    user_agent: str
    status: str


class LoginLogCreate(LoginLogBase):
    pass


class LoginLog(LoginLogBase):
    id: int
    login_at: datetime

    class Config:
        from_attributes = True


class LoginLogWithUser(LoginLog):
    user: User


# Task Log schemas
class TaskLogBase(BaseModel):
    task_id: int
    user_id: int
    action_type: str
    title: str
    content: str


class TaskLogCreate(TaskLogBase):
    pass


class TaskLog(TaskLogBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskLogWithUser(TaskLog):
    user: User


# ReleaseTag schemas
class ReleaseTagBase(BaseModel):
    name: str
    color: str


class ReleaseTagCreate(ReleaseTagBase):
    pass


class ReleaseTag(ReleaseTagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Release schemas
class ReleaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    planned_release_date: Optional[datetime] = None
    actual_release_date: Optional[datetime] = None
    task_ids: Optional[List[int]] = None  # 关联的任务ID列表
    tag_ids: Optional[List[int]] = None  # 发版标签ID列表
    
    @field_validator('planned_release_date', 'actual_release_date', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class ReleaseCreate(ReleaseBase):
    pass


class ReleaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    planned_release_date: Optional[datetime] = None
    actual_release_date: Optional[datetime] = None
    task_ids: Optional[List[int]] = None  # 关联的任务ID列表
    tag_ids: Optional[List[int]] = None  # 发版标签ID列表
    
    @field_validator('planned_release_date', 'actual_release_date', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class Release(ReleaseBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReleaseWithDetails(Release):
    creator: User
    tasks: List[TaskWithDetails] = []
    tags: List[ReleaseTag] = []  # 发版标签列表
    defect_count: int = 0  # 版本缺陷数


# RequirementTag schemas
class RequirementTagBase(BaseModel):
    name: str
    color: str


class RequirementTagCreate(RequirementTagBase):
    pass


class RequirementTag(RequirementTagBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Requirement schemas
class RequirementBase(BaseModel):
    source: str
    name: str
    tag_id: Optional[int] = None
    description: str
    status: str
    priority: str
    planned_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    
    @field_validator('planned_completion_date', 'actual_completion_date', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class RequirementCreate(RequirementBase):
    pass


class RequirementUpdate(BaseModel):
    source: Optional[str] = None
    name: Optional[str] = None
    tag_id: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    planned_completion_date: Optional[datetime] = None
    actual_completion_date: Optional[datetime] = None
    
    @field_validator('planned_completion_date', 'actual_completion_date', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '':
            return None
        return v


class Requirement(RequirementBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    task_id: Optional[int] = None

    class Config:
        from_attributes = True


class RequirementWithDetails(Requirement):
    creator: User
    tag: Optional[RequirementTag] = None
    task: Optional[TaskWithDetails] = None

    class Config:
        from_attributes = True


# Memo schemas
class MemoBase(BaseModel):
    name: str
    content: Optional[str] = None

class MemoCreate(MemoBase):
    pass

class MemoUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None

class Memo(MemoBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MemoWithDetails(Memo):
    creator: Optional[UserBasic] = None

    class Config:
        from_attributes = True


# UserSession schemas
class UserSessionBase(BaseModel):
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_at: datetime
    last_activity_at: datetime
    is_active: int = 1


class UserSession(UserSessionBase):
    id: int

    class Config:
        from_attributes = True


class UserSessionResponse(BaseModel):
    id: int
    user_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    login_at: datetime
    last_activity_at: datetime
    is_active: int = 1

    class Config:
        from_attributes = True


# Task Hour schemas
class TaskHourBase(BaseModel):
    task_id: int
    user_id: int
    hours: float
    remark: Optional[str] = None


class TaskHourCreate(BaseModel):
    task_id: int
    user_ids: List[int]
    hours: float
    remark: Optional[str] = None


class TaskHour(TaskHourBase):
    id: int
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskHourWithDetails(TaskHour):
    user: UserBasic
    creator: UserBasic

    class Config:
        from_attributes = True


class TaskHoursStats(BaseModel):
    total_hours: float
    hours_list: List[TaskHourWithDetails]


# Menu schemas
class MenuBase(BaseModel):
    name: str
    parent_id: Optional[int] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    order_index: int = 0
    type: str = "menu"
    external_url: Optional[str] = None
    target: Optional[str] = None
    status: int = 1


class MenuCreate(MenuBase):
    pass


class MenuUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    order_index: Optional[int] = None
    type: Optional[str] = None
    external_url: Optional[str] = None
    target: Optional[str] = None
    status: Optional[int] = None


class MenuResponse(MenuBase):
    id: int
    created_at: datetime
    updated_at: datetime
    children: Optional[List['MenuResponse']] = []

    class Config:
        from_attributes = True


# Role schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: int = 1


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None


class RoleResponse(RoleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Permission schemas
class PermissionBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    menu_id: Optional[int] = None


class PermissionCreate(PermissionBase):
    menu_id: int = Field(..., description="关联的菜单ID，不能为空")


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    menu_id: Optional[int] = None


class PermissionResponse(PermissionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Update forward references
MenuResponse.model_rebuild()
