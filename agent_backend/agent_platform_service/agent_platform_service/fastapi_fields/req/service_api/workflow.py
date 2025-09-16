from typing import Optional, Literal

from pydantic import BaseModel

from agent_platform_core.models.db_model.model import App, EndUser


class ValidateAppTokenFields(BaseModel):
    app_model: Optional[App]
    end_user: Optional[EndUser]

    class Config:
        arbitrary_types_allowed = True


class WorkflowRunApiReq(BaseModel):

    inputs: dict

    files: Optional[list]

    response_mode: Literal['blocking', 'streaming']

    user: str
