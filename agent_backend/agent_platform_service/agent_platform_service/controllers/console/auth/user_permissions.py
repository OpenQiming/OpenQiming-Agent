import logging

from fastapi import Depends

from agent_platform_basic.models.db_model import Account
from agent_platform_service.controllers.console import console_api
from agent_platform_service.fastapi_fields.req.console.user_permissions_req import UserPermissionsReq, \
    UserPermissionsQueryReq
from agent_platform_service.fastapi_fields.resp.console.user_permissions_resp import UserPermissionsResp, \
    UserPermissionsDetailResp
from agent_platform_service.services.auth.user_permissions_service import UserPermissionsService
from agent_platform_service.services.auth_service import login_user

logger = logging.getLogger(__name__)


@console_api.post("/user/permissions/edit", response_model=UserPermissionsDetailResp,
                  summary="新增｜修改｜删除用户权限",
                  description="新增｜修改｜删除用户权限",
                  tags=["UserPermissions"])
async def user_permissions_api_post(request_body: UserPermissionsReq,
                                    current_user: Account = Depends(login_user),
                                    user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    return await user_permissions_service.user_permissions_edit(request_body.app_id,
                                                                request_body.user_permission_list,
                                                                current_user.username,
                                                                current_user.employee_number)


@console_api.post("/user/permissions/list", response_model=UserPermissionsResp, description="用户权限 列表查询",
                  tags=["UserPermissions"])
async def user_permissions_api_get(request_body: UserPermissionsQueryReq,
                                   current_user: Account = Depends(login_user),
                                   user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):

    return await user_permissions_service.user_permissions_api_get(request_body.app_id, request_body.employee_number)


@console_api.get("/user/permission/supper/list", response_model=UserPermissionsResp,
                 summary="超管或系统用户权限 列表查询",
                 description="超管或系统用户权限 列表查询",
                 tags=["UserPermissions"])
async def user_super_permissions_api_get(current_user: Account = Depends(login_user),
                                         user_permissions_service: UserPermissionsService = Depends(
                                             UserPermissionsService)):
    return await user_permissions_service.user_super_permissions_api_get(current_user.employee_number)
