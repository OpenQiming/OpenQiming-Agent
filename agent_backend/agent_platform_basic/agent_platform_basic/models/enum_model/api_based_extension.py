from enum import Enum

"""
@Date    ：2024/7/13 11:14 
@Version: 1.0
@Description:

"""


class APIBasedExtensionPoint(Enum):
    APP_EXTERNAL_DATA_TOOL_QUERY = 'app.external_data_tool.query'
    PING = 'ping'
    APP_MODERATION_INPUT = 'app.moderation.input'
    APP_MODERATION_OUTPUT = 'app.moderation.output'
