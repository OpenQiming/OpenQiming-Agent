from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict


class ApplicationAuditItem(BaseModel):
    id: Optional[str] = None
    application_type: Optional[str] = None
    applicant_id: Optional[str] = None
    applicant: Optional[str] = None
    reason: Optional[str] = None
    app_id: Optional[str] = None
    app_type: Optional[str] = None
    space_id: Optional[str] = None
    space_name: Optional[str] = None
    application_time: Optional[datetime] = None
    status: Optional[str] = None
    denial_reason: Optional[str] = None
    reviewer_id: Optional[str] = None
    reviewer: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    app_name: Optional[str] = None
    app_attr: Optional[str] = None
    app_desc: Optional[str] = None
    app_creator: Optional[str] = None
    owner_name: Optional[str] = None
    owner_id:Optional[str] = None

class ApplicationAuditResp(BaseModel):
    data: List[ApplicationAuditItem] = Field(..., description="审核记录列表")


class ApplicationAuditPageResp(BaseModel):
    page: int
    limit: int
    total: int
    has_more: bool
    data: List[ApplicationAuditItem] = Field(..., description="审核记录列表")


class ApplicationAuditEditResp(BaseModel):
    result: Optional[str] = None
    process_id: Optional[str] = None
