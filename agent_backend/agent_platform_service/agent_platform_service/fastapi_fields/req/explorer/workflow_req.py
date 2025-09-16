from typing import Optional

from pydantic import BaseModel


class DraftWorkflowRunReq(BaseModel):
    inputs: dict
    files: Optional[list]
