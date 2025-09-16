from datetime import datetime, timezone

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from agent_platform_basic.exceptions.base_http_exception import Forbidden

from agent_platform_basic.exceptions.controllers.console.app import (
    DraftModelConfigNotExist,
)
from agent_platform_basic.libs import DbUtils
from agent_platform_basic.models.db_model import Account
from agent_platform_service.controllers.console import api, console_api
from agent_platform_service.fields.app_model_config_async import AppModelConfigAsync
from agent_platform_service.services.app_model_config_service import AppModelConfigService
from agent_platform_service.services.auth_service import login_user
from agent_platform_service.controllers.console.app.wraps import get_app_model_async
from agent_platform_service.fastapi_fields.req.console.agent_req import PublishAgentReq


@console_api.post("/apps/{app_id}/model-config")
async def model_config_resource_post(app_id: str, request_body: PublishAgentReq,
                                     current_user: Account = Depends(login_user),
                                     app_model_config_service: AppModelConfigService = Depends(
                                         AppModelConfigService)):
    app_model = await get_app_model_async(app_id=app_id, mode=None)

    new_app_model_config = await app_model_config_service.get_new_model_config_async(
        app_model,
        request_body.model_dump(),
        current_user.current_tenant_id
    )
    new_app_model_config.version = str(datetime.now().replace(tzinfo=None))
    await app_model_config_service.publish_model_config_async(app_model, current_user, new_app_model_config)

    return {'result': 'success'}


@console_api.get("/apps/{app_id}/model-config/draft")
async def draft_model_config_resource_get(app_id: str,
                                          current_user: Account = Depends(login_user),
                                          app_model_config_service: AppModelConfigService = Depends(
                                              AppModelConfigService),
                                          model_config_async_service: AppModelConfigAsync = Depends(
                                              AppModelConfigAsync)):
    """
    Get draft model config
    """
    # The role of the current user in the ta table must be admin, owner, or editor
    if not current_user.is_editor:
        raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id, mode=None)

    # fetch draft model config by app_model
    model_config = await app_model_config_service.get_draft_model_config_async(app_model,
                                                                               current_user.current_tenant_id)
    if not model_config:
        raise DraftModelConfigNotExist()

    model_config = await model_config_async_service.get_model_config_fields_async(model_config)
    return model_config


@console_api.post("/apps/{app_id}/model-config/draft")
async def draft_model_config_resource_post(app_id: str, request_body: PublishAgentReq,
                                           current_user: Account = Depends(login_user),
                                           app_model_config_service: AppModelConfigService = Depends(
                                               AppModelConfigService)):
    """Sync app model config"""

    app_model = await get_app_model_async(app_id=app_id, mode=None)

    # The role of the current user in the ta table must be admin, owner, or editor
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()

    new_app_model_config = await app_model_config_service.get_new_model_config_async(
        app_model,
        request_body.model_dump(),
        app_model.tenant_id
    )
    new_app_model_config.version = 'draft'
    new_app_model_config.version_created_by = current_user.id
    # await app_model_config_service.update_header_image_async(app_model, request_body.header_image,
    #                                                          request_body.name)
    await app_model_config_service.sync_draft_model_config_async(app_model, new_app_model_config,
                                                                 current_user.current_tenant_id)

    return {'result': 'success'}


@console_api.post("/apps/{app_id}/model-config/history")
async def get_history_model_config_async(app_id: str,
                                         current_user: Account = Depends(login_user),
                                         app_model_config_service: AppModelConfigService = Depends(
                                             AppModelConfigService)):
    app_model = await get_app_model_async(app_id=app_id, mode=None)
    if not current_user.is_tenant_user(app_model.tenant_id):
        raise Forbidden()
    return await app_model_config_service.get_history_model_config(app_id)


@console_api.get("/apps/{app_id}/model-config/history/info/{model_config_id}")
async def get_history_model_config_info_async(app_id: str, model_config_id: str,
                                              current_user: Account = Depends(login_user),
                                              app_model_config_service: AppModelConfigService = Depends(
                                                  AppModelConfigService),
                                              model_config_async_service: AppModelConfigAsync = Depends(
                                                  AppModelConfigAsync)):
    """
    Get draft model config
    """
    # The role of the current user in the ta table must be admin, owner, or editor
    if not current_user.is_editor:
        raise Forbidden()
    app_model = await get_app_model_async(app_id=app_id, mode=None)
    # fetch draft model config by app_model
    model_config = await app_model_config_service.get_draft_model_config_by_id_async(model_config_id, app_model)
    if not model_config:
        raise DraftModelConfigNotExist()

    model_config = await model_config_async_service.get_model_config_fields_async(model_config)
    return model_config


@console_api.post("/apps/{app_id}/model-config/publish")
async def publish_model_config_resource_post(app_id: str, request_body: PublishAgentReq,
                                             current_user: Account = Depends(login_user),
                                             app_model_config_service: AppModelConfigService = Depends(
                                                 AppModelConfigService)):
    app_model = await get_app_model_async(app_id=app_id, mode=None)

    new_app_model_config = await app_model_config_service.get_new_model_config_async(
        app_model,
        request_body.model_dump(),
        current_user.current_tenant_id
    )
    new_app_model_config.version = str(datetime.now().replace(tzinfo=None))
    # await app_model_config_service.update_header_image_async(app_model, request_body.model_dump().get('header_image'),
    #                                                          request_body.model_dump().get('name'))
    await app_model_config_service.publish_model_config_async(app_model, current_user, new_app_model_config)

    return {'result': 'success'}


@console_api.get("/apps/{app_id}/model-config/publish")
async def publish_model_config_resource_get(app_id: str,
                                            current_user: Account = Depends(login_user),
                                            app_model_config_service: AppModelConfigService = Depends(
                                                AppModelConfigService),
                                            model_config_async_service: AppModelConfigAsync = Depends(
                                                AppModelConfigAsync)):
    """
    Get published model config
    """
    # The role of the current user in the ta table must be admin, owner, or editor
    if not current_user.is_editor:
        raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id, mode=None)

    # fetch draft model config by app_model
    model_config = await app_model_config_service.get_draft_model_config_async(app_model,
                                                                               current_user.current_tenant_id)
    if not model_config:
        raise DraftModelConfigNotExist()

    model_config = await model_config_async_service.get_model_config_fields_async(model_config)
    return model_config
