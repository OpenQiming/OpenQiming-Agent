from enum import Enum
""" 
@Date    ：2024/7/14 21:43 
@Version: 1.0
@Description:

"""

class ProviderType(Enum):
    CUSTOM = 'custom'
    SYSTEM = 'system'

    @staticmethod
    def value_of(value):
        for member in ProviderType:
            if member.value == value:
                return member
        raise ValueError(f"No matching enum found for value '{value}'")

class ProviderQuotaType(Enum):
    PAID = 'paid'
    """hosted paid quota"""

    FREE = 'free'
    """third-party free quota"""

    TRIAL = 'trial'
    """hosted trial quota"""

    @staticmethod
    def value_of(value):
        for member in ProviderQuotaType:
            if member.value == value:
                return member
        raise ValueError(f"No matching enum found for value '{value}'")
