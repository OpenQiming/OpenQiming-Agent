"""

@Date    ：2024/9/2 18:39 
@Version: 1.0
@Description:

"""
from typing import Optional

from pydantic import BaseModel, Field

from agent_platform_basic.models.enum_model.tenant import TenantAccountRole


class TenantAccountsField(BaseModel):
    id: str = Field(..., description="用户id")
    role: TenantAccountRole = Field(..., description="用户角色")


class TenantCreateOrUpdateReq(BaseModel):
    id: Optional[str] = Field(None, description="项目空间id")
    name: str = Field(..., description="项目空间名称")
    description: Optional[str] = Field(None, description="项目空间描述")
    accounts: Optional[list[TenantAccountsField]] = Field(None, description="项目空间用户")

class UpdateRole(BaseModel):
    role: str = Field(..., description="用户角色")
    account_id: str = Field(..., description="用户id")
    tenant_id: str = Field(..., description="项目空间id")
