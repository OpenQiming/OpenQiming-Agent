import logging
from datetime import datetime, timezone
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from flask_login import current_user
from flask_restful import reqparse
from starlette import status
from agent_platform_service.services.auth_service import login_user
from agent_platform_core.app.apps.async_base_app_queue_manager import AsyncAppQueueManager
from agent_platform_basic.models.db_model import Account
from agent_platform_service.fastapi_fields.req.console.chat_messages_req import ChatMessagesReq
from werkzeug.exceptions import InternalServerError, NotFound
from agent_platform_basic.libs import helper, DbUtils
from agent_platform_service.services.async_app_generate_service import AsyncAppGenerateService

import agent_platform_basic
from agent_platform_basic.exceptions.controllers.console.app import (
    AppUnavailableError,
    CompletionRequestError,
    ConversationCompletedError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from agent_platform_basic.exceptions.controllers.console.explore import NotChatAppError, NotCompletionAppError
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.libs import helper
from agent_platform_basic.libs.helper import uuid_value
from agent_platform_core.app.apps.base_app_queue_manager import AppQueueManager
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.controllers.console import api, console_api
from agent_platform_service.controllers.console.explore.wraps import InstalledAppResource
from agent_platform_service.services.app_generate_service import AppGenerateService
from agent_platform_service.controllers.console.app.wraps import get_app_model, get_app_model_async


# define completion api for user
class CompletionApi(InstalledAppResource):

    def post(self, app_model):
        if app_model.mode != 'completion':
            raise NotCompletionAppError()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, required=True, location='json')
        parser.add_argument('query', type=str, location='json', default='')
        parser.add_argument('files', type=list, required=False, location='json')
        parser.add_argument('response_mode', type=str, choices=['blocking', 'streaming'], location='json')
        parser.add_argument('retriever_from', type=str, required=False, default='explore_app', location='json')
        args = parser.parse_args()

        streaming = args['response_mode'] == 'streaming'
        args['auto_generate_name'] = False

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=current_user,
                args=args,
                invoke_from=InvokeFrom.EXPLORE,
                streaming=streaming
            )

            return helper.compact_generate_response(response)
        except agent_platform_basic.exceptions.services.conversation.ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except agent_platform_basic.exceptions.services.conversation.ConversationCompletedError:
            raise ConversationCompletedError()
        except agent_platform_basic.exceptions.services.app_model_config.AppModelConfigBrokenError:
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


class CompletionStopApi(InstalledAppResource):
    def post(self, app_model, task_id):
        if app_model.mode != 'completion':
            raise NotCompletionAppError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.EXPLORE, current_user.id)

        return {'result': 'success'}, 200



@console_api.post("/explore-apps/{installed_app_id}/chat-messages", status_code=status.HTTP_200_OK)
async def chat_message_api_post(installed_app_id: str,
                                request_body: ChatMessagesReq,
                                current_user: Account = Depends(login_user),
                                async_app_generate_service: AsyncAppGenerateService = Depends(AsyncAppGenerateService)):
    app_model = await get_app_model_async(app_id=installed_app_id,
                                          mode=[AppMode.AGENT_CHAT, AppMode.CHAT, AppMode.ADVANCED_CHAT])

    if not app_model:
        raise NotChatAppError()

    try:
        args = request_body.model_dump()

        streaming = request_body.response_mode != 'blocking'
        args['auto_generate_name'] = False
        response = await async_app_generate_service.generate(
            app_model=app_model,
            user=current_user,
            args=args,
            invoke_from=InvokeFrom.EXPLORE,
            streaming=streaming
        )
        return await helper.async_compact_generate_response(response)
    except ValueError as e:
        raise e
    except Exception as e:
        logging.exception('internal server error.')
        raise InternalServerError()
    pass

class ChatApi(InstalledAppResource):
    def post(self, app_model):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, required=True, location='json')
        parser.add_argument('query', type=str, required=True, location='json')
        parser.add_argument('files', type=list, required=False, location='json')
        parser.add_argument('conversation_id', type=uuid_value, location='json')
        parser.add_argument('retriever_from', type=str, required=False, default='explore_app', location='json')
        args = parser.parse_args()

        args['auto_generate_name'] = False

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=current_user,
                args=args,
                invoke_from=InvokeFrom.EXPLORE,
                streaming=True
            )

            return helper.compact_generate_response(response)
        except agent_platform_basic.exceptions.services.conversation.ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except agent_platform_basic.exceptions.services.conversation.ConversationCompletedError:
            raise ConversationCompletedError()
        except agent_platform_basic.exceptions.services.app_model_config.AppModelConfigBrokenError:
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

@console_api.post("/explore-apps/{installed_app_id}/chat-messages/{task_id}/stop", status_code=status.HTTP_200_OK)
async def chat_message_api_stop(app_id: str, installed_app_id: str,
                                current_user: Account = Depends(login_user),
                                ):
    await AsyncAppQueueManager.set_stop_flag(installed_app_id, InvokeFrom.EXPLORE, current_user.id)
    return {'result': 'success'}, 200

class ChatStopApi(InstalledAppResource):
    def post(self, app_model, task_id):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.EXPLORE, current_user.id)

        return {'result': 'success'}, 200


api.add_resource(CompletionApi, '/explore-apps/<uuid:installed_app_id>/completion-messages',
                 endpoint='explore_app_completion')
api.add_resource(CompletionStopApi, '/explore-apps/<uuid:installed_app_id>/completion-messages/<string:task_id>/stop',
                 endpoint='explore_app_stop_completion')
# api.add_resource(ChatApi, '/explore-apps/<uuid:installed_app_id>/chat-messages',
#                  endpoint='explore_app_chat_completion')
# api.add_resource(ChatStopApi, '/explore-apps/<uuid:installed_app_id>/chat-messages/<string:task_id>/stop',
#                  endpoint='explore_app_stop_chat_completion')
