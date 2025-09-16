from typing import List, Optional

from pydantic import BaseModel


class UserPermissionReq(BaseModel):
    user_id: Optional[str] = None
    can_view: Optional[bool] = None
    can_edit: Optional[bool] = None


class UserPermissionsReq(BaseModel):
    request_id: Optional[str] = None
    app_id: Optional[str] = None
    user_permission_list: List[UserPermissionReq] = None


class UserPermissionsQueryReq(BaseModel):
    app_id: Optional[str] = None
    employee_number: Optional[str] = None
