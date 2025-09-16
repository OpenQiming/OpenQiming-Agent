from flask_login import current_user
from flask_restful import marshal_with, reqparse
from flask_restful.inputs import int_range
from werkzeug.exceptions import NotFound

from agent_platform_basic.exceptions.controllers.console.explore import NotChatAppError
from agent_platform_basic.exceptions.services.conversation import ConversationNotExistsError, \
    LastConversationNotExistsError
from agent_platform_basic.libs.helper import uuid_value
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.explore.wraps import InstalledAppResource
from agent_platform_service.fields.conversation_fields import conversation_infinite_scroll_pagination_fields, \
    simple_conversation_fields
from agent_platform_service.services.conversation_service import ConversationService
from agent_platform_service.services.web_conversation_service import WebConversationService


class ConversationListApi(InstalledAppResource):

    @marshal_with(conversation_infinite_scroll_pagination_fields)
    def get(self, app_model):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        parser = reqparse.RequestParser()
        parser.add_argument('last_id', type=uuid_value, location='args')
        parser.add_argument('limit', type=int_range(1, 100), required=False, default=20, location='args')
        parser.add_argument('pinned', type=str, choices=['true', 'false', None], location='args')
        parser.add_argument('name', type=str, required=False, nullable=True, location='args')

        args = parser.parse_args()

        pinned = None
        if 'pinned' in args and args['pinned'] is not None:
            pinned = True if args['pinned'] == 'true' else False

        try:
            return WebConversationService.pagination_by_last_id(
                app_model=app_model,
                user=current_user,
                last_id=args['last_id'],
                limit=args['limit'],
                invoke_from=InvokeFrom.EXPLORE,
                pinned=pinned,
                name=args.get('name'),
            )
        except LastConversationNotExistsError:
            raise NotFound("Last Conversation Not Exists.")


class ConversationApi(InstalledAppResource):
    def delete(self, app_model, c_id):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        conversation_id = str(c_id)
        try:
            ConversationService.delete(app_model, conversation_id, current_user)
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")
        WebConversationService.unpin(app_model, conversation_id, current_user)

        return {"result": "success"}, 204


class ConversationRenameApi(InstalledAppResource):

    @marshal_with(simple_conversation_fields)
    def post(self, app_model, c_id):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        conversation_id = str(c_id)

        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=False, location='json')
        parser.add_argument('auto_generate', type=bool, required=False, default=False, location='json')
        args = parser.parse_args()

        try:
            return ConversationService.rename(
                app_model,
                conversation_id,
                current_user,
                args['name'],
                args['auto_generate']
            )
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")


class ConversationPinApi(InstalledAppResource):

    def patch(self, app_model, c_id):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        conversation_id = str(c_id)

        try:
            WebConversationService.pin(app_model, conversation_id, current_user)
        except ConversationNotExistsError:
            raise NotFound("Conversation Not Exists.")

        return {"result": "success"}


class ConversationUnPinApi(InstalledAppResource):
    def patch(self, app_model, c_id):
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode not in [AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.ADVANCED_CHAT]:
            raise NotChatAppError()

        conversation_id = str(c_id)
        WebConversationService.unpin(app_model, conversation_id, current_user)

        return {"result": "success"}


api.add_resource(ConversationRenameApi, '/explore-apps/<uuid:installed_app_id>/conversations/<uuid:c_id>/name',
                 endpoint='explore_app_conversation_rename')
api.add_resource(ConversationListApi, '/explore-apps/<uuid:installed_app_id>/conversations',
                 endpoint='explore_app_conversations')
api.add_resource(ConversationApi, '/explore-apps/<uuid:installed_app_id>/conversations/<uuid:c_id>',
                 endpoint='explore_app_conversation')
api.add_resource(ConversationPinApi, '/explore-apps/<uuid:installed_app_id>/conversations/<uuid:c_id>/pin',
                 endpoint='explore_app_conversation_pin')
api.add_resource(ConversationUnPinApi, '/explore-apps/<uuid:installed_app_id>/conversations/<uuid:c_id>/unpin',
                 endpoint='explore_app_conversation_unpin')
