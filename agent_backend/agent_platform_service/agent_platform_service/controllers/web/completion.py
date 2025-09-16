import logging

from flask_restful import reqparse
from werkzeug.exceptions import InternalServerError, NotFound

import agent_platform_basic.exceptions.services as ServiceExceptions
from agent_platform_basic.exceptions.controllers.web import (
    AppUnavailableError,
    CompletionRequestError,
    ConversationCompletedError,
    NotChatAppError,
    NotCompletionAppError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.libs import helper
from agent_platform_basic.libs.helper import uuid_value
from agent_platform_core.app.apps.base_app_queue_manager import AppQueueManager
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.controllers.web import api
from agent_platform_service.controllers.web.wraps import WebApiResource
from agent_platform_service.services.app_generate_service import AppGenerateService


# define completion api for user
class CompletionApi(WebApiResource):

    def post(self, app_model, end_user):
        if app_model.mode != 'completion':
            raise NotCompletionAppError()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, required=True, location='json')
        parser.add_argument('query', type=str, location='json', default='')
        parser.add_argument('files', type=list, required=False, location='json')
        parser.add_argument('response_mode', type=str, choices=['blocking', 'streaming'], location='json')
        parser.add_argument('retriever_from', type=str, required=False, default='web_app', location='json')

        args = parser.parse_args()

        streaming = args['response_mode'] == 'streaming'
        args['auto_generate_name'] = False

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=end_user,
                args=args,
                invoke_from=InvokeFrom.WEB_APP,
                streaming=streaming
            )

            return helper.compact_generate_response(response)
        except ServiceExceptions.conversation.ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except ServiceExceptions.conversation.ConversationCompletedError:
            raise ConversationCompletedError()
        except ServiceExceptions.app_model_config.AppModelConfigBrokenError:
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


class CompletionStopApi(WebApiResource):
    def post(self, app_model, end_user, task_id):
        if app_model.mode != 'completion':
            raise NotCompletionAppError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.WEB_APP, end_user.id)

        return {'result': 'success'}, 200


class ChatApi(WebApiResource):
    def post(self, app_model, end_user):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        parser = reqparse.RequestParser()
        parser.add_argument('inputs', type=dict, required=True, location='json')
        parser.add_argument('query', type=str, required=True, location='json')
        parser.add_argument('files', type=list, required=False, location='json')
        parser.add_argument('response_mode', type=str, choices=['blocking', 'streaming'], location='json')
        parser.add_argument('conversation_id', type=uuid_value, location='json')
        parser.add_argument('retriever_from', type=str, required=False, default='web_app', location='json')

        args = parser.parse_args()

        streaming = args['response_mode'] == 'streaming'
        args['auto_generate_name'] = False

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=end_user,
                args=args,
                invoke_from=InvokeFrom.WEB_APP,
                streaming=streaming
            )

            return helper.compact_generate_response(response)
        except ServiceExceptions.conversation.ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except ServiceExceptions.conversation.ConversationCompletedError:
            raise ConversationCompletedError()
        except ServiceExceptions.app_model_config.AppModelConfigBrokenError:
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


class ChatStopApi(WebApiResource):
    def post(self, app_model, end_user, task_id):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.WEB_APP, end_user.id)

        return {'result': 'success'}, 200


api.add_resource(CompletionApi, '/completion-messages')
api.add_resource(CompletionStopApi, '/completion-messages/<string:task_id>/stop')
api.add_resource(ChatApi, '/chat-messages')
api.add_resource(ChatStopApi, '/chat-messages/<string:task_id>/stop')
