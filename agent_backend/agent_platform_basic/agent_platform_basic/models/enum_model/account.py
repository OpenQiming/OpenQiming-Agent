from enum import Enum

""" 

@Date    ：2024/7/13 10:16 
@Version: 1.0
@Description:
    用户相关枚举
"""


class AccountStatus(str, Enum):
    PENDING = 'pending'
    UNINITIALIZED = 'uninitialized'
    ACTIVE = 'active'
    BANNED = 'banned'
    CLOSED = 'closed'
