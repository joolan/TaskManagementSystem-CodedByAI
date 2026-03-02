# routes/__init__.py
# 导出所有路由模块

from . import auth
from . import tasks
from . import comments
from . import attachments
from . import stats
from . import settings
from . import uploads
from . import logs
from . import releases
from . import requirements
from . import database
from . import memos
from . import menus
from . import roles
from . import permissions

__all__ = [
    'auth',
    'tasks',
    'comments',
    'attachments',
    'stats',
    'settings',
    'uploads',
    'logs',
    'releases',
    'requirements',
    'database',
    'memos',
    'menus',
    'roles',
    'permissions'
]