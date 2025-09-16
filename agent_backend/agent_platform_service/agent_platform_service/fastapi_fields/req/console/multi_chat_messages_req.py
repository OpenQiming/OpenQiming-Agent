"""

@Date    ：2024/9/12 11:50 
@Version: 1.0
@Description:

"""
from typing import Optional, Literal, Dict, Any

from pydantic import BaseModel, field_validator, Field


class MultiChatMessagesReq(BaseModel):
    inputs: dict
    query: str
    conversation_id: Optional[str] = None
    response_mode: Literal["streaming", "blocking"] = "streaming"
    model_config_settings: dict
    model_config_data: Dict[str, Any] = Field(..., alias="model_config")

    @field_validator('query')
    def check_query_non_empty(cls, v):
        if not v.strip():  # 去除空格后判断
            raise ValueError('Query cannot be an empty string')
        return v

    # @field_validator('model_config_setting')
    # def check_model_config(cls, v):
    #     if not v:
    #         raise ValueError('Model config cannot be an empty string')
    #     return v