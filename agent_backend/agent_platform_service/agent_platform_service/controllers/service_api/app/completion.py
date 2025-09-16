import logging

from fastapi import Depends
from agent_platform_core.app.apps.async_base_app_queue_manager import AsyncAppQueueManager
from flask_restful import Resource, reqparse
from starlette import status
from werkzeug.exceptions import InternalServerError, NotFound
from agent_platform_service.services.async_app_generate_service import AsyncAppGenerateService

from agent_platform_service.controllers.service_api import api, service_api
from agent_platform_basic.exceptions.controllers.service_api.app import (
    AppUnavailableError,
    CompletionRequestError,
    ConversationCompletedError,
    NotChatAppError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from agent_platform_service.controllers.service_api.wraps import FetchUserArg, WhereisUserArg, validate_app_token, \
    get_app_model_without_login_by_app_id, create_or_update_end_user_for_user_id, \
    async_create_or_update_end_user_for_user_id
from agent_platform_core.app.apps.base_app_queue_manager import AppQueueManager
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.libs import helper
from agent_platform_basic.libs.helper import uuid_value
from agent_platform_core.models.db_model.model import App, EndUser
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.services.app_generate_service import AppGenerateService
from agent_platform_basic.exceptions.services.conversation import ConversationNotExistsError, ConversationCompletedError
from agent_platform_basic.exceptions.services.app_model_config import AppModelConfigBrokenError
from agent_platform_service.fastapi_fields.req.console.chat_messages_req import ChatMessagesReq
from agent_platform_service.controllers.console.app.wraps import get_app_model_async


class CompletionApi(Resource):
    @validate_app_token(fetch_user_arg=FetchUserArg(fetch_from=WhereisUserArg.JSON, required=True))
    def post(self, app_model: App, end_user: EndUser):
        if app_model.mode != 'completion':
            raise AppUnavailableError()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, required=True, location='json')
        parser.add_argument('query', type=str, location='json', default='')
        parser.add_argument('files', type=list, required=False, location='json')
        parser.add_argument('response_mode', type=str, choices=['blocking', 'streaming'], location='json')
        parser.add_argument('retriever_from', type=str, required=False, default='dev', location='json')

        args = parser.parse_args()

        streaming = args['response_mode'] == 'streaming'

        args['auto_generate_name'] = False

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=end_user,
                args=args,
                invoke_from=InvokeFrom.SERVICE_API,
                streaming=streaming,
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
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()


class CompletionStopApi(Resource):
    @validate_app_token(fetch_user_arg=FetchUserArg(fetch_from=WhereisUserArg.JSON, required=True))
    def post(self, app_model: App, end_user: EndUser, task_id):
        if app_model.mode != 'completion':
            raise AppUnavailableError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.SERVICE_API, end_user.id)

        return {'result': 'success'}, 200


@service_api.post("/chat-messages/{app_id}", status_code=status.HTTP_200_OK)
async def chat_message_api_post(app_id: str,
                                request_body: ChatMessagesReq,
                                async_app_generate_service: AsyncAppGenerateService = Depends(AsyncAppGenerateService)):
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.AGENT_CHAT, AppMode.CHAT, AppMode.ADVANCED_CHAT])

    if not app_model:
        raise NotChatAppError()
    end_user = await async_create_or_update_end_user_for_user_id(app_model)
    try:
        args = request_body.model_dump()

        streaming = request_body.response_mode != 'blocking'
        args['auto_generate_name'] = False
        response = await async_app_generate_service.generate(
            app_model=app_model,
            user=end_user,
            args=args,
            invoke_from=InvokeFrom.SERVICE_API,
            streaming=streaming
        )
        return await helper.async_compact_generate_response(response)
    except ValueError as e:
        raise e
    except Exception as e:
        logging.exception('internal server error.')
        raise InternalServerError()
    pass


class ChatApi(Resource):
    @get_app_model_without_login_by_app_id(mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    def post(self, app_model: App):
        end_user = create_or_update_end_user_for_user_id(app_model)
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, required=True, location='json')
        parser.add_argument('query', type=str, required=True, location='json')
        parser.add_argument('files', type=list, required=False, location='json')
        parser.add_argument('response_mode', type=str, choices=['blocking', 'streaming'], location='json')
        parser.add_argument('conversation_id', type=uuid_value, location='json')
        parser.add_argument('retriever_from', type=str, required=False, default='dev', location='json')
        parser.add_argument('auto_generate_name', type=bool, required=False, default=True, location='json')

        args = parser.parse_args()

        streaming = args['response_mode'] == 'streaming'

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=end_user,
                args=args,
                invoke_from=InvokeFrom.SERVICE_API,
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
        except Exception as e:
            logging.exception("internal server error.")
            raise InternalServerError()


@service_api.post("/chat-messages/{app_id}/{task_id}/stop", status_code=status.HTTP_200_OK)
async def chat_message_api_stop(app_id:str, task_id: str):
    app_model = await get_app_model_async(app_id=app_id,
                                          mode=[AppMode.AGENT_CHAT, AppMode.CHAT, AppMode.ADVANCED_CHAT])

    if not app_model:
        raise NotChatAppError()
    end_user = await async_create_or_update_end_user_for_user_id(app_model)
    await AsyncAppQueueManager.set_stop_flag(task_id, InvokeFrom.SERVICE_API, end_user.id)
    return {'result': 'success'}, 200


class ChatStopApi(Resource):
    @get_app_model_without_login_by_app_id(mode=[AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT])
    def post(self, app_model: App, task_id):
        end_user = create_or_update_end_user_for_user_id(app_model)
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.SERVICE_API, end_user.id)

        return {'result': 'success'}, 200


api.add_resource(CompletionApi, '/completion-messages')
api.add_resource(CompletionStopApi, '/completion-messages/<string:task_id>/stop')
# api.add_resource(ChatApi, '/chat-messages/<string:app_id>')
# api.add_resource(ChatStopApi, '/chat-messages/<string:task_id>/stop')
