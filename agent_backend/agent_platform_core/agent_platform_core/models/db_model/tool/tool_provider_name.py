from enum import Enum

"""
@Date    ：2024/7/15 8:49 
@Version: 1.0
@Description:

"""


class ToolProviderName(Enum):
    SERPAPI = 'serpapi'

    @staticmethod
    def value_of(value):
        for member in ToolProviderName:
            if member.value == value:
                return member
        raise ValueError(f"No matching enum found for value '{value}'")

