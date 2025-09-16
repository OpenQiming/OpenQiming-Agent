import logging

from flask_login import current_user
from flask_restful import marshal_with, reqparse
from flask_restful.inputs import int_range
from werkzeug.exceptions import InternalServerError, NotFound

from agent_platform_basic.exceptions.controllers.console.app import (
    AppMoreLikeThisDisabledError,
    CompletionRequestError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from agent_platform_basic.exceptions.controllers.console.explore import (
    AppSuggestedQuestionsAfterAnswerDisabledError,
    NotChatAppError,
    NotCompletionAppError,
)
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.exceptions.services.app import MoreLikeThisDisabledError
from agent_platform_basic.exceptions.services.conversation import ConversationNotExistsError
from agent_platform_basic.exceptions.services.message import MessageNotExistsError, \
    SuggestedQuestionsAfterAnswerDisabledError, FirstMessageNotExistsError
from agent_platform_basic.libs import helper
from agent_platform_basic.libs.helper import uuid_value
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.explore.wraps import InstalledAppResource
from agent_platform_service.fields.message_fields import message_infinite_scroll_pagination_fields
from agent_platform_service.services.app_generate_service import AppGenerateService
from agent_platform_service.services.message_service import MessageService


class MessageListApi(InstalledAppResource):
    @marshal_with(message_infinite_scroll_pagination_fields)
    def get(self, app_model):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        parser = reqparse.RequestParser()
        parser.add_argument('conversation_id', required=True, type=uuid_value, location='args')
        parser.add_argument('first_id', type=uuid_value, location='args')
        parser.add_argument('limit', type=int_range(1, 100), required=False, default=20, location='args')
        args = parser.parse_args()

        try:
            return MessageService.pagination_by_first_id(app_model, current_user,
                                                         args['conversation_id'], args['first_id'], args['limit'])
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        except FirstMessageNotExistsError:
            raise NotFound("First Message Not Exists.")


class MessageFeedbackApi(InstalledAppResource):
    def post(self, app_model, message_id):
        message_id = str(message_id)

        parser = reqparse.RequestParser()
        parser.add_argument('rating', type=str, choices=['like', 'dislike', None], location='json')
        args = parser.parse_args()

        try:
            MessageService.create_feedback(app_model, message_id, current_user, args['rating'])
        except MessageNotExistsError:
            raise NotFound("Message Not Exists.")

        return {'result': 'success'}


class MessageMoreLikeThisApi(InstalledAppResource):
    def get(self, app_model, message_id):
        if app_model.mode != 'completion':
            raise NotCompletionAppError()

        message_id = str(message_id)

        parser = reqparse.RequestParser()
        parser.add_argument('response_mode', type=str, required=True, choices=['blocking', 'streaming'],
                            location='args')
        args = parser.parse_args()

        streaming = args['response_mode'] == 'streaming'

        try:
            response = AppGenerateService.generate_more_like_this(
                app_model=app_model,
                user=current_user,
                message_id=message_id,
                invoke_from=InvokeFrom.EXPLORE,
                streaming=streaming
            )
            return helper.compact_generate_response(response)
        except MessageNotExistsError:
            raise NotFound("Message Not Exists.")
        except MoreLikeThisDisabledError:
            raise AppMoreLikeThisDisabledError()
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


class MessageSuggestedQuestionApi(InstalledAppResource):
    def get(self, app_model, message_id):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        message_id = str(message_id)

        try:
            questions = MessageService.get_suggested_questions_after_answer(
                app_model=app_model,
                user=current_user,
                message_id=message_id,
                invoke_from=InvokeFrom.EXPLORE
            )
        except MessageNotExistsError:
            raise NotFound("Message not found")
        except ConversationNotExistsError:
            raise NotFound("Conversation not found")
        except SuggestedQuestionsAfterAnswerDisabledError:
            raise AppSuggestedQuestionsAfterAnswerDisabledError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except Exception:
            logging.exception("internal server error.")
            raise InternalServerError()

        return {'data': questions}


api.add_resource(MessageListApi, '/explore-apps/<uuid:installed_app_id>/messages', endpoint='explore_app_messages')
api.add_resource(MessageFeedbackApi, '/explore-apps/<uuid:installed_app_id>/messages/<uuid:message_id>/feedbacks',
                 endpoint='explore_app_message_feedback')
api.add_resource(MessageMoreLikeThisApi,
                 '/explore-apps/<uuid:installed_app_id>/messages/<uuid:message_id>/more-like-this',
                 endpoint='explore_app_more_like_this')
api.add_resource(MessageSuggestedQuestionApi,
                 '/explore-apps/<uuid:installed_app_id>/messages/<uuid:message_id>/suggested-questions',
                 endpoint='explore_app_suggested_question')
