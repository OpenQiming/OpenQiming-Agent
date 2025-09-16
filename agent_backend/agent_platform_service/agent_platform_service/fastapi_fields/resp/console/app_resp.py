from datetime import datetime
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class TagFields(BaseModel):
    id: str
    name: str
    type: str


class ModelConfigPartialFields(BaseModel):
    model: dict
    pre_prompt: str


class AppPartialField(BaseModel):
    id: str
    name: str
    description: str
    mode: str
    icon: Optional[str]
    icon_background: Optional[str]
    status: str
    # model_config: ModelConfigPartialFields
    created_at: date
    is_auditing: bool
    header_image: Optional[str]
    tags: List[TagFields]
    like_count: int
    location: Optional[str]


class AppPaginationResp(BaseModel):
    page: int
    limit: int
    total: int
    has_more: bool
    data: List[AppPartialField]


class AppDetailResp(BaseModel):
    id: str
    name: str
    description: str
    mode: str
    icon: Optional[str]
    icon_background: Optional[str]
    enable_site: bool
    enable_api: bool
    status: str
    tracing: Optional[str]
    created_at: datetime


class AIAppDetailResp(BaseModel):
    id: str
    name: str
    description: str
    mode: str
    icon: Optional[str]
    icon_background: Optional[str]
    enable_site: bool
    enable_api: bool
    status: str
    tracing: Optional[str]
    created_at: datetime
    #ai4apps
    agent_prompt: str
    tool_choice: List[str]


class SiteFields(BaseModel):
    access_token: Optional[str] = Field(None, alias="code")
    code: Optional[str]
    title: str
    icon: Optional[str]
    icon_background: Optional[str]
    description: Optional[str]
    default_language: str
    chat_color_theme: Optional[str]
    chat_color_theme_inverted: bool
    customize_domain: Optional[str]
    copyright: Optional[str]
    privacy_policy: Optional[str]
    custom_disclaimer: Optional[str] = Field(None, alias="customize_domain")
    customize_token_strategy: str
    prompt_public: bool
    app_base_url: str
    show_workflow_steps: bool


class AppDetailWithSiteResp(BaseModel):
    id: str
    name: str
    description: str
    mode: str
    icon: Optional[str]
    icon_background: Optional[str]
    enable_site: bool
    enable_api: bool
    app_model_configs: Optional[dict | list] = Field(None, alias="model_configs")
    site: SiteFields
    api_base_url: str
    created_at: datetime
    deleted_tools: List[str]
    header_image: Optional[str]
    tenant_id: Optional[str]
    tenant_name: Optional[str]


class AppExportedResp(BaseModel):
    data: str = Field(..., description="yaml格式导出的字符串")


class BaseResp(BaseModel):
    result: str

class AppStatistics(BaseModel):
    agent: int = Field(..., description="agent的数量")
    workflow: int = Field(..., description="workflow的数量")


class AppProvinceStatistics(BaseModel):
    data: dict = Field(..., description="各省份的app数量, key 为 employee_number 的后两位, value 为 数量")