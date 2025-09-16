"""

@Date    ：2024/9/12 11:50 
@Version: 1.0
@Description:

"""
from typing import Optional, Literal

from pydantic import BaseModel, field_validator, Field


class ChatMessagesReq(BaseModel):
    inputs: dict
    query: str
    conversation_id: Optional[str] = None
    response_mode: Literal["streaming", "blocking"] = "streaming"

    @field_validator('query')
    def check_query_non_empty(cls, v):
        if not v.strip():  # 去除空格后判断
            raise ValueError('Query cannot be an empty string')
        return v