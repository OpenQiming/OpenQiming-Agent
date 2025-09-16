from datetime import datetime
from typing import Optional, List, Annotated

from pydantic import BaseModel, BeforeValidator
from pydantic import Field
from pydantic.v1.datetime_parse import parse_datetime


class ApiExportReq(BaseModel):
    api_id_list: Optional[list[str]]


class ApiInfoReq(BaseModel):
    interface_name_zh: Optional[str] = None
    api_id: Optional[List[str]] = None
    interface_type: Optional[str] = None
    region: Optional[str] = None
    application_scenario: Optional[str] = None
    startTime: Optional[Annotated[datetime, BeforeValidator(parse_datetime)]] = Field(
        None,
        description="开始时间(非必需)"
    )
    endTime: Optional[Annotated[datetime, BeforeValidator(parse_datetime)]] = Field(
        None,
        description="结束时间(非必需)"
    )

    class Config:
        from_attributes = True


class ApiInfoDto(BaseModel):
    id: Optional[int] = None
    interface_name_zh: str
    interface_name_en: str
    api_id: str
    interface_type: str
    eop_protocol: str
    eop_call_address: str
    service_protocol: str
    interface_description: str
    auth_policy: str
    timeout: int
    open_scope: str
    is_public: bool
    system_belonged_to: str
    region: str
    application_scenario: str
    headers: str
    request_script: str
    input_params: str
    request_example: str
    output_params: str
    response_example: str


class ApiInfoPageReq(BaseModel):
    page: Optional[int] = None
    limit: Optional[int] = None
    interface_name_zh: Optional[str]
    api_id: Optional[str]
    interface_type: Optional[str]
    region: Optional[str]
    application_scenario: Optional[str]


class ApiInfoPageResp(BaseModel):
    page: int
    limit: int
    total: int
    has_more: bool
    data: list[ApiInfoDto] = []
