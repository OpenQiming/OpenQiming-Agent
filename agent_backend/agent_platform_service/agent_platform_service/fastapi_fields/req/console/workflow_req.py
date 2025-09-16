from pydantic import BaseModel, Field
from typing import Optional


class DraftWorkflowRunReq(BaseModel):
    inputs: dict
    files: Optional[list] = Field(None, description="文件附件")
    body: Optional[str] = Field(None, description="请求体")

class DraftChatflowRunReq(BaseModel):
    inputs: dict
    files: Optional[list] = Field(None, description="文件附件")
    body: Optional[str] = Field(None, description="请求体")
    conversation_id: Optional[str] = None
    query: Optional[str]
    parent_message_id: Optional[str] = None


class WorkflowReq(BaseModel):
    inputs: dict


class DraftWorkflowImportReq(BaseModel):
    data: str


class WorkflowPublishReq(BaseModel):
    tenant_id: Optional[str] = Field(None, description="发布到目标租户的id")
