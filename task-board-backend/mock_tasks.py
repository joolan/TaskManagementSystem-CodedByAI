from datetime import datetime, timedelta

# Mock users data
mock_users = [
    {
        "id": 1,
        "username": "admin",
        "name": "管理员",
        "email": "admin@example.com",
        "role": "admin",
        "created_at": (datetime.now() - timedelta(days=10)).isoformat(),
        "last_login_at": (datetime.now() - timedelta(days=1)).isoformat()
    },
    {
        "id": 2,
        "username": "frontend",
        "name": "前端开发",
        "email": "frontend@example.com",
        "role": "pm",
        "created_at": (datetime.now() - timedelta(days=9)).isoformat(),
        "last_login_at": (datetime.now() - timedelta(days=2)).isoformat()
    },
    {
        "id": 3,
        "username": "backend",
        "name": "后端开发",
        "email": "backend@example.com",
        "role": "pm",
        "created_at": (datetime.now() - timedelta(days=9)).isoformat(),
        "last_login_at": (datetime.now() - timedelta(days=1)).isoformat()
    }
]

# Mock statuses data
mock_statuses = [
    {
        "id": 1,
        "name": "待办",
        "order_index": 1,
        "color": "#94a3b8"
    },
    {
        "id": 2,
        "name": "进行中",
        "order_index": 2,
        "color": "#3b82f6"
    },
    {
        "id": 3,
        "name": "已完成",
        "order_index": 3,
        "color": "#10b981"
    },
    {
        "id": 4,
        "name": "已暂停",
        "order_index": 4,
        "color": "#f59e0b"
    },
    {
        "id": 5,
        "name": "已取消",
        "order_index": 5,
        "color": "#ef4444"
    }
]

# Mock tags data
mock_tags = [
    {
        "id": 1,
        "name": "前端",
        "color": "#60a5fa",
        "created_at": (datetime.now() - timedelta(days=10)).isoformat()
    },
    {
        "id": 2,
        "name": "后端",
        "color": "#10b981",
        "created_at": (datetime.now() - timedelta(days=10)).isoformat()
    },
    {
        "id": 3,
        "name": "UI/UX",
        "color": "#f472b6",
        "created_at": (datetime.now() - timedelta(days=10)).isoformat()
    },
    {
        "id": 4,
        "name": "测试",
        "color": "#fbbf24",
        "created_at": (datetime.now() - timedelta(days=10)).isoformat()
    },
    {
        "id": 5,
        "name": "优化",
        "color": "#a78bfa",
        "created_at": (datetime.now() - timedelta(days=10)).isoformat()
    },
    {
        "id": 6,
        "name": "文档",
        "color": "#6ee7b7",
        "created_at": (datetime.now() - timedelta(days=10)).isoformat()
    }
]

# Helper function to get user by id
def get_user_by_id(user_id):
    for user in mock_users:
        if user["id"] == user_id:
            return user
    return None

# Helper function to get status by id
def get_status_by_id(status_id):
    for status in mock_statuses:
        if status["id"] == status_id:
            return status
    return None

# Helper function to get tags by ids
def get_tags_by_ids(tag_ids):
    return [tag for tag in mock_tags if tag["id"] in tag_ids]

# Helper function to generate task data
def generate_task(task_id, title, description, status_id, assignee_id, priority, due_date_days, estimated_hours, tag_ids, created_days_ago=2, actual_start_days_ago=None, actual_completion_days_ago=None, actual_hours=None):
    task = {
        "id": task_id,
        "title": title,
        "description": description,
        "status_id": status_id,
        "status": get_status_by_id(status_id),
        "assignee_id": assignee_id,
        "assignee": get_user_by_id(assignee_id) if assignee_id else None,
        "assignee_ids": [assignee_id] if assignee_id else [],
        "assignees": [get_user_by_id(assignee_id)] if assignee_id else [],
        "priority": priority,
        "due_date": (datetime.now() + timedelta(days=due_date_days)).isoformat(),
        "estimated_hours": estimated_hours,
        "tag_ids": tag_ids,
        "tags": get_tags_by_ids(tag_ids),
        "created_by": 1,
        "creator": get_user_by_id(1),
        "created_at": (datetime.now() - timedelta(days=created_days_ago)).isoformat(),
        "updated_at": (datetime.now() - timedelta(days=created_days_ago)).isoformat()
    }
    
    if actual_start_days_ago is not None:
        task["actual_start_date"] = (datetime.now() - timedelta(days=actual_start_days_ago)).isoformat()
    
    if actual_completion_days_ago is not None:
        task["actual_completion_date"] = (datetime.now() - timedelta(days=actual_completion_days_ago)).isoformat()
        task["updated_at"] = task["actual_completion_date"]
    
    if actual_hours is not None:
        task["actual_hours"] = actual_hours
    
    return task

# Mock tasks data for internet project development
mock_tasks = [
    # 待办状态任务
    generate_task(
        1, "设计项目首页UI界面", "根据产品需求文档设计项目首页的UI界面，包括响应式布局和交互效果",
        1, 2, "high", 5, 8, [1, 3]
    ),
    # 待办状态任务
    generate_task(
        2, "实现用户注册功能", "开发用户注册模块，包括表单验证、密码加密和邮箱验证",
        1, 3, "medium", 7, 10, [2]
    ),
    generate_task(
        3, "搭建项目数据库结构", "设计并实现项目的数据库表结构，包括用户、任务、标签等表",
        1, 3, "high", 3, 12, [2]
    ),
    # 进行中状态任务
    generate_task(
        4, "开发项目API接口", "实现项目所需的RESTful API接口，包括用户、任务、标签等资源的CRUD操作",
        2, 3, "high", 4, 20, [2], 3, 1, None, 8
    ),
    generate_task(
        5, "开发任务管理界面", "实现任务管理模块的前端界面，包括任务列表、创建、编辑、删除等功能",
        2, 2, "medium", 6, 16, [1], 3, 1, None, 6
    ),
    generate_task(
        6, "实现用户认证系统", "开发基于JWT的用户认证系统，包括登录、注册、刷新token等功能",
        2, 3, "high", 3, 12, [2], 4, 2, None, 8
    ),
    generate_task(
        7, "开发看板界面", "实现任务看板界面，包括拖拽排序、状态切换等功能",
        2, 2, "medium", 5, 14, [1, 3], 3, 1, None, 4
    ),
    # 已完成状态任务
    generate_task(
        8, "项目初始化配置", "初始化项目结构，配置开发环境，安装必要的依赖包",
        3, 1, "high", -5, 8, [1, 2], 7, 7, 6, 6
    ),
    generate_task(
        9, "编写项目需求文档", "根据产品需求编写详细的项目需求文档，包括功能模块、数据结构、界面设计等",
        3, 1, "high", -4, 12, [6], 6, 6, 5, 10
    ),
    generate_task(
        10, "设计项目logo", "设计项目的logo和品牌标识，确保符合项目的定位和风格",
        3, 2, "medium", -3, 8, [3], 5, 5, 4, 7
    ),
    # 已暂停状态任务
    generate_task(
        11, "开发用户个人中心", "实现用户个人中心页面，包括个人信息管理、密码修改、头像上传等功能",
        4, 2, "medium", 8, 16, [1], 3, 2, None, 4
    ),
    generate_task(
        12, "实现数据统计功能", "开发数据统计模块，包括用户活跃度、任务完成率等统计功能",
        4, 3, "low", 10, 12, [2], 2, 1, None, 2
    ),
    # 已取消状态任务
    generate_task(
        13, "开发移动端适配", "为项目添加移动端适配，确保在手机和平板设备上正常显示",
        5, 2, "low", 12, 20, [1, 3], 4
    ),
    # 更多待办任务
    generate_task(
        14, "实现任务搜索功能", "开发任务搜索功能，支持按标题、描述、标签等条件搜索",
        1, 2, "medium", 9, 10, [1]
    ),
    generate_task(
        15, "开发标签管理功能", "实现标签的创建、编辑、删除等管理功能",
        1, 3, "medium", 8, 8, [2]
    ),
    generate_task(
        16, "实现任务提醒功能", "开发任务提醒功能，包括邮件通知、系统消息等",
        1, 3, "low", 11, 12, [2]
    ),
    generate_task(
        17, "设计任务详情页", "设计任务详情页面，包括任务信息、评论、附件等功能",
        1, 2, "medium", 7, 10, [1, 3]
    ),
    # 更多进行中任务
    generate_task(
        18, "开发评论功能", "实现任务评论功能，支持用户对任务进行评论和回复",
        2, 2, "medium", 5, 10, [1, 2], 3, 1, None, 3
    ),
    generate_task(
        19, "实现任务附件功能", "开发任务附件功能，支持上传、下载、预览附件",
        2, 3, "medium", 6, 14, [2], 3, 1, None, 4
    ),
    generate_task(
        20, "开发用户角色权限系统", "实现基于角色的权限控制系统，包括管理员、普通用户等角色",
        2, 3, "high", 8, 16, [2], 4, 2, None, 6
    ),
    # 更多已完成任务
    generate_task(
        21, "搭建项目版本控制系统", "搭建Git版本控制系统，配置代码仓库，设置分支管理策略",
        3, 1, "high", -5, 4, [1, 2], 6, 6, 6, 3
    ),
    generate_task(
        22, "配置项目CI/CD流程", "配置持续集成和持续部署流程，实现自动构建、测试、部署",
        3, 3, "medium", -3, 10, [2], 5, 5, 4, 8
    ),
    # 更多已暂停任务
    generate_task(
        23, "开发任务导出功能", "实现任务导出功能，支持导出为Excel、CSV等格式",
        4, 3, "low", 12, 8, [2], 3, 1, None, 1
    ),
    # 更多已取消任务
    generate_task(
        24, "开发任务甘特图视图", "实现任务甘特图视图，直观展示任务的时间安排和依赖关系",
        5, 2, "low", 14, 20, [1, 3], 4
    ),
    # 剩余待办任务
    generate_task(
        25, "实现任务批量操作功能", "开发任务批量操作功能，支持批量修改状态、优先级、标签等",
        1, 2, "medium", 10, 12, [1]
    ),
    generate_task(
        26, "开发用户通知系统", "实现用户通知系统，包括任务状态变更、评论回复等通知",
        1, 3, "medium", 11, 14, [2]
    ),
    generate_task(
        27, "实现任务模板功能", "开发任务模板功能，支持创建和使用任务模板",
        1, 3, "low", 13, 10, [2]
    ),
    # 剩余进行中任务
    generate_task(
        28, "开发任务依赖关系功能", "实现任务依赖关系功能，支持设置任务之间的依赖关系",
        2, 3, "medium", 7, 12, [2], 3, 1, None, 2
    ),
    generate_task(
        29, "优化任务加载性能", "优化任务列表和详情页面的加载性能，减少加载时间",
        2, 2, "high", 4, 8, [1, 5], 3, 1, None, 3
    ),
    # 最后一个已完成任务
    generate_task(
        30, "编写项目技术文档", "编写详细的项目技术文档，包括架构设计、API文档、部署指南等",
        3, 1, "medium", -2, 16, [6], 4, 4, 2, 14
    )
]

if __name__ == "__main__":
    import json
    print(json.dumps(mock_tasks, indent=2, ensure_ascii=False))
