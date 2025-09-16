from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from typing import List


class UserPermissionsDetailResp(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    app_id: Optional[str] = None
    can_view: Optional[bool] = None
    can_edit: Optional[bool] = None
    operator: Optional[str] = None
    created_at: Optional[datetime] = None


class UserPermission(BaseModel):
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    can_view: Optional[bool] = None
    can_edit: Optional[bool] = None
    operator: Optional[str] = None
    created_at: Optional[datetime] = None


class UserPermissionsResp(BaseModel):
    user_permissions_list: List[UserPermission] = []


@dataclass
class Reviewer:
    id: str
    name: str
