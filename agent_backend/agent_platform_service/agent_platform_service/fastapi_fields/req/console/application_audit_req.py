from typing import Optional, List

from pydantic import BaseModel
from sqlalchemy import true


class ApplicationAuditCreateReq(BaseModel):
    application_type: Optional[str] = None
    applicant_id: Optional[str] = None
    applicant: Optional[str] = None
    reason: Optional[str] = None
    app_id: Optional[str] = None
    app_type: Optional[str] = None
    space_id: Optional[str] = None
    current_tenant_id: Optional[str] = None
    employee_number: Optional[str] = None
    username: Optional[str] = None
    status: Optional[str] = None
    reviewer_id: Optional[str] = None
    reviewer: Optional[str] = None
    change_description: Optional[str] = None
    need_publish_tool: Optional[bool] = False
    tool_param: Optional[str] = None


class ApplicationAuditUpdateReq(BaseModel):
    process_id: Optional[str] = None
    app_id: Optional[str] = None
    status: Optional[str] = None
    denial_reason: Optional[str] = None


class ApplicationAuditPageReq(BaseModel):
    page: Optional[int] = None
    limit: Optional[int] = None
    need_check: Optional[bool] = true
    process_id: Optional[str] = None
    application_type: Optional[List[str]] = None
    applicant_id: Optional[str] = None
    applicant: Optional[str] = None
    reason: Optional[str] = None
    app_id: Optional[str] = None
    app_type: Optional[List[str]] = None
    space_id: Optional[str] = None
    space_name: Optional[str] = None
    status: Optional[str] = None
    denial_reason: Optional[str] = None
    reviewer_id: Optional[str] = None
    reviewer: Optional[str] = None
