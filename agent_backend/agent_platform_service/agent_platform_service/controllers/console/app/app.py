import logging
from typing import Optional

from fastapi import Request, Depends
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.responses import JSONResponse

from agent_platform_basic.exceptions.base_http_exception import Forbidden
from agent_platform_basic.exceptions.services.user_permissions import UserPermissionError
from agent_platform_basic.extensions.ext_redis import async_redis_client
from agent_platform_basic.libs import DbUtils
from agent_platform_basic.libs.aes import encrypt_data_and_base64_encode, decrypt_data_from_base64
from agent_platform_basic.models.db_model import Account
from agent_platform_basic.models.enum_model.application_audit import AppType, ApplicationType
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.models.db_model.model import App, AppModelConfig
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_core.models.enum_model.app_status import AppStatus
from agent_platform_core.ops.ops_trace_manager import OpsTraceManager
from agent_platform_service.controllers.console import console_api
from agent_platform_service.controllers.console.app.wraps import get_app_model_async
from agent_platform_service.fastapi_fields.req.console.app_req import CreateAppReq, ImportAppReq, CopyAppReq, \
    UpdateAppReq, UpdateAppNameReq, UpdateAppIconReq, EnableSiteReq, EnableApiReq, UpdateAppTracerReq, MoveAppReq, \
    CreateAIAppReq
from agent_platform_service.fastapi_fields.resp.console.app_resp import AppPaginationResp, AppDetailResp, \
    AppDetailWithSiteResp, AppExportedResp, BaseResp, AIAppDetailResp
from agent_platform_service.fields.model_async.app_async import AppAsync
from agent_platform_service.services.app_model_config_service import AppModelConfigService
from agent_platform_service.services.app_service import AppService
from agent_platform_service.services.app_yaml_service import AppYamlService
from agent_platform_service.services.audit.application_audit_service import ApplicationAuditService
from agent_platform_service.services.workflow_service import WorkflowService
from agent_platform_service.services.auth.user_permissions_service import UserPermissionsService
from agent_platform_service.services.auth_service import login_user

logger = logging.getLogger(__name__)


# @console_api.get("/apps", response_model=AppPaginationResp)
@console_api.get("/apps")
async def app_list_api_get(page: int, limit: int,
                           mode: Optional[str] = None, name: Optional[str] = None,
                           tag_ids: Optional[str] = None, status: Optional[str] = None,
                           tenant_id: Optional[str] = None,
                           app_service: AppService = Depends(AppService),
                           current_user: Account = Depends(login_user),
                           user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_user(tenant_id):
    #     raise Forbidden()
    #
    # try:
    #     has_permission_apps = await user_permissions_service.check_user_read_auth(current_user.employee_number, None)
    #     if not has_permission_apps:
    #         return []
    # except UserPermissionError as e:
    #     logger.error(f'app_list_api_get.check_user_edit_auth: {e}')
    #     raise Forbidden()

    """Get app list"""
    args = {'page': page, 'limit': limit, 'mode': mode, 'name': name, 'tag_ids': tag_ids, 'status': status,
            'tenant_id': tenant_id}
    return await app_service.get_paginate_apps_async(current_user, args)


@console_api.post("/apps", response_model=AppDetailResp, status_code=status.HTTP_201_CREATED)
async def app_list_api_post(request_body: CreateAppReq,
                            app_service: AppService = Depends(AppService),
                            current_user: Account = Depends(login_user),
                            user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_user(request_body.tenant_id):
    #     raise Forbidden()
    #
    # try:
    #     has_permission = await user_permissions_service.check_user_edit_auth(current_user.employee_number, None)
    #     if not has_permission:
    #         raise Forbidden()
    # except UserPermissionError as e:
    #     logger.error(f'app_list_api_post.check_user_edit_auth: {e}')
    #     raise Forbidden()

    """Create app"""
    if not current_user.is_editor:
        raise Forbidden()

    app = await app_service.create_app_async(current_user, request_body.model_dump())
    return app


@console_api.post("/ai4apps", response_model=AIAppDetailResp, status_code=status.HTTP_201_CREATED)
async def app_list_api_post(request_body: CreateAIAppReq,
                            app_service: AppService = Depends(AppService),
                            current_user: Account = Depends(login_user),
                            user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_user(request_body.tenant_id):
    #     raise Forbidden()
    #
    # try:
    #     has_permission = await user_permissions_service.check_user_edit_auth(current_user.employee_number, None)
    #     if not has_permission:
    #         raise Forbidden()
    # except UserPermissionError as e:
    #     logger.error(f'app_list_api_post.check_user_edit_auth: {e}')
    #     raise Forbidden()

    """Create app"""
    if not current_user.is_editor:
        raise Forbidden()

    app = await app_service.ai_create_app_async(current_user, request_body.model_dump())
    return app


@console_api.post("/apps/import", response_model=AppDetailResp, status_code=status.HTTP_201_CREATED)
async def app_import_api_post(request_body: ImportAppReq,
                              app_yaml_service: AppYamlService = Depends(AppYamlService),
                              current_user: Account = Depends(login_user),
                              user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(request_body.tenant_id):
    #     raise Forbidden()
    #
    # try:
    #     has_permission = await user_permissions_service.check_user_edit_auth(current_user.employee_number, None)
    #     if not has_permission:
    #         raise Forbidden()
    # except UserPermissionError as e:
    #     logger.error(f'app_import_api_post.check_user_edit_auth: {e}')
    #     raise Forbidden()

    """Import app"""

    tenant_id = request_body.tenant_id if request_body.tenant_id else current_user.current_tenant_id

    # if not current_user.is_tenant_editor(tenant_id):
    #     raise Forbidden

    decrypted_data_dict = decrypt_data_from_base64(request_body.data)

    app = await app_yaml_service.import_and_create_new_app(
        tenant_id=tenant_id, data=decrypted_data_dict,
        args=request_body.model_dump(exclude={"data"}), account=current_user
    )

    return app


@console_api.get("/apps/{app_id}", response_model=AppDetailWithSiteResp)
async def app_api_get(app_id: str,
                      current_user: Account = Depends(login_user),
                      app_model: App = Depends(get_app_model_async),
                      app_async=Depends(AppAsync), app_service: AppService = Depends(AppService),
                      user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_read_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_api_get.check_user_read_auth: {e}')
    #     raise Forbidden()

    """Get app detail"""
    api_base_url = agent_platform_config.SERVICE_API_URL
    deleted_tools = await app_async.deleted_tools_async(app_model)
    site = await app_async.site_fields_async(app_model)
    model_configs = await app_async.model_config_fields_async(app_model)
    tenant_obj = await app_service.get_tenant_obj_async(app_model.tenant_id)
    logger.info(f'app_model.tenant_id:{app_model.tenant_id}tenant_obj: {tenant_obj},tenant_obj.name:{tenant_obj.name}')
    resp = AppDetailWithSiteResp(**vars(app_model), model_configs=model_configs, api_base_url=api_base_url, site=site,
                                 deleted_tools=deleted_tools, tenant_name=tenant_obj.name)
    resp.tenant_name = tenant_obj.name
    return resp


@console_api.put("/apps/{app_id}", response_model=AppDetailResp)
async def app_api_put(app_id: str, request_body: UpdateAppReq,
                      current_user: Account = Depends(login_user),
                      app_service: AppService = Depends(AppService),
                      user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)
                      ):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_api_put.check_user_edit_auth: {e}')
    #     raise Forbidden()

    """Update app"""
    # The role of the current user in the ta table must be admin, owner, or editor
    if not current_user.is_editor:
        raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id, mode=None)

    app_model = await app_service.update_app_async(app_model, request_body.model_dump())

    return app_model


# @console_api.delete("/apps/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
@console_api.delete("/apps/{app_id}")
async def app_api_delete(app_id: str,
                         app_service: AppService = Depends(AppService),
                         current_user: Account = Depends(login_user),
                         app_model: App = Depends(get_app_model_async),
                         workflow_service: WorkflowService = Depends(WorkflowService),
                         app_model_config_service: AppModelConfigService = Depends(AppModelConfigService),
                         user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    #
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_api_delete.check_user_edit_auth: {e}')
    #     raise Forbidden()
    """Delete app"""
    # The role of the current user in the ta table must be admin, owner, or editor
    if not current_user.is_tenant_editor(app_model.tenant_id):
        # raise Forbidden()
        return JSONResponse(
            status_code=200,  # 或者使用其他合适的状态码
            content={"success": False, "message": "您没有删除该应用的权限!"}
        )

    # 判断是否通知数智下线模型
    if app_model.mode in [AppMode.WORKFLOW.value, AppMode.METABOLIC.value] and app_model.workflow_id:
        workflows = await app_service.get_workflows_async(app_model.workflow_id)
        await workflow_service.send_tool_chain_msg(app_model, {'nodes': '1'}, workflows)
    if app_model.mode in [AppMode.AGENT_CHAT.value] and app_model.app_model_config_id:
        app_model_config = await app_service.get_app_model_config_async(app_model.app_model_config_id)
        await app_model_config_service.send_tool_chain_msg_async(app_model=app_model, new_app_model_config=None,
                                                                 original_app_model_config=app_model_config)
    await app_service.delete_app_async(app_model)
    return JSONResponse(
        status_code=200,
        content={"success": True, "message": "应用删除成功"}
    )


@console_api.delete("/apps/tenant/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def app_delete_api_delete(app_id: str,
                                app_service: AppService = Depends(AppService),
                                current_user: Account = Depends(login_user),
                                app_model: App = Depends(get_app_model_async)):
    """Delete app"""
    # The role of the current user in the ta table must be admin, owner, or editor
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()

    await app_service.delete_tenant_app_async(current_user, app_model=app_model, provider_name=None)


@console_api.post("/apps/{app_id}/copy", response_model=AppDetailResp, status_code=status.HTTP_201_CREATED)
async def app_copy_api_post(request: Request, app_id: str, request_body: CopyAppReq,
                            current_user: Account = Depends(login_user),
                            app_yaml_service: AppYamlService = Depends(AppYamlService),
                            app_service: AppService = Depends(AppService),):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_copy_api_post.check_user_edit_auth: {e}')
    #     raise Forbidden()
    # 获取指定 header，比如 Authorization
    auth_token = request.headers.get("Authorization")

    """Copy app"""
    #获取app
    app_model = await get_app_model_async(app_id=app_id, mode=None)

    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()

    #导出配置
    data = await app_yaml_service.export_yaml(app_model, include_secret=False)
    # print("squre::::", request_body.squre)
    tenant_id = request_body.tenant_id if request_body.tenant_id else current_user.current_tenant_id
    # tenant_id = current_user.current_tenant_id if request_body.squre == "1" else app_model.tenant_id
    app = await app_yaml_service.import_and_create_new_app(tenant_id, data,
                                                           request_body.model_dump(), current_user)

    print("token::::", auth_token, tenant_id)
    # 创建嵌套工作流和绑定智能体
    await app_service.app_copy_main(app_id=app_id, new_id=app.id, application_type='', account=current_user, token=auth_token, publish_tenant_id=tenant_id)
    return app


@console_api.post("/apps/{app_id}/move", response_model=AppDetailResp, status_code=status.HTTP_201_CREATED)
async def app_move_api_post(app_id: str, request_body: MoveAppReq,
                            current_user: Account = Depends(login_user),
                            app_yaml_service: AppYamlService = Depends(AppYamlService),
                            user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_move_api_post.check_user_edit_auth: {e}')
    #     raise Forbidden()

    """Move app"""
    # The role of the current user in the ta table must be admin, owner, or editor
    if not current_user.is_editor:
        raise Forbidden()
    app_model = await get_app_model_async(app_id=app_id, mode=None)
    if not (current_user.is_tenant_editor(app_model.tenant_id)
            and current_user.is_tenant_editor(request_body.to_tenant_id)):
        raise Forbidden()

    data = await app_yaml_service.export_yaml(app_model, include_secret=False)
    app = await app_yaml_service.import_and_create_new_app(request_body.to_tenant_id, data,
                                                           request_body.model_dump(exclude={"data"}), current_user)
    return app


@console_api.get("/apps/{app_id}/export", response_model=AppExportedResp)
async def app_export_api_get(app_id: str, include_secret: bool = False,
                             current_user: Account = Depends(login_user),
                             app_yaml_service: AppYamlService = Depends(AppYamlService),
                             user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_export_api_get.check_user_edit_auth: {e}')
    #     raise Forbidden()

    """Export app"""
    app_model = await get_app_model_async(app_id=app_id, mode=None)

    if not current_user.is_tenant_editor(app_model.tenant_id):
        raise Forbidden()

    export_data = await app_yaml_service.export_yaml(app_model, include_secret=include_secret)

    # 数据加密
    encrypted_data_base64 = encrypt_data_and_base64_encode(export_data)
    return {
        'data': encrypted_data_base64
    }


@console_api.post("/apps/{app_id}/name", response_model=AppDetailResp)
async def app_name_api_post(app_id: str, request_body: UpdateAppNameReq,
                            current_user: Account = Depends(login_user),
                            app_service: AppService = Depends(AppService),
                            user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_name_api_post.check_user_edit_auth: {e}')
    #     raise Forbidden()
    # # The role of the current user in the ta table must be admin, owner, or editor
    # if not current_user.is_editor:
    #     raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id, mode=None)

    app_model = await app_service.update_app_name_async(app_model, request_body.name)

    return app_model


@console_api.post("/apps/{app_id}/icon", response_model=AppDetailResp)
async def app_icon_api_post(app_id: str, request_body: UpdateAppIconReq,
                            current_user: Account = Depends(login_user),
                            app_service: AppService = Depends(AppService),
                            user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_read_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_icon_api_post.check_user_read_auth: {e}')
    #     raise Forbidden()
    #
    # The role of the current user in the ta table must be admin, owner, or editor
    # if not current_user.is_editor:
    #     raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id, mode=None)

    app_model = await app_service.update_app_icon_async(app_model, request_body.icon, request_body.icon_background)

    return app_model


@console_api.post("/apps/{app_id}/site-enable", response_model=AppDetailResp)
async def app_site_status_post(app_id: str, request_body: EnableSiteReq,
                               current_user: Account = Depends(login_user),
                               app_service: AppService = Depends(AppService),
                               user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_read_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_site_status_post.check_user_read_auth: {e}')
    #     raise Forbidden()
    #
    # # The role of the current user in the ta table must be admin, owner, or editor
    # if not current_user.is_editor:
    #     raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id, mode=None)

    app_model = await app_service.update_app_site_status_async(app_model, request_body.enable_site)

    return app_model


@console_api.post("/apps/{app_id}/api-enable", response_model=AppDetailResp)
async def app_api_status_post(app_id: str, request_body: EnableApiReq,
                              current_user: Account = Depends(login_user),
                              app_service: AppService = Depends(AppService),
                              user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    #
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_api_status_post.check_user_read_auth: {e}')
    #     raise Forbidden()
    #
    # # The role of the current user in the ta table must be admin or owner
    # if not current_user.is_editor:
    #     raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id, mode=None)

    app_model = await app_service.update_app_api_status_async(app_model, request_body.enable_api)

    return app_model


@console_api.get("/apps/{app_id}/trace")
async def app_trace_api_get(app_id: str, current_user: Account = Depends(login_user),
                            ops_trace_manager: OpsTraceManager = Depends(OpsTraceManager),
                            app_model: App = Depends(get_app_model_async),
                            user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_read_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_trace_api_get.check_user_read_auth: {e}')
    #     raise Forbidden()
    """Get app trace"""
    app_trace_config = await ops_trace_manager.get_app_tracing_config_async(
        app_id=app_id
    )

    return app_trace_config


@console_api.post("/apps/{app_id}/trace", response_model=BaseResp)
async def app_trace_api_post(app_id: str, request_body: UpdateAppTracerReq,
                             current_user: Account = Depends(login_user),
                             app_model: App = Depends(get_app_model_async),
                             ops_trace_manager: OpsTraceManager = Depends(OpsTraceManager),
                             user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_read_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'app_trace_api_post.check_user_read_auth: {e}')
    #     raise Forbidden()
    #
    # # add app trace
    # if not current_user.is_editor:
    #     raise Forbidden()

    await ops_trace_manager.update_app_tracing_config_async(
        app_id=app_id,
        enabled=request_body.enabled,
        tracing_provider=request_body.tracing_provider,
    )

    return {"result": "success"}


# 个人空间-应用发布到个人空间
@console_api.post("/apps/{app_id}/published/personal")
async def app_published_to_personal(app_id: str, request: Request,
                                    app_service: AppService = Depends(AppService),
                                    current_user: Account = Depends(login_user)):
    # if not current_user.is_editor:
    #     raise Forbidden()
    app_model = await get_app_model_async(app_id=app_id, mode=None)
    param = await request.json()
    new_app_id = await app_service.publish_app_to_personal(app_id, app_model, param['desc'])
    await app_service.publish_personal_audit_create(app_id, app_model.mode, current_user)
    return {"result": "success", "workflow_app_id": new_app_id}


# 个人空间-工具发布到个人空间
@console_api.post("/tools/{tool_api_providers_id}/published/personal")
async def tool_published_to_personal(tool_api_providers_id: str, request: Request,
                                     app_service: AppService = Depends(AppService),
                                     current_user: Account = Depends(login_user)):
    # if not current_user.is_editor:
    #     raise Forbidden()
    param = await request.json()
    await app_service.publish_tool(tool_api_providers_id, ApplicationType.NORMAL.value, tenant_id=None,
                                   desc=param['desc'])
    await app_service.publish_personal_audit_create(tool_api_providers_id, AppMode.TOOL.value,
                                                    current_user)
    return {"result": "success"}


# 个人空间-工具发布到广场
@console_api.post("/tools/{tool_api_providers_id}/audit/public")
async def tool_published_to_public_audit(tool_api_providers_id: str,
                                         request: Request,
                                         app_service: AppService = Depends(AppService),
                                         current_user: Account = Depends(login_user)):
    param = await request.json()
    await app_service.published_audit_main(app_id=tool_api_providers_id, current_user=current_user, msg=param['msg'],
                                           workspace_id=agent_platform_config.GLOBAL_TENANT_ID,
                                           app_type=AppMode.TOOL.value,
                                           application_type=ApplicationType.PUBLIC.value, desc=param['desc'])
    return {"result": "success"}


# 个人空间-工具发布到共享广场（即插件发布到共享广场）
@console_api.post("/tools/{tool_api_providers_id}/audit/share_public")
async def tool_published_to_public_audit(tool_api_providers_id: str,
                                         request: Request,
                                         app_service: AppService = Depends(AppService),
                                         current_user: Account = Depends(login_user)):
    param = await request.json()
    await app_service.published_audit_main(app_id=tool_api_providers_id, current_user=current_user, msg=param['msg'],
                                           workspace_id=agent_platform_config.GLOBAL_SHARE_TENANT_ID,
                                           app_type=AppMode.TOOL.value,
                                           application_type=ApplicationType.SHARE.value, desc=param['desc'])
    return {"result": "success"}


# 个人空间-应用发布到广场
@console_api.post("/apps/{app_id}/audit/public")
async def app_published_to_public_audit(app_id: str,
                                        request: Request,
                                        app_service: AppService = Depends(AppService),
                                        current_user: Account = Depends(login_user)):
    app_model = await get_app_model_async(app_id=app_id, mode=None)
    param = await request.json()

    need_publish_tool = bool(param.get('need_publish_tool'))
    tool_param = None
    if need_publish_tool:
        tool_param = param.get('tool_param')
    await app_service.published_audit_main(app_id=app_id, current_user=current_user, msg=param['msg'],
                                           workspace_id=agent_platform_config.GLOBAL_TENANT_ID,
                                           app_type=app_model.mode,
                                           application_type=ApplicationType.PUBLIC.value, desc=param['desc'],
                                           need_publish_tool=param['need_publish_tool'],
                                           tool_param=tool_param)
    return {"result": "success"}


# 个人空间-应用发布到共享广场
@console_api.post("/apps/{app_id}/audit/share_public")
async def app_published_to_public_audit(app_id: str,
                                        request: Request,
                                        app_service: AppService = Depends(AppService),
                                        current_user: Account = Depends(login_user)):
    app_model = await get_app_model_async(app_id=app_id, mode=None)
    param = await request.json()

    need_publish_tool = bool(param.get('need_publish_tool'))
    tool_param = None
    if need_publish_tool:
        tool_param = param.get('tool_param')
    await app_service.published_audit_main(app_id=app_id, current_user=current_user, msg=param['msg'],
                                           workspace_id=agent_platform_config.GLOBAL_TENANT_ID,
                                           app_type=app_model.mode,
                                           application_type=ApplicationType.SHARE.value, desc=param['desc'],
                                           need_publish_tool=param['need_publish_tool'],
                                           tool_param=tool_param)
    return {"result": "success"}


# todo 刷数据用的接口
@console_api.get("/user/permission/flush/data")
async def user_super_permissions_flush_data(app_service: AppService = Depends(AppService)):
    return await app_service.user_super_permissions_flush_data()


@console_api.get("/tenant/get/current/user/tenants")
async def get_current_user_tenants(current_user: Account = Depends(login_user),
                                   app_service: AppService = Depends(AppService)):
    return await app_service.get_current_user_tenants_async(current_user)


# 项目空间-应用发布到项目空间请求
@console_api.post("/app/{app_id}/public/workspace/audit")
async def workspace_app_public_audit(app_id: str, request: Request,
                                     app_service: AppService = Depends(AppService),
                                     current_user: Account = Depends(login_user)):
    app_model = await get_app_model_async(app_id=app_id, mode=None)
    param = await request.json()

    need_publish_tool = bool(param.get('need_publish_tool'))
    tool_param = None
    if need_publish_tool:
        tool_param = param.get('tool_param')
    # await app_service.published_audit_main(app_id=app_id, current_user=current_user, msg=param['msg'],
    #                                        workspace_id=param['workspace_id'], app_type=app_model.mode,
    #                                        application_type=ApplicationType.PROJECT.value, desc=param['desc'],
    #                                        need_publish_tool=param['need_publish_tool'], tool_param=tool_param)
    if app_model.mode == AppMode.TOOL.value:
        await app_service.publish_tool(app_id, "", app_model.tenant_id, param['desc'])
    else:
        # 应用发布到广场/项目空间
        await app_service.app_published_main(app_id, ApplicationType.PROJECT.value,
                                             app_model.tenant_id,
                                             param['desc'],
                                             need_publish_tool,
                                             tool_param)
    return {"result": "success"}


# 项目空间-工具发布到项目空间请求
@console_api.post("/tools/{app_id}/public/workspace/audit")
async def workspace_tool_public_audit(app_id: str, request: Request,
                                      app_service: AppService = Depends(AppService),
                                      current_user: Account = Depends(login_user)):
    param = await request.json()
    # await app_service.published_audit_main(app_id=app_id, current_user=current_user, msg=param['msg'],
    #                                        workspace_id=param['workspace_id'],
    #                                        app_type=AppMode.TOOL.value, application_type=ApplicationType.PROJECT.value,
    #                                        desc=param['desc'])
    await app_service.publish_tool(app_id, "", param['workspace_id'], param['desc'])

    return {"result": "success"}


# 大模型-发布到项目空间申请请求
@console_api.post("/models/public/workspace/audit")
async def workspace_model_public_audit(request: Request,
                                       app_service: AppService = Depends(AppService),
                                       current_user: Account = Depends(login_user), ):
    param = await request.json()
    logger.info("请求参数===============================")
    logger.info(param)
    logger.info("请求参数===============================")
    if param['application_type'] == 'public':
        param['workspace_id'] = '7956bb7d-10d3-4551-9ad5-3303cccccccc'
    await app_service.published_audit_main(app_id='927c9ca3-6d0a-4033-8e14-3303aaaaaaaa', current_user=current_user,
                                           msg=param['msg'],
                                           workspace_id=param['workspace_id'],
                                           app_type=AppMode.BIGMODEL.value, application_type=param['application_type'],
                                           desc=param['desc'], need_publish_tool=param['need_publish_tool'],
                                           tool_param=param['tool_param'])

    return {"result": "success"}


# 批量刷草稿数据
# @console_api.post("/copyToDraftAll")
async def copy_to_draft_all(app_service: AppService = Depends(AppService),
                            current_user: Account = Depends(login_user)):
    await app_service.copy_to_draft_all()


# 批量刷草稿数据
# @console_api.post("/copyToDraft")
async def copy_to_draft(request: Request,
                        app_service: AppService = Depends(AppService),
                        current_user: Account = Depends(login_user)):
    param = await request.json()
    await app_service.copy_to_draft(param['app_id'])


@console_api.get("/global-apps", response_model=AppPaginationResp)
async def global_app_list_api_get(page: int, limit: int,
                                  mode: Optional[str] = None, name: Optional[str] = None,
                                  tag_ids: Optional[str] = None,
                                  app_service: AppService = Depends(AppService),
                                  current_user: Account = Depends(login_user)):
    """Get app list"""
    args = {'page': page, 'limit': limit, 'mode': mode, 'name': name, 'tag_ids': tag_ids,
            'status': AppStatus.PUBLISHED.value,
            'tenant_id': agent_platform_config.GLOBAL_TENANT_ID}
    return await app_service.get_paginate_apps_async(current_user, args)


@console_api.get("/global-share-apps", response_model=AppPaginationResp)
async def global_share_app_list_api_get(page: int, limit: int,
                                        mode: Optional[str] = None, name: Optional[str] = None,
                                        tag_ids: Optional[str] = None,
                                        app_service: AppService = Depends(AppService),
                                        current_user: Account = Depends(login_user)):
    """Get app list"""
    args = {'page': page, 'limit': limit, 'mode': mode, 'name': name, 'tag_ids': tag_ids,
            'status': AppStatus.PENDING.value,
            'tenant_id': agent_platform_config.GLOBAL_TENANT_ID}
    return await app_service.get_paginate_share_apps_async(current_user, args)


@console_api.post("/app/{app_id}/update/name")
async def update_app_name(app_id: str, request: Request,
                          session: AsyncSession = Depends(DbUtils.get_db_async_session), ):
    app_model = await get_app_model_async(app_id=app_id, mode=None)
    param = await request.json()
    app_model.name = param['name']
    session.add(app_model)
    await session.commit()
    await async_redis_client.delete(f"agent_platform_app_by_app_id: {app_model.id}")
    return {"result": "success"}


@console_api.get("/app/{app_id}/check_app_is_can_edit")
async def check_app_is_can_edit(app_id: str, current_user: Account = Depends(login_user)):
    value_byte = await async_redis_client.get(f"THE_APP_IS_EDITING:{app_id}")
    if value_byte and value_byte.decode() != current_user.id:
        return {"result": "error", "detail": "当前应用正在被编辑中，请稍后再试"}
    else:
        return {"result": "success"}
    # value_user = await async_redis_client.delete(f"THE_APP_IS_EDITING:{app_id}_USER_ID:{current_user.id}")
    # if value and not value_user:
    #     return {"result": "error", "detail": "当前应用正在被编辑中，请稍后再试"}
    # return {"result": "success"}


@console_api.get("/app/{app_id}/delete_app_is_using")
async def delete_app_is_using(app_id: str, current_user: Account = Depends(login_user)):
    value_byte = await async_redis_client.get(f"THE_APP_IS_EDITING:{app_id}")
    # 检查是否有锁
    if value_byte:
        # 检查锁是不是自己的
        if value_byte.decode() == current_user.id:
            await async_redis_client.delete(f"THE_APP_IS_EDITING:{app_id}")
            return {"result": "success"}
        else:
            return {"result": "error", "detail": "当前用户无法删除app使用缓存"}
    else:
        return {"result": "success", "detail": "当前app没有使用缓存"}
    # value_user = await async_redis_client.delete(f"THE_APP_IS_EDITING:{app_id}_USER_ID:{current_user.id}")
    # if value and not value_user:
    #     return {"result": "error", "detail": "当前用户无法删除app使用缓存"}
    #
    # await async_redis_client.delete(f"THE_APP_IS_EDITING:{app_id}")
    # await async_redis_client.delete(f"THE_APP_IS_EDITING:{app_id}_USER_ID:{current_user.id}")
    # return {"result": "success"}


@console_api.get("/app/{app_id}/keep_app_is_editing")
async def keep_app_is_editing(app_id: str, current_user: Account = Depends(login_user)):
    value_byte = await async_redis_client.get(f"THE_APP_IS_EDITING:{app_id}")
    # 检查redis有没有上锁或者锁是自己的
    if not value_byte or value_byte.decode() == current_user.id:
        # 前端每30秒发起一次, 设置为35秒过期
        await async_redis_client.set(f"THE_APP_IS_EDITING:{app_id}", current_user.id,
                                     ex=35)
        return {"result": "success"}
    else:
        return {"result": "someone else is editing"}
    # value_user = await async_redis_client.delete(f"THE_APP_IS_EDITING:{app_id}_USER_ID:{current_user.id}")
    # if not value or (value and value_user):
    #     await async_redis_client.set(f"THE_APP_IS_EDITING:{app_id}", '1',
    #                                  ex=35)
    #     await async_redis_client.set(f"THE_APP_IS_EDITING:{app_id}_USER_ID:{current_user.id}", '1',
    #                                  ex=35)
    # return {"result": "success"}


# 根据体验，订阅，点赞最高排序
# count_type: "like_count", "experience_count",
# is_hot_rank: false 为最新排序
# mode: "agent-chat", "workflow"
# app_type: (“通用”，“办公助手”，“业务场景”)
@console_api.get("/global-apps/rank", response_model=AppPaginationResp)
async def global_app_list_api_get_by_rank(page: int, limit: int, is_hot_rank: bool = True,
                                  count_type: Optional[str] = None,
                                  mode: str = "agent-chat",
                                  app_type: Optional[str] = None,
                                  name: Optional[str] = None,
                                  tag_ids: Optional[str] = None,
                                  app_service: AppService = Depends(AppService),
                                  current_user: Account = Depends(login_user)):
    """Get app list"""
    args = {'page': page, 'limit': limit, 'is_hot_rank': is_hot_rank,'count_type' :count_type,
            "app_type":app_type, 'mode': mode, 'name': name, 'tag_ids': tag_ids,
            'status': AppStatus.PUBLISHED.value,
            'tenant_id': agent_platform_config.GLOBAL_TENANT_ID}
    return await app_service.get_paginate_apps_by_rank_async(current_user, args)



# 体验，订阅，点赞埋点
# count_type: "like_count", "experience_count"
# addValue: 1, -1
@console_api.get("/app/edit-count")
async def app_edit_count(app_id: str, count_type: str, add_value: int, mode: str = "agent-chat",
                                app_service: AppService = Depends(AppService),
                                current_user: Account = Depends(login_user)):
    args = {'app_id': app_id, 'mode': mode, 'count_type': count_type, 'add_value': add_value,
            'app_service': app_service,
            'tenant_id': agent_platform_config.GLOBAL_TENANT_ID}
    return await app_service.edit_count(current_user, args)


# 查看详情,返回新增字段是否点赞
@console_api.get("/app/get-specifics")
async def app_get_specifics(app_id: str, mode: str = "agent-chat",
                            app_service: AppService = Depends(AppService),
                            current_user: Account = Depends(login_user)):
    args = {'app_id': app_id,
            'mode': mode,
            'app_service': app_service}
    return await app_service.get_app_specifics(current_user, args)
