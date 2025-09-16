from enum import Enum

"""

@Date    ：2024/7/13 10:17 
@Version: 1.0
@Description:
    租户相关枚举
"""


class TenantStatus(str, Enum):
    NORMAL = 'normal'
    ARCHIVE = 'archive'


class TenantAccountRole(str, Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    EDITOR = 'editor'
    NORMAL = 'normal'

    @staticmethod
    def is_valid_role(role: str) -> bool:
        return role and role in {TenantAccountRole.OWNER, TenantAccountRole.ADMIN, TenantAccountRole.EDITOR,
                                 TenantAccountRole.NORMAL}

    @staticmethod
    def is_privileged_role(role: str) -> bool:
        return role and role in {TenantAccountRole.OWNER, TenantAccountRole.ADMIN}

    @staticmethod
    def is_non_owner_role(role: str) -> bool:
        return role and role in {TenantAccountRole.ADMIN, TenantAccountRole.EDITOR, TenantAccountRole.NORMAL}

    @staticmethod
    def is_editing_role(role: str) -> bool:
        return role and role in {TenantAccountRole.OWNER, TenantAccountRole.ADMIN, TenantAccountRole.EDITOR}

    @classmethod
    def is_owner_role(cls, role: str) -> bool:
        return role and role == TenantAccountRole.OWNER
