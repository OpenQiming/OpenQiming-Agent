import asyncio
import json
import logging
import time

from starlette.websockets import WebSocketDisconnect

from agent_platform_basic.exceptions.services.user_permissions import UserPermissionError
from agent_platform_basic.libs.redis_utils import MutexAcquireError
from agent_platform_basic.models.db_model import Account
from agent_platform_common.constants.metabolic_redis_const import ANSWER_NODE_OUTPUT_PREFIX, \
    MESSAGE_FROM_WORKFLOW_PREFIX, MESSAGE_FROM_AGENT_PREFIX, SHUTDOWN_ALL_AGENT_PREFIX
from agent_platform_metabolic.schema import Message
from flask import request
from flask_restful import Resource, marshal_with, reqparse
from fastapi import WebSocket, Depends, HTTPException, status
from agent_platform_basic.exceptions.base_http_exception import InternalServerError, NotFound
from agent_platform_basic.exceptions.base_http_exception import Forbidden

from agent_platform_basic.exceptions.controllers.console.app import (
    ConversationCompletedError,
    DraftWorkflowNotExist,
    DraftWorkflowNotSync
)
from agent_platform_basic.exceptions.services.app import WorkflowHashNotEqualError
from agent_platform_basic.exceptions.services.conversation import (
    ConversationNotExistsError,
    ConversationCompletedError
)
from fastapi import Request
from agent_platform_basic.libs import helper
from agent_platform_basic.libs.aes import decrypt_data_from_base64
from agent_platform_basic.libs.helper import uuid_value
from agent_platform_basic.libs.login import current_user, login_required
from agent_platform_core.app.apps.base_app_queue_manager import AppQueueManager
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.models.db_model.model import App
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_metabolic.actions import UserRequirement
from agent_platform_metabolic.hand_made_agents.envs.metabolic_env import MetabolicEnv
from agent_platform_common.constants.metabolic_redis_const import MESSAGE_FROM_WORKFLOW_PREFIX, \
    MESSAGE_FROM_AGENT_PREFIX, SHUTDOWN_ALL_AGENT_PREFIX, ANSWER_NODE_OUTPUT_PREFIX
from agent_platform_metabolic.hand_made_agents.roles.account_agent import AccountAgent
from agent_platform_metabolic.hand_made_agents.roles.fault_report_agent import FaultReportAgent
from agent_platform_metabolic.hand_made_agents.roles.solution_confirm_agent import SolutionConfirmAgent
from agent_platform_metabolic.hand_made_agents.roles.sigma_agent import SigmaAgent
from agent_platform_service.controllers.console import api, console_api
from agent_platform_service.controllers.console.app.wraps import get_app_model, get_app_model_async
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.fastapi_fields.req.console.workflow_req import DraftWorkflowRunReq, DraftWorkflowImportReq, \
    DraftChatflowRunReq
from agent_platform_service.fields.workflow_fields import workflow_fields
from agent_platform_service.fields.workflow_run_fields import workflow_run_node_execution_fields
from agent_platform_service.fastapi_fields.resp.console.workflow_resp import WorkflowResponse, DraftWorkflowApiPostResp, \
    PublishedWorkflowApiPostResp, WorkflowRunNodeExecutionResp
from agent_platform_service.fastapi_fields.resp.console.websocket_metabolic_resp import WebsocketMetabolicResp
from agent_platform_service.services.async_app_generate_service import AsyncAppGenerateService
from agent_platform_service.services.app_generate_service import AppGenerateService
from agent_platform_service.services.app_yaml_service import AppYamlService
from agent_platform_service.services.auth.user_permissions_service import UserPermissionsService
from agent_platform_service.services.auth_service import login_user
from agent_platform_service.services.workflow_service import WorkflowService
from sqlalchemy.ext.asyncio import AsyncSession
from agent_platform_basic.libs import DbUtils

from agent_platform_core.factories import variable_factory

# from agent_platform_core.errors.error import AppInvokeQuotaExceededError

logger = logging.getLogger(__name__)


@console_api.get("/apps/{app_id}/workflows/draft", response_model=WorkflowResponse,
                 summary="获取 workflow 草稿",
                 description="根据 app_id  获取 workflow 草稿",
                 tags=["workflow"])
async def draft_workflow_api_get(app_id: str,
                                 user: Account = Depends(login_user),
                                 session: AsyncSession = Depends(DbUtils.get_db_async_session),
                                 workflow_service: WorkflowService = Depends(WorkflowService),
                                 user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    #
    # try:
    #     await user_permissions_service.check_user_read_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'draft_workflow_api_get.check_user_read_auth: {e}')
    #     raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC])

    # if not user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    workflow = await workflow_service.get_draft_workflow_async(app_model=app_model)

    if not workflow:
        raise DraftWorkflowNotExist()

    return await WorkflowResponse.from_workflow(workflow=workflow, session=session)


@console_api.post("/apps/{app_id}/workflows/draft", response_model=DraftWorkflowApiPostResp,
                  summary="创建或更新 workflow 草稿",
                  description="创建或更新 workflow 草稿",
                  tags=["workflow"])
async def draft_workflow_api_post(app_id: str,
                                  request: Request,
                                  user: Account = Depends(login_user),
                                  workflow_service: WorkflowService = Depends(WorkflowService),
                                  user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)
                                  ):

    #获取app
    app_model = await get_app_model_async(
        app_id=app_id,
        mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC]
    )

    content_type = request.headers.get('Content-Type', '')

    if 'application/json' in content_type:
        args = await request.json()
        '''
        # TODO: set this to required=True after frontend is updated
        parser.add_argument('environment_variables', type=list, required=False, location='json')
        '''
    elif 'text/plain' in content_type:
        try:
            data = await request.body()  # 异步读取请求体
            decoded_data = data.decode('utf-8')  # 解码为UTF-8字符串
            param = json.loads(decoded_data)  # 将字符串解析为JSON

            if 'graph' not in param or 'features' not in param:
                raise ValueError('graph or features not found in data')

            if not isinstance(param.get('graph'), dict) or not isinstance(param.get('features'), dict):
                raise ValueError('graph or features is not a dict')

            args = {
                "graph": param.get("graph"),
                "features": param.get("features"),
                "hash": param.get("hash"),
                "environment_variables": param.get("environment_variables"),
                "conversation_variables": param.get("conversation_variables"),
            }
        except json.JSONDecodeError:
            return {"message": "Invalid JSON data"}, 400
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported Media Type"
        )

    try:
        #环境变量
        environment_variables_list = args.get("environment_variables") or []
        environment_variables = [
            variable_factory.build_environment_variable_from_mapping(obj) for obj in environment_variables_list
        ]
        #会话变量
        conversation_variables_list = args.get("conversation_variables") or []
        conversation_variables = [
            variable_factory.build_conversation_variable_from_mapping(obj) for obj in conversation_variables_list
        ]

        workflow = await workflow_service.sync_draft_workflow_async(
            app_model=app_model,
            graph=args['graph'],
            features=args['features'],
            workflow_id=args.get('workflow_id', None),
            account=user,
            environment_variables=environment_variables,
            conversation_variables=conversation_variables,
        )
    except WorkflowHashNotEqualError:
        raise DraftWorkflowNotSync()
    return {
        "result": "success",
        "hash": workflow.unique_hash,
        "updated_at": int(workflow.updated_at.timestamp() if workflow.updated_at else workflow.created_at.timestamp())
    }


@console_api.post("/apps/{app_id}/workflows/history")
async def get_history_workflows_async(app_id: str,
                                      current_user: Account = Depends(login_user),
                                      workflow_service: WorkflowService = Depends(WorkflowService)):
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC])
    if not current_user.is_tenant_user(app_model.tenant_id):
        raise Forbidden()
    return await workflow_service.get_history_workflows(app_id)


@console_api.get("/apps/{app_id}/workflows/history/info/{workflow_id}")
async def draft_history_workflow_api_get(app_id: str, workflow_id: str,
                                         user: Account = Depends(login_user),
                                         session: AsyncSession = Depends(DbUtils.get_db_async_session),
                                         workflow_service: WorkflowService = Depends(WorkflowService),
                                         user_permissions_service: UserPermissionsService = Depends(
                                             UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    #
    # try:
    #     await user_permissions_service.check_user_read_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'draft_workflow_api_get.check_user_read_auth: {e}')
    #     raise Forbidden()

    # if not user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    workflow = await workflow_service.get_enabled_draft_workflow_by_id_async(workflow_id)

    if not workflow:
        raise DraftWorkflowNotExist()

    return await WorkflowResponse.from_workflow(workflow=workflow, session=session)




@console_api.post("/apps/{app_id}/workflows/draft/import", response_model=WorkflowResponse,
                  summary="导入 workflow",
                  description="导入DSL创建 workflow 草稿",
                  tags=["workflow"])
async def draft_workflow_import_api(app_id: str, request_body: DraftWorkflowImportReq,
                                    session: AsyncSession = Depends(DbUtils.get_db_async_session),
                                    user: Account = Depends(login_user),
                                    app_yaml_service: AppYamlService = Depends(AppYamlService),
                                    user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'draft_workflow_import_api.check_user_edit_auth: {e}')
    #     raise Forbidden()

    """
    Import draft workflow
    """
    # 获取应用模型
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC])

    # if not user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()

    # 解密
    decrypted_data_dict = decrypt_data_from_base64(request_body.data)

    # 导入工作流草稿
    workflow = await app_yaml_service.import_and_overwrite_workflow(
        app_model=app_model, data=decrypted_data_dict, account=user
    )

    return await WorkflowResponse.from_workflow(workflow, session)


class DraftWorkflowImportApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC])
    @marshal_with(workflow_fields)
    def post(self, app_model: App):
        """
        Import draft workflow
        """
        # The role of the current user in the ta table must be admin, owner, or editor
        if not current_user.is_tenant_editor(app_model.tenant_id):
            raise Forbidden()

        parser = reqparse.RequestParser()
        parser.add_argument('data', type=str, required=True, nullable=False, location='json')
        args = parser.parse_args()

        workflow_service = WorkflowService()
        workflow = workflow_service.import_draft_workflow(
            app_model=app_model,
            data=args['data'],
            account=current_user
        )

        return workflow


class AdvancedChatDraftWorkflowRunApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.ADVANCED_CHAT])
    async def post(self, app_model: App):
        """
        Run draft workflow
        """
        # The role of the current user in the ta table must be admin, owner, or editor
        if not current_user.is_tenant_editor(app_model.tenant_id):
            raise Forbidden()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, location='json')
        parser.add_argument('query', type=str, required=True, location='json', default='')
        parser.add_argument('files', type=list, location='json')
        parser.add_argument('conversation_id', type=uuid_value, location='json')
        args = parser.parse_args()

        try:
            response = await AsyncAppGenerateService.generate(
                app_model=app_model,
                user=current_user,
                args=args,
                invoke_from=InvokeFrom.DEBUGGER,
                streaming=True
            )
            print("response::::", response)

            return await helper.async_compact_generate_response(response)
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except ConversationCompletedError:
            raise ConversationCompletedError()
        except ValueError as e:
            raise e
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()

@console_api.post("/apps/{app_id}/advanced-chat/workflows/draft/run",
                  summary="启动 chatflow",
                  description="启动 chatflow",
                  tags=["chatflow"])
async def draft_chat_workflow_run_api_post(app_id,
                                      request_body: DraftChatflowRunReq,
                                      session: AsyncSession = Depends(DbUtils.get_db_async_session),
                                      current_user: Account = Depends(login_user),
                                      async_app_generate_service: AsyncAppGenerateService = Depends(
                                          AsyncAppGenerateService)):
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.ADVANCED_CHAT])

    await session.close()
    invoke_from = InvokeFrom.DEBUGGER
    try:
        response = await async_app_generate_service.generate(
            app_model=app_model,
            user=current_user,
            args=request_body.model_dump(),
            invoke_from=invoke_from,
            streaming=True
        )

        return await helper.async_compact_generate_response(response)
    except ConversationNotExistsError:
        raise NotFound("Conversation Not Exists.")
    except ConversationCompletedError:
        raise ConversationCompletedError()
    except ValueError as e:
        raise e
    except Exception as e:
        logging.exception("internal server error.")
        raise InternalServerError()


class AdvancedChatDraftRunIterationNodeApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.ADVANCED_CHAT])
    def post(self, app_model: App, node_id: str):
        """
        Run draft workflow iteration node
        """
        # The role of the current user in the ta table must be admin, owner, or editor
        if not current_user.is_tenant_editor(app_model.tenant_id):
            raise Forbidden()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, location='json')
        args = parser.parse_args()

        try:
            response = AppGenerateService.generate_single_iteration(
                app_model=app_model,
                user=current_user,
                node_id=node_id,
                args=args,
                streaming=True
            )

            return helper.compact_generate_response(response)
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except ConversationCompletedError:
            raise ConversationCompletedError()
        except ValueError as e:
            raise e
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()


class WorkflowDraftRunIterationNodeApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.WORKFLOW, AppMode.METABOLIC])
    def post(self, app_model: App, node_id: str):
        """
        Run draft workflow iteration node
        """
        # The role of the current user in the ta table must be admin, owner, or editor
        if not current_user.is_tenant_editor(app_model.tenant_id):
            raise Forbidden()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, location='json')
        args = parser.parse_args()

        try:
            response = AppGenerateService.generate_single_iteration(
                app_model=app_model,
                user=current_user,
                node_id=node_id,
                args=args,
                streaming=True
            )

            return helper.compact_generate_response(response)
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except ConversationCompletedError:
            raise ConversationCompletedError()
        except ValueError as e:
            raise e
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()


@console_api.post("/apps/{app_id}/workflows/draft/run",
                  summary="启动 workflow",
                  description="启动 workflow",
                  tags=["workflow"])
async def draft_workflow_run_api_post(app_id,
                                      request_body: DraftWorkflowRunReq,
                                      session: AsyncSession = Depends(DbUtils.get_db_async_session),
                                      current_user: Account = Depends(login_user),
                                      async_app_generate_service: AsyncAppGenerateService = Depends(
                                          AsyncAppGenerateService),
                                      user_permissions_service: UserPermissionsService = Depends(
                                          UserPermissionsService)):
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'draft_workflow_run_api_post.check_user_edit_auth: {e}')
    #     raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.WORKFLOW])
    await session.close()
    invoke_from = InvokeFrom.DEBUGGER
    try:
        response = await async_app_generate_service.generate(
            app_model=app_model,
            user=current_user,
            args=request_body.model_dump(),
            invoke_from=invoke_from,
            streaming=True
        )
        # response = await async_app_generate_service.generate(
        #     app_model=app_model,
        #     user=current_user,
        #     args=request_body.model_dump(),
        #     invoke_from=InvokeFrom.DEBUGGER,
        #     streaming=True
        # )

        return await helper.async_compact_generate_response(response)
    except ValueError as e:
        raise e
    except Exception as e:
        logging.exception("internal server error.")
        raise InternalServerError()

    pass


class DraftWorkflowRunApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.WORKFLOW, AppMode.METABOLIC])
    def post(self, app_model: App):
        """
        Run draft workflow
        """
        # The role of the current user in the ta table must be admin, owner, or editor
        if not current_user.is_tenant_editor(app_model.tenant_id):
            raise Forbidden()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, required=True, nullable=False, location='json')
        parser.add_argument('files', type=list, required=False, location='json')
        args = parser.parse_args()

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=current_user,
                args=args,
                invoke_from=InvokeFrom.DEBUGGER,
                streaming=True
            )

            return helper.compact_generate_response(response)
        except ValueError as e:
            raise e
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()


class WorkflowTaskStopApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC])
    def post(self, app_model: App, task_id: str):
        """
        Stop workflow task
        """
        # The role of the current user in the ta table must be admin, owner, or editor
        if not current_user.is_tenant_editor(app_model.tenant_id):
            raise Forbidden()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.DEBUGGER, current_user.id)

        return {
            "result": "success"
        }


@console_api.post("/apps/{app_id}/workflows/draft/nodes/{node_id}/run", response_model=WorkflowRunNodeExecutionResp,
                  summary="启动 workflow 中的 node",
                  description="根据 app_id 和 node_id 启动 workflow 中的 node",
                  tags=["workflow"])
async def draft_workflow_node_run_api_post(app_id: str, node_id: str, request_body: DraftWorkflowRunReq,
                                           current_user=Depends(login_user),
                                           workflow_service: WorkflowService = Depends(WorkflowService),
                                           user_permissions_service: UserPermissionsService = Depends(
                                               UserPermissionsService)
                                           ):
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'draft_workflow_node_run_api_post.check_user_edit_auth: {e}')
    #     raise Forbidden()

    """
    Run draft workflow node
    """
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC])

    # The role of the current user in the ta table must be admin, owner, or editor
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()

    workflow_node_execution = await workflow_service.async_run_draft_workflow_node(
        app_model=app_model,
        node_id=node_id,
        user_inputs=request_body.inputs,
        account=current_user
    )

    return workflow_node_execution


@console_api.get("/apps/{app_id}/workflows/publish", response_model=WorkflowResponse,
                 summary="获取发布状态的 workflow",
                 description="根据 app_id 获取发布状态的 workflow",
                 tags=["workflow"])
async def published_workflow_api_get(app_id: str,
                                     current_user: Account = Depends(login_user),
                                     session: AsyncSession = Depends(DbUtils.get_db_async_session),
                                     workflow_service: WorkflowService = Depends(WorkflowService),
                                     user_permissions_service: UserPermissionsService = Depends(
                                         UserPermissionsService)):
    # is_super_admin_read = await user_permissions_service.check_user_is_super_admin_read_auth(current_user.employee_number)
    # if not is_super_admin_read:
    #     raise Forbidden()
    #
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'published_workflow_api_get.check_user_edit_auth: {e}')
    #     raise Forbidden()
    """
    Get published workflow
    """
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC])

    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()

    workflow = await workflow_service.get_published_workflow_async(app_model=app_model)

    return await WorkflowResponse.from_workflow(workflow=workflow, session=session)


@console_api.post("/apps/{app_id}/workflows/publish", response_model=PublishedWorkflowApiPostResp,
                  summary="发布 workflow",
                  description="发布 workflow",
                  tags=["workflow"])
async def published_workflow_api_post(app_id: str,
                                      current_user: Account = Depends(login_user),
                                      workflow_service: WorkflowService = Depends(WorkflowService),
                                      user_permissions_service: UserPermissionsService = Depends(
                                          UserPermissionsService)):
    # is_super_admin_edit = await user_permissions_service.check_user_is_super_admin_edit_auth(
    #     current_user.employee_number)
    # if not is_super_admin_edit:
    #     raise Forbidden()
    #
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_edit_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'published_workflow_api_post.check_user_edit_auth: {e}')
    #     raise Forbidden()
    """
    Publish workflow
    """
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC])

    # The role of the current user in the ta table must be admin, owner, or editor
    # if not current_user.is_tenant_admin_or_owner(app_model.tenant_id):
    #     raise Forbidden()

    workflow = await workflow_service.publish_workflow_async(app_model=app_model,
                                                             account=current_user)

    return {
        "result": "success",
        "created_at": int(workflow.created_at.timestamp())
    }


@console_api.get("/apps/{app_id}/workflows/default-workflow-block-configs",
                 summary="获取 workflow 的节点默认配置",
                 description="获取 workflow 的节点默认配置",
                 tags=["workflow"])
async def default_block_configs_api_get(app_id: str, current_user: Account = Depends(login_user)):
    # is_super_admin_read = await user_permissions_service.check_user_is_super_admin_read_auth(current_user.employee_number)
    # if not is_super_admin_read:
    #     raise Forbidden()
    #
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()
    # try:
    #     await user_permissions_service.check_user_read_auth(current_user.employee_number, app_id)
    # except UserPermissionError as e:
    #     logger.error(f'default_block_configs_api_get.check_user_edit_auth: {e}')
    #     raise Forbidden()

    # The role of the current user in the ta table must be admin, owner, or editor
    # if not current_user.is_tenant_editor(app_model.tenant_id):
    #     raise Forbidden()

    workflow_service = WorkflowService()
    return workflow_service.get_default_block_configs()


@console_api.get("/apps/{app_id}/workflows/default-workflow-block-configs/{block_type}",
                  summary="获取某个类型的 node 的默认配置",
                  description="获取某个类型的 node 的默认配置",
                  tags=["workflow"])
async def default_block_config_api_get(app_id: str,
                                       block_type: str,
                                       request: Request,
                                       current_user: Account = Depends(login_user),
                                       ):
    # app_model = await get_app_model_async(app_id=app_id,
    #                                       session=session,
    #                                       mode=[AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC])
    # if not current_user.is_tenant_user(app_model.tenant_id):
    #     raise Forbidden()

    query_params = request.query_params

    filters = None
    if query_params.get('q'):
        try:
            filters = json.loads(query_params.get('q'))
        except json.JSONDecodeError:
            raise ValueError('Invalid filters')

    workflow_service = WorkflowService()
    return workflow_service.get_default_block_config(node_type=block_type,
                                                     filters=filters)


class ConvertToWorkflowApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.CHAT, AppMode.COMPLETION])
    def post(self, app_model: App):
        """
        Convert basic mode of chatbot app to workflow mode
        Convert expert mode of chatbot app to workflow mode
        Convert Completion App to Workflow App
        """
        # The role of the current user in the ta table must be admin, owner, or editor
        if not current_user.is_tenant_editor(app_model.tenant_id):
            raise Forbidden()

        if request.data:
            parser = reqparse.RequestParser()
            parser.add_argument('name', type=str, required=False, nullable=True, location='json')
            parser.add_argument('icon', type=str, required=False, nullable=True, location='json')
            parser.add_argument('icon_background', type=str, required=False, nullable=True, location='json')
            args = parser.parse_args()
        else:
            args = {}

        # convert to workflow mode
        workflow_service = WorkflowService()
        new_app_model = workflow_service.convert_to_workflow(
            app_model=app_model,
            account=current_user,
            args=args
        )

        # return app id
        return {
            'new_app_id': new_app_model.id,
        }


@console_api.websocket("/apps/{workflow_id}/ws/metabolic")
async def metabolic_websocket_endpoint(websocket: WebSocket, workflow_id: str, user: Account = Depends(login_user)):
    await websocket.accept()
    start = time.time()
    user_id = user.id

    metabolic_queue = asyncio.Queue()
    redis_label = f"{user_id}_{workflow_id}"
    env = MetabolicEnv(redis_label=redis_label, q=metabolic_queue)
    env.add_roles([SigmaAgent(), AccountAgent(), FaultReportAgent(),
                   SolutionConfirmAgent()])

    while True:
        # 120秒没有操作, 断开websocket
        if time.time() - start > 120:
            logger.info(f"用户{user_id}长时间未操作, websocket连接断开")
            await websocket.close()
            return
        user_input_content = None
        try:
            logger.debug("===============================================")
            logger.debug(f"user_id: {user_id}, receive_text")
            logger.debug(f"user_id: {user_id}, websocket client_state: {websocket.client_state}")
            logger.debug(f"user_id: {user_id}, websocket application_state: {websocket.application_state}")
            logger.debug("===============================================")
            user_input_content = await asyncio.wait_for(websocket.receive_text(), timeout=2)
            start = time.time()
        except WebSocketDisconnect:
            logger.warning("WebSocket connection closed unexpectedly")
            return
        except Exception as e:
            pass
        answer_node_output_key = f"{ANSWER_NODE_OUTPUT_PREFIX}:{redis_label}"
        logger.debug(f"redis get, answer_node_output_key, {answer_node_output_key}")
        answer_node_output = await env._get_and_delete(answer_node_output_key)
        if answer_node_output:
            resp = WebsocketMetabolicResp(type="answer_node_output", data=answer_node_output)
            logger.debug("===============================================")
            logger.debug(f"user_id: {user_id}, answer_node_output: send_text")
            logger.debug(f"user_id: {user_id}, websocket client_state: {websocket.client_state}")
            logger.debug(f"user_id: {user_id}, websocket application_state: {websocket.application_state}")
            logger.debug("===============================================")
            await websocket.send_text(resp.model_dump_json())
            start = time.time()

        workflow_message_key = f"{MESSAGE_FROM_WORKFLOW_PREFIX}:{redis_label}"
        agent_reply_message_key = f"{MESSAGE_FROM_AGENT_PREFIX}:{redis_label}"
        shutdown_message_key = f"{SHUTDOWN_ALL_AGENT_PREFIX}:{redis_label}"
        logger.debug(f"redis get, workflow_message_key, {workflow_message_key}")
        logger.debug(f"redis get, shutdown_message_key, {shutdown_message_key}")
        workflow_msg = await env._get_and_delete(workflow_message_key)
        shutdown_message = await env._get_and_delete(shutdown_message_key)

        if workflow_msg:
            workflow_message_json = json.loads(workflow_msg)
            env._process_message(workflow_message_json)
        if shutdown_message:
            shutdown_message_json = json.loads(shutdown_message)
            env._process_message(shutdown_message_json)
        if user_input_content:
            user_input_message = Message(content=user_input_content, cause_by=UserRequirement,
                                         send_to="SigmaAgent")
            env.publish_message(user_input_message)
        # 如果处于空闲状态，退出循环
        if env.is_idle:
            break

        # 异步执行角色任务
        futures = [role.run() for role in env.roles.values()]
        await asyncio.gather(*futures)

        logger.debug(f"is idle: {env.is_idle}")
        logger.debug(f"redis get, agent_reply_message_key, {agent_reply_message_key}")
        agent_reply = await env._get_and_delete(agent_reply_message_key)
        if agent_reply:
            resp = WebsocketMetabolicResp(type="multi_agent_output", data=agent_reply)
            logger.debug("===============================================")
            logger.debug(f"user_id: {user_id}, agent_reply: send_text")
            logger.debug(f"user_id: {user_id}, websocket client_state: {websocket.client_state}")
            logger.debug(f"user_id: {user_id}, websocket application_state: {websocket.application_state}")
            logger.debug("===============================================")
            await websocket.send_text(resp.model_dump_json())
            start = time.time()


api.add_resource(DraftWorkflowImportApi, '/apps/<uuid:app_id>/workflows/draft/import')
# api.add_resource(AdvancedChatDraftWorkflowRunApi, '/apps/<uuid:app_id>/advanced-chat/workflows/draft/run')
api.add_resource(WorkflowTaskStopApi, '/apps/<uuid:app_id>/workflow-runs/tasks/<string:task_id>/stop')
api.add_resource(AdvancedChatDraftRunIterationNodeApi,
                 '/apps/<uuid:app_id>/advanced-chat/workflows/draft/iteration/nodes/<string:node_id>/run')
api.add_resource(WorkflowDraftRunIterationNodeApi,
                 '/apps/<uuid:app_id>/workflows/draft/iteration/nodes/<string:node_id>/run')
api.add_resource(ConvertToWorkflowApi, '/apps/<uuid:app_id>/convert-to-workflow')
