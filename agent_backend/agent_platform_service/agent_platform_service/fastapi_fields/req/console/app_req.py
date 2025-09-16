from typing import Optional

from pydantic import BaseModel, field_validator, Field

ALLOW_CREATE_APP_MODES = ['chat', 'agent-chat', 'advanced-chat', 'workflow', 'completion', 'metabolic']


class CreateAppReq(BaseModel):
    name: str = Field(..., description="app名称")
    description: str = Field(..., description="app描述")
    mode: str = Field(..., description="app类型")
    tenant_id: Optional[str] = Field(None, description="租户id")
    icon: Optional[str] = Field(None, description="图标")
    icon_background: Optional[str] = Field(None, description="图标背景")
    header_image: Optional[str] = Field(None, description="头像")
    def validate_mode(cls, value):
        if value not in ALLOW_CREATE_APP_MODES:
            error = f'{value} is not a supported mode.'
            raise ValueError(error)
        return value

class CreateAIAppReq(BaseModel):
    # name: str = Field(..., description="app名称")
    description: str = Field(..., description="app描述")
    mode: str = Field(..., description="app类型")
    tenant_id: Optional[str] = Field(None, description="租户id")
    icon: Optional[str] = Field(None, description="图标")
    icon_background: Optional[str] = Field(None, description="图标背景")
    header_image: Optional[str] = Field(None, description="头像")
    tool_list: list[dict] = Field(None, description="可调用工具集")

    def validate_mode(cls, value):
        if value not in ALLOW_CREATE_APP_MODES:
            error = f'{value} is not a supported mode.'
            raise ValueError(error)
        return value


class ImportAppReq(BaseModel):
    name: Optional[str] = Field(None, description="app名称")
    description: Optional[str] = Field(None, description="app描述")
    tenant_id: str = Field(None, description="租户id")
    icon: Optional[str] = Field(None, description="图标")
    icon_background: Optional[str] = Field(None, description="图标背景")
    data: str = Field(..., description="yaml格式数据")


class UpdateAppReq(BaseModel):
    name: str = Field(..., description="app名称")
    description: str = Field(..., description="app描述")
    icon: Optional[str] = Field(None, description="图标")
    icon_background: Optional[str] = Field(None, description="图标背景")
    header_image: Optional[str] = Field(None, description="头像")
    tenant_id : Optional[str] = Field(None, description="租户名称")


class CopyAppReq(BaseModel):
    name: str = Field(..., description="app名称")
    mode: str = Field(..., description="app类型")
    tenant_id: Optional[str] = Field(None, description="租户id")
    icon: Optional[str] = Field(None, description="图标")
    icon_background: Optional[str] = Field(None, description="图标背景")
    squre: str = "0"

class MoveAppReq(BaseModel):
    mode: str = Field(..., description="app类型")
    # from_tenant_id: str = Field(..., description="原租户id")
    to_tenant_id: str = Field(..., description="目标租户id")


class UpdateAppNameReq(BaseModel):
    name: str = Field(..., description="app名称")


class UpdateAppIconReq(BaseModel):
    icon: str = Field(..., description="图标")
    icon_background: str = Field(..., description="图标背景")


class EnableSiteReq(BaseModel):
    enable_site: bool


class EnableApiReq(BaseModel):
    enable_api: bool


class UpdateAppTracerReq(BaseModel):
    enabled: bool
    tracing_provider: str
