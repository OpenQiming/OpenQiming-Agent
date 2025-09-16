import logging

from agent_platform_core.app.apps.async_base_app_queue_manager import AsyncAppQueueManager
from fastapi import Depends
import flask_login
from flask_restful import Resource, reqparse
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from werkzeug.exceptions import InternalServerError, NotFound

from agent_platform_basic.exceptions.controllers.console.app import (
    AppUnavailableError,
    CompletionRequestError,
    ConversationCompletedError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.exceptions.services.app_model_config import AppModelConfigBrokenError
from agent_platform_basic.exceptions.services.conversation import (
    ConversationNotExistsError,
    ConversationCompletedError)
from agent_platform_basic.libs import helper, DbUtils
from agent_platform_basic.libs.helper import uuid_value
from agent_platform_basic.libs.login import login_required
from agent_platform_basic.models.db_model import Account
from agent_platform_core.app.apps.base_app_queue_manager import AppQueueManager
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.errors.error import (
    ModelCurrentlyNotSupportError,
    ProviderTokenNotInitError,
    QuotaExceededError
)
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.controllers.console import api, console_api
from agent_platform_service.controllers.console.app.wraps import get_app_model, get_app_model_async
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.fastapi_fields.req.console.chat_messages_req import ChatMessagesReq
from agent_platform_service.fastapi_fields.req.console.multi_chat_messages_req import MultiChatMessagesReq
from agent_platform_service.services.async_app_generate_service import AsyncAppGenerateService
from agent_platform_service.services.app_generate_service import AppGenerateService
from agent_platform_service.services.auth_service import login_user


# define completion message api for user
class CompletionMessageApi(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=AppMode.COMPLETION)
    def post(self, app_model):
        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, required=True, location='json')
        parser.add_argument('query', type=str, location='json', default='')
        parser.add_argument('files', type=list, required=False, location='json')
        parser.add_argument('model_config', type=dict, required=True, location='json')
        parser.add_argument('response_mode', type=str, choices=['blocking', 'streaming'], location='json')
        parser.add_argument('retriever_from', type=str, required=False, default='dev', location='json')
        args = parser.parse_args()

        streaming = args['response_mode'] != 'blocking'
        args['auto_generate_name'] = False

        account = flask_login.current_user

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=account,
                args=args,
                invoke_from=InvokeFrom.DEBUGGER,
                streaming=streaming
            )

            return helper.compact_generate_response(response)
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except ConversationCompletedError:
            raise ConversationCompletedError()
        except AppModelConfigBrokenError:
            logging.exception("App model config broken.")
            raise AppUnavailableError()
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
        except Exception:
            logging.exception("internal server error.")
            raise InternalServerError()


class CompletionMessageStopApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=AppMode.COMPLETION)
    def post(self, app_model, task_id):
        account = flask_login.current_user

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.DEBUGGER, account.id)

        return {'result': 'success'}, 200

# 单个大模型请求时的接口
@console_api.post("/apps/{app_id}/chat-messages", status_code=status.HTTP_200_OK)
async def chat_message_api_post(app_id: str,
                                request_body: ChatMessagesReq,
                                current_user: Account = Depends(login_user),
                                async_app_generate_service: AsyncAppGenerateService = Depends(AsyncAppGenerateService)):
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.AGENT_CHAT])

    try:
        args = request_body.model_dump()

        streaming = request_body.response_mode != 'blocking'
        args['auto_generate_name'] = False
        response = await async_app_generate_service.generate(
            app_model=app_model,
            user=current_user,
            args=args,
            invoke_from=InvokeFrom.DEBUGGER,
            streaming=streaming
        )
        return await helper.async_compact_generate_response(response)
    except ValueError as e:
        raise e
    except Exception as e:
        logging.exception('internal server error.')
        raise InternalServerError()
    pass

# 多个大模型请求时的接口
@console_api.post("/apps/{app_id}/multi-chat-messages", status_code=status.HTTP_200_OK)
async def chat_message_api_post(app_id: str,
                                request_body: MultiChatMessagesReq,
                                current_user: Account = Depends(login_user),
                                async_app_generate_service: AsyncAppGenerateService = Depends(AsyncAppGenerateService)):

    # 根据app id查出app的相关配置
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.AGENT_CHAT])

    try:
        args = request_body.model_dump()

        frontend_model_config = args["model_config_data"]["model"]

        streaming = request_body.response_mode != 'blocking'
        args['auto_generate_name'] = False
        response = await async_app_generate_service.generate(
            app_model=app_model,
            user=current_user,
            args=args,
            invoke_from=InvokeFrom.DEBUGGER,
            streaming=streaming,
            is_multi_chat=True,
            frontend_model_config=frontend_model_config,
        )
        return await helper.async_compact_generate_response(response)
    except ValueError as e:
        raise e
    except Exception as e:
        logging.exception('internal server error.')
        raise InternalServerError()
    pass


class ChatMessageApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.CHAT, AppMode.AGENT_CHAT])
    def post(self, app_model):
        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, required=True, location='json')
        parser.add_argument('query', type=str, required=True, location='json')
        parser.add_argument('files', type=list, required=False, location='json')
        parser.add_argument('model_config', type=dict, required=True, location='json')
        parser.add_argument('conversation_id', type=uuid_value, location='json')
        parser.add_argument('response_mode', type=str, choices=['blocking', 'streaming'], location='json')
        parser.add_argument('retriever_from', type=str, required=False, default='dev', location='json')
        args = parser.parse_args()

        streaming = args['response_mode'] != 'blocking'
        args['auto_generate_name'] = False

        account = flask_login.current_user

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=account,
                args=args,
                invoke_from=InvokeFrom.DEBUGGER,
                streaming=streaming
            )

            return helper.compact_generate_response(response)
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except ConversationCompletedError:
            raise ConversationCompletedError()
        except AppModelConfigBrokenError:
            logging.exception("App model config broken.")
            raise AppUnavailableError()
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
        except Exception:
            logging.exception("internal server error.")
            raise InternalServerError()


@console_api.post("/apps/{app_id}/chat-messages/{task_id}/stop", status_code=status.HTTP_200_OK)
async def chat_message_api_stop(app_id: str, task_id: str,
                                current_user: Account = Depends(login_user),
                                ):
    await AsyncAppQueueManager.set_stop_flag(task_id, InvokeFrom.DEBUGGER, current_user.id)
    return {'result': 'success'}, 200


class ChatMessageStopApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    def post(self, app_model, task_id):
        account = flask_login.current_user

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.DEBUGGER, account.id)

        return {'result': 'success'}, 200


api.add_resource(CompletionMessageApi, '/apps/<uuid:app_id>/completion-messages')
api.add_resource(CompletionMessageStopApi, '/apps/<uuid:app_id>/completion-messages/<string:task_id>/stop')
# api.add_resource(ChatMessageApi, '/apps/<uuid:app_id>/chat-messages')
# api.add_resource(ChatMessageStopApi, '/apps/<uuid:app_id>/chat-messages/<string:task_id>/stop')
