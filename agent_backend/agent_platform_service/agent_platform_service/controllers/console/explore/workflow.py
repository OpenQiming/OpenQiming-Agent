import asyncio
import json
import logging
import time
import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect
from fastapi import WebSocket

from agent_platform_basic.exceptions.base_http_exception import (
    InternalServerError,
    Forbidden
)
from agent_platform_basic.exceptions.controllers.console.app import (
    CompletionRequestError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from agent_platform_basic.exceptions.controllers.console.explore import NotWorkflowAppError
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.libs import helper, DbUtils
from agent_platform_basic.libs.login import current_user
from agent_platform_basic.models.db_model import Account
from agent_platform_core import contexts
from agent_platform_core.app.apps.base_app_queue_manager import AppQueueManager
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_core.models.db_model.model import App
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_metabolic.actions import UserRequirement
from agent_platform_metabolic.hand_made_agents.envs.metabolic_env import MetabolicEnv
from agent_platform_metabolic.hand_made_agents.roles.account_agent import AccountAgent
from agent_platform_metabolic.hand_made_agents.roles.fault_report_agent import FaultReportAgent
from agent_platform_metabolic.hand_made_agents.roles.sigma_agent import SigmaAgent
from agent_platform_metabolic.hand_made_agents.roles.solution_confirm_agent import SolutionConfirmAgent
from agent_platform_metabolic.schema import Task, Message
from agent_platform_service.controllers.console import api, console_api
from agent_platform_service.controllers.console.app.wraps import get_app_model_async
from agent_platform_service.controllers.console.explore.wraps import async_get_published_app
from agent_platform_service.controllers.console.explore.wraps import InstalledAppResource
from agent_platform_service.fastapi_fields.req.console.workflow_req import DraftWorkflowRunReq
from agent_platform_service.fastapi_fields.resp.console.websocket_metabolic_resp import WebsocketMetabolicResp
from agent_platform_service.services.async_app_generate_service import AsyncAppGenerateService
from agent_platform_service.services.auth_service import login_user

logger = logging.getLogger(__name__)


# class InstalledAppWorkflowRunApi(InstalledAppResource):
#     def post(self, app_model: App):
#         """
#         Run workflow
#         """
#         app_mode = AppMode.value_of(app_model.mode)
#         if app_mode != AppMode.WORKFLOW:
#             raise NotWorkflowAppError()
#
#         parser = reqparse.RequestParser()
#         parser.add_argument('inputs', type=dict, required=True, nullable=False, location='json')
#         parser.add_argument('files', type=list, required=False, location='json')
#         args = parser.parse_args()
#
#         try:
#             response = AppGenerateService.generate(
#                 app_model=app_model,
#                 user=current_user,
#                 args=args,
#                 invoke_from=InvokeFrom.EXPLORE,
#                 streaming=True
#             )
#
#             return helper.compact_generate_response(response)
#         except ProviderTokenNotInitError as ex:
#             raise ProviderNotInitializeError(ex.description)
#         except QuotaExceededError:
#             raise ProviderQuotaExceededError()
#         except ModelCurrentlyNotSupportError:
#             raise ProviderModelCurrentlyNotSupportError()
#         except InvokeError as e:
#             raise CompletionRequestError(e.description)
#         except ValueError as e:
#             raise e
#         except Exception as e:
#             logging.exception("internal server error.")
#             raise InternalServerError()


@console_api.post("/explore-apps/{app_id}/workflows/run")
async def installed_app_workflow_run_api(app_id,
                                         request_body: DraftWorkflowRunReq,
                                         current_user: Account = Depends(login_user),
                                         async_app_generate_service: AsyncAppGenerateService = Depends(
                                             AsyncAppGenerateService)):
    """
    Run workflow
    """

    app_model = await async_get_published_app(app_id,
                                              mode=[AppMode.WORKFLOW])

    if not current_user.is_tenant_user(app_model.tenant_id):
        raise Forbidden()

    try:
        response = await async_app_generate_service.generate(
            app_model=app_model,
            user=current_user,
            args=request_body.model_dump(),
            invoke_from=InvokeFrom.EXPLORE,
            streaming=True
        )

        return await helper.async_compact_generate_response(response)
    except ProviderTokenNotInitError as ex:
        raise ProviderNotInitializeError(ex.description)
    except QuotaExceededError:
        raise ProviderQuotaExceededError()
    except ModelCurrentlyNotSupportError:
        raise ProviderModelCurrentlyNotSupportError()
    except InvokeError as e:
        raise CompletionRequestError(e.description)
    except ValueError as e:
        raise e
    except Exception as e:
        logging.exception("internal server error.")
        raise InternalServerError()


class InstalledAppWorkflowTaskStopApi(InstalledAppResource):
    def post(self, app_model: App, task_id: str):
        """
        Stop workflow task
        """
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode != AppMode.WORKFLOW:
            raise NotWorkflowAppError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.EXPLORE, current_user.id)

        return {
            "result": "success"
        }


@console_api.websocket("/explore-apps/{app_id}/ws/metabolic")
async def explore_metabolic_websocket_endpoint(websocket: WebSocket, app_id: str,
                                               user: Account = Depends(login_user),
                                               async_app_generate_service: AsyncAppGenerateService = Depends(
                                                   AsyncAppGenerateService)
                                               ):
    await websocket.accept()
    workflow_queue = asyncio.Queue()
    metabolic_queue = asyncio.Queue()
    try:
        app_model = await get_app_model_async(app_id=app_id,
                                              mode=[AppMode.METABOLIC])
    except Exception as e:
        logger.error(e)
        await websocket.close()
        return

    redis_label = str(uuid.uuid4())
    contexts.redis_label.set(redis_label)
    user_id = user.id

    env = MetabolicEnv(redis_label=redis_label, q=metabolic_queue)
    env.add_roles([SigmaAgent(), AccountAgent(), FaultReportAgent(),
                   SolutionConfirmAgent()])

    params = dict(websocket.query_params)

    async def start_workflow(query: str):
        # try:
        async for event in await async_app_generate_service.generate(
                app_model=app_model,
                user=user,
                args={"inputs": params, "query": query, "files": []},
                invoke_from=InvokeFrom.DEBUGGER,
                streaming=True
        ):
            logger.debug(f"put into queue, {event}")
            await workflow_queue.put(event)
        logger.debug("workflow queue ended")
        # 工作流结束时, start_workflow方法会put一个None至队列表示结束
        await workflow_queue.put(None)

    workflow_task_list: list[Task] = []

    async def process():
        start = time.time()
        workflow_ended = True
        while True:
            # 120秒没有操作, 断开websocket
            logger.debug(f"user_id: {user_id}, websocket client_state: {websocket.client_state}")
            if time.time() - start > 120:
                logger.info(f"用户{user_id}长时间未操作, websocket连接断开")
                await websocket.close()
                return

            # 工作流信息输出到websocket
            try:
                event = await asyncio.wait_for(workflow_queue.get(), timeout=0.1)
                if event is None:
                    # 工作流结束时, start_workflow方法会put一个None至队列表示结束
                    workflow_ended = True
                elif "event: " in event:
                    """event: ping\n\n"""
                    pass
                else:
                    """data: {xxxx}\n\n"""
                    event_list = event.split("data:")
                    event_json = json.loads(event_list[1])
                    workflow_resp = WebsocketMetabolicResp(type="workflow", data=event_json)
                    await websocket.send_text(workflow_resp.model_dump_json())
                    start = time.time()
                    # 直接回复节点额外封装输出到websocket
                    if event_json["event"] == "node_finished" and event_json["data"]["node_type"] == "answer":
                        answer = event_json["data"]["outputs"]["output"]
                        answer_node_output_resp = WebsocketMetabolicResp(type="answer_node_output", data=answer)
                        await websocket.send_text(answer_node_output_resp.model_dump_json())
                        start = time.time()
                    # 智能体节点发送信息到metabolic
                    if event_json["event"] == "node_message":
                        workflow_message = WebsocketMetabolicResp(type="node_message",
                                                                  data=event_json["data"]["message"])
                        env._process_message(workflow_message.data)
            except asyncio.TimeoutError:
                pass

            user_input_content = None
            try:
                user_input_content = await asyncio.wait_for(websocket.receive_text(), timeout=0.1)
                start = time.time()
            except WebSocketDisconnect:
                logger.warning("WebSocket connection closed unexpectedly")
                return
            except asyncio.TimeoutError:
                pass
            if user_input_content:
                if workflow_ended:
                    current_workflow_task = asyncio.create_task(start_workflow(user_input_content))
                    workflow_task_list.append(current_workflow_task)
                    workflow_ended = False
                user_input_message = Message(content=user_input_content, cause_by=UserRequirement,
                                             send_to="SigmaAgent")
                env.publish_message(user_input_message)
            # 如果处于空闲状态，退出循环
            if env.is_idle:
                break

            # 异步执行角色任务
            futures = [role.run() for role in env.roles.values()]
            await asyncio.gather(*futures)

            # 多智能体信息输出到websocket
            try:
                agent_reply = await asyncio.wait_for(metabolic_queue.get(), timeout=0.1)
                resp = WebsocketMetabolicResp(type="multi_agent_output", data=agent_reply)
                await websocket.send_text(resp.model_dump_json())
                start = time.time()
            except asyncio.TimeoutError:
                pass

    process_task = asyncio.create_task(process())
    try:
        await process_task
    except Exception as e:
        logger.error(e)
    finally:
        logger.info("close websocket connection")
        for workflow_task in workflow_task_list:
            if not workflow_task.done():
                workflow_task.cancel()
        await websocket.close()


# api.add_resource(InstalledAppWorkflowRunApi, '/explore-apps/<uuid:installed_app_id>/workflows/run')
api.add_resource(InstalledAppWorkflowTaskStopApi,
                 '/explore-apps/<uuid:installed_app_id>/workflows/tasks/<string:task_id>/stop')
