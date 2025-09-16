import logging

from flask_restful import reqparse
from werkzeug.exceptions import InternalServerError

from agent_platform_basic.exceptions.controllers.web import (
    CompletionRequestError,
    NotWorkflowAppError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.libs import helper
from agent_platform_core.app.apps.base_app_queue_manager import AppQueueManager
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.errors.error import ModelCurrentlyNotSupportError, ProviderTokenNotInitError, \
    QuotaExceededError
from agent_platform_core.models.db_model.model import App, EndUser
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.controllers.web import api
from agent_platform_service.controllers.web.wraps import WebApiResource
from agent_platform_service.services.app_generate_service import AppGenerateService

logger = logging.getLogger(__name__)


class WorkflowRunApi(WebApiResource):
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
        args = parser.parse_args()

        try:
            response = AppGenerateService.generate(
                app_model=app_model,
                user=end_user,
                args=args,
                invoke_from=InvokeFrom.WEB_APP,
                streaming=True
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


class WorkflowTaskStopApi(WebApiResource):
    def post(self, app_model: App, end_user: EndUser, task_id: str):
        """
        Stop workflow task
        """
        app_mode = AppMode.value_of(app_model.mode)
        if app_mode != AppMode.WORKFLOW:
            raise NotWorkflowAppError()

        AppQueueManager.set_stop_flag(task_id, InvokeFrom.WEB_APP, end_user.id)

        return {
            "result": "success"
        }


api.add_resource(WorkflowRunApi, '/workflows/run')
api.add_resource(WorkflowTaskStopApi, '/workflows/tasks/<string:task_id>/stop')
