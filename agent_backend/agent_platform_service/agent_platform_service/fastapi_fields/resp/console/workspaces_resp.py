"""

@Date    ：2024/9/2 18:39 
@Version: 1.0
@Description:

"""
from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional


class TenantsFields(BaseModel):
    id: Optional[str] = Field(..., description="项目空间唯一标识")
    name: Optional[str] = Field(..., description="项目空间名称")
    status: Optional[str] = Field(..., description="项目空间状态")
    created_at: Optional[datetime] = Field(..., description="创建时间")
    current: bool = Field(False, description="默认空间")
    role: str = Field(..., description="空间权限")
    tenant_desc: Optional[str] = Field(None, description="项目空间描述")


class CreateOrUpdateTenantResponse(BaseModel):
    result: str = Field(..., description="result")
    message: Optional[str] = Field(None, description="message")
