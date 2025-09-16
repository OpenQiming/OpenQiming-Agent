import json
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform_basic.models.db_model import Account
from agent_platform_core.helper import encrypter
from agent_platform_core.models.db_model.model import EndUser
from agent_platform_core.models.db_model.workflow import Workflow
from agent_platform_core.models.enum_model.enums import CreatedByRole
from agent_platform_core.variables import SecretVariable, Variable
from agent_platform_service.fastapi_fields.resp.console.member_fields import SimpleAccountFields
from agent_platform_service.fields.model_async.config.handle_extra_fields import create_instance
from agent_platform_service.fields.model_async.workflow_async import WorkflowAsync
from agent_platform_service.fields.workflow_fields import ENVIRONMENT_VARIABLE_SUPPORTED_TYPES


# 定义 WorkflowResponse 模型
class WorkflowResponse(BaseModel):
    id: Optional[str] = None
    environment_variables: Optional[list] = None
    conversation_variables: Optional[list] = None
    graph: Optional[Any] = None
    features: Optional[Any] = None
    hash: Optional[str] = None
    created_by: Optional[SimpleAccountFields] = None
    created_at: Optional[int] = None
    updated_by: Optional[SimpleAccountFields] = None
    updated_at: Optional[int] = None
    tool_published: Optional[bool] = None
    '''
    environment_variables_list = param.get('environment_variables') or []
    environment_variables = [variable_factory.build_environment_variable_from_mapping(obj) for obj in environment_variables_list] if len(environment_variables_list) >0 else []
    '''

    @classmethod
    def _format(cls, value):
        # Mask secret variables values in environment_variables
        if isinstance(value, SecretVariable):
            return {
                "id": value.id,
                "name": value.name,
                "value": encrypter.obfuscated_token(value.value),
                "value_type": value.value_type.value,
                "description": value.description,
            }
        if isinstance(value, Variable):
            return {
                "id": value.id,
                "name": value.name,
                "value": value.value,
                "value_type": value.value_type.value,
                "description": value.description,
            }
        if isinstance(value, dict):
            value_type = value.get("value_type")
            if value_type not in ENVIRONMENT_VARIABLE_SUPPORTED_TYPES:
                raise ValueError(f"Unsupported environment variable value type: {value_type}")
            return value

    @classmethod
    async def from_workflow(cls, workflow: Workflow, session):
        if workflow is None:
            return WorkflowResponse()
        return cls(
            id=workflow.id,
            environment_variables=[cls._format(var) for var in await workflow.async_environment_variables()],
            conversation_variables=[cls._format(var) for var in workflow.conversation_variables],
            graph=workflow.graph_dict,
            features=workflow.features_dict,
            hash=workflow.unique_hash,
            updated_at=int(workflow.updated_at.timestamp()) if workflow.updated_at else None,
            created_at=int(workflow.created_at.timestamp()) if workflow.created_at else None,
            created_by=await create_instance(WorkflowAsync, "created_by_account",
                                             method_args={'created_by': workflow.created_by}, session=session,
                                             return_type=SimpleAccountFields),
            updated_by=await create_instance(WorkflowAsync, "updated_by_account",
                                             method_args={'updated_by': workflow.updated_by}, session=session,
                                             return_type=SimpleAccountFields),
            tool_published=await create_instance(WorkflowAsync, "async_tool_published",
                                                 method_args={'app_id': workflow.app_id}, session=session)
        )


class DraftWorkflowApiPostResp(BaseModel):
    result: str

    hash: str

    updated_at: int


class PublishedWorkflowApiPostResp(BaseModel):
    result: str
    created_at: int


class WorkflowRunNodeExecutionResp(BaseModel):
    id: str
    index: int
    predecessor_node_id: Optional[str]
    node_id: str
    node_type: str
    title: str
    inputs: Optional[dict]
    process_data: Optional[dict]
    outputs: Optional[dict]
    status: str
    error: Optional[str]
    elapsed_time: float
    execution_metadata: Optional[dict]
    # extras: dict  暂时注释掉 图标编码有问题
    created_at: datetime
    created_by_role: str
    # created_by_account: Optional[SimpleAccountFields] = Field(None, alias='created_by_account')
    # created_by_end_user: Optional[SimpleEndUserFields] = Field(None, alias='created_by_end_user')
    finished_at: datetime

    @classmethod
    async def created_by_account(cls, session: AsyncSession, created_by_role: str, created_by: str):
        created_by_role = CreatedByRole.value_of(created_by_role)
        if created_by_role == CreatedByRole.ACCOUNT:
            return await session.get(Account, created_by)
        return None

    @classmethod
    async def created_by_end_user(cls, session: AsyncSession, created_by_role: str, created_by: str):
        created_by_role = CreatedByRole.value_of(created_by_role)

        if created_by_role == CreatedByRole.END_USER:
            return await session.get(EndUser, created_by)
        return None

    @field_validator("inputs", "process_data", "outputs", "execution_metadata", mode="before")
    def parse_json_fields(cls, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format")
        return value


class HistoryWorkflowResp(BaseModel):
    app_model_config_id: Optional[str] = Field(None, alias="model_config_id")
    workflow_id: Optional[str] = None
    history_time: datetime
    update_man_name: str
    update_man_id: str
    version_name: str
