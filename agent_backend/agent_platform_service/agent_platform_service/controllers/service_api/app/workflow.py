import asyncio
import json
import logging
import time
import uuid

from fastapi import Depends, WebSocket
from flask_restful import Resource, reqparse
from starlette.websockets import WebSocketDisconnect
from werkzeug.exceptions import InternalServerError

from agent_platform_core import contexts
from agent_platform_metabolic.actions import UserRequirement
from agent_platform_metabolic.hand_made_agents.envs.metabolic_env import MetabolicEnv
from agent_platform_metabolic.hand_made_agents.roles.account_agent import AccountAgent
from agent_platform_metabolic.hand_made_agents.roles.fault_report_agent import FaultReportAgent
from agent_platform_metabolic.hand_made_agents.roles.sigma_agent import SigmaAgent
from agent_platform_metabolic.hand_made_agents.roles.solution_confirm_agent import SolutionConfirmAgent
from agent_platform_metabolic.schema import Task, Message
from agent_platform_service.controllers.console.app.wraps import get_app_model_async
from agent_platform_service.controllers.service_api.wraps import get_published_app_model_async
from agent_platform_service.controllers.service_api import api, service_api
from agent_platform_basic.exceptions.controllers.service_api.app import (
    CompletionRequestError,
    NotWorkflowAppError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from agent_platform_service.controllers.service_api.wraps import FetchUserArg, WhereisUserArg, validate_app_token, \
    AppTokenValidator, async_create_or_update_end_user_for_user_id
from agent_platform_core.app.apps.base_app_queue_manager import AppQueueManager
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.libs import helper, StringUtils
from agent_platform_core.models.db_model.model import App, EndUser
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.fastapi_fields.req.service_api.workflow import WorkflowRunApiReq, ValidateAppTokenFields
from agent_platform_service.fastapi_fields.resp.console.websocket_metabolic_resp import WebsocketMetabolicResp
from agent_platform_service.services.async_app_generate_service import AsyncAppGenerateService
from agent_platform_service.services.app_generate_service import AppGenerateService


logger = logging.getLogger(__name__)

workflow_run_v1_validator = AppTokenValidator(
    fetch_user_arg=FetchUserArg(fetch_from=WhereisUserArg.JSON, required=True))


@service_api.post("/workflows/run/{app_id}")
async def workflow_run_api_post(app_id: str, request: WorkflowRunApiReq,
                                # validate_app_token_fields: ValidateAppTokenFields =
                                # Depends(workflow_run_v1_validator.call),
                                async_app_generate_service: AsyncAppGenerateService = Depends(AsyncAppGenerateService)):
    """
    Run workflow
    """

    app_model = await get_published_app_model_async(app_id=app_id, mode=[AppMode.WORKFLOW])
    # app_model = validate_app_token_fields.app_model
    # end_user = validate_app_token_fields.end_user
    end_user_id = request.user
    end_user = await async_create_or_update_end_user_for_user_id(app_model, end_user_id)

    request_body = request.model_dump()
    streaming = request.response_mode == 'streaming'

    try:
        response = await async_app_generate_service.generate(
            app_model=app_model,
            user=end_user,
            args=request_body,
            invoke_from=InvokeFrom.SERVICE_API,
            streaming=streaming
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
        logging.exception(e)
        raise InternalServerError()


class WorkflowRunApi(Resource):
    @validate_app_token(fetch_user_arg=FetchUserArg(fetch_from=WhereisUserArg.JSON, required=True))
    def post(self, app_model: App, end_user: EndUser):
        """
        Run workflow
        """
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode != AppMode.WORKFLOW:
            raise NotWorkflowAppError()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, required=True, nullable=False, location='json')
        parser.add_argument('files', type=list, required=False, location='json')
        parser.add_argument('response_mode', type=str, choices=['blocking', 'streaming'], location='json')
        args = parser.parse_args()

        streaming = args.get('response_mode') == 'streaming'

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=end_user,
                args=args,
                invoke_from=InvokeFrom.SERVICE_API,
                streaming=streaming
            )

            return helper.compact_generate_response(response)
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


class WorkflowTaskStopApi(Resource):
    @validate_app_token(fetch_user_arg=FetchUserArg(fetch_from=WhereisUserArg.JSON, required=True))
    def post(self, app_model: App, end_user: EndUser, task_id: str):
        """
        Stop workflow task
        """
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode != AppMode.WORKFLOW:
            raise NotWorkflowAppError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.SERVICE_API, end_user.id)

        return {
            "result": "success"
        }

@service_api.websocket("/{app_id}/ws/metabolic")
async def service_metabolic_websocket_endpoint(websocket: WebSocket, app_id: str,
                                               async_app_generate_service: AsyncAppGenerateService = Depends(
                                                   AsyncAppGenerateService)
                                               ):
    await websocket.accept()
    workflow_queue = asyncio.Queue()
    metabolic_queue = asyncio.Queue()
    try:
        app_model = await get_app_model_async(app_id=app_id,
                                              mode=[AppMode.WORKFLOW, AppMode.METABOLIC])
    except Exception as e:
        logger.error(e)
        await websocket.close()
        return

    redis_label = str(uuid.uuid4())
    contexts.redis_label.set(redis_label)
    end_user_id = websocket.query_params.get("user")
    if StringUtils.is_blank(end_user_id):
        raise Exception("missing query param: user")
    end_user = await async_create_or_update_end_user_for_user_id(app_model, end_user_id)

    env = MetabolicEnv(redis_label=redis_label, q=metabolic_queue)
    env.add_roles([SigmaAgent(), AccountAgent(), FaultReportAgent(),
                   SolutionConfirmAgent()])

    params = dict(websocket.query_params)

    async def start_workflow(query: str):
        # try:
        async for event in await async_app_generate_service.generate(
                app_model=app_model,
                user=end_user,
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
            logger.debug(f"user_id: {end_user_id}, websocket client_state: {websocket.client_state}")
            if time.time() - start > 120:
                logger.info(f"用户{end_user_id}长时间未操作, websocket连接断开")
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


# api.add_resource(WorkflowRunApi, '/workflows/run')
api.add_resource(WorkflowTaskStopApi, '/workflows/tasks/<string:task_id>/stop')
