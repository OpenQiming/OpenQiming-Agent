from enum import Enum


class AuditStatus(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    DENIED = 'denied'


class ApplicationType(str, Enum):
    PUBLIC = 'public'  # 广场
    NORMAL = 'normal'  # 个人空间
    PROJECT = 'project'  # 项目空间
    SHARE = 'share'  # 共享广场
    DELETE = 'delete'  # 删除


class AppType(str, Enum):
    TOOL = 'tool'
