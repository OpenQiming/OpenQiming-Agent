"""

@Date    ：2024/9/18 10:26 
@Version: 1.0
@Description:

"""
from typing import Optional

from pydantic import BaseModel, Field


class ModelSetting(BaseModel):
    model: Optional[str] = Field(None, description="模型名称")
    model_type: str = Field(..., description="模型类型")
    provider: Optional[str] = Field(None, description="供应商模型")


class DefaultModelReq(BaseModel):
    app_model_settings: list[ModelSetting] = Field(..., description="默认模型设置列表", alias="model_settings")
    tenant_id: Optional[str] = None
