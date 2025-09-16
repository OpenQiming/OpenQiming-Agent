from flask_restful import marshal_with

from agent_platform_service.controllers.common import fields
from agent_platform_service.controllers.common import helpers as controller_helpers
from agent_platform_service.controllers.console import api
from agent_platform_basic.exceptions.controllers.console.app import AppUnavailableError
from agent_platform_service.controllers.console.explore.wraps import InstalledAppResource
from agent_platform_core.models.db_model.model import App
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.services.app_service import AppService

class AppParameterApi(InstalledAppResource):
    """Resource for app variables."""

    @marshal_with(fields.parameters_fields)
    def get(self, app_model: App):
        """Retrieve app parameters."""

        if app_model is None:
            raise AppUnavailableError()

        if app_model.mode in {AppMode.ADVANCED_CHAT.value, AppMode.WORKFLOW.value}:
            workflow = app_model.workflow
            if workflow is None:
                raise AppUnavailableError()

            features_dict = workflow.features_dict
            user_input_form = workflow.user_input_form(to_old_structure=True)
            features_dict["example"] = workflow.example
        else:
            app_model_config = app_model.app_model_config
            if app_model_config is None:
                raise AppUnavailableError()

            features_dict = app_model_config.to_dict()

            user_input_form = features_dict.get("user_input_form", [])

        return controller_helpers.get_parameters_from_feature_dict(
            features_dict=features_dict, user_input_form=user_input_form
        )


class ExploreAppMetaApi(InstalledAppResource):
    def get(self, app_model: App):
        """Get app meta"""
        return AppService().get_app_meta(app_model)


api.add_resource(AppParameterApi, '/explore-apps/<uuid:installed_app_id>/parameters',
                 endpoint='installed_app_parameters')
api.add_resource(ExploreAppMetaApi, '/explore-apps/<uuid:installed_app_id>/meta', endpoint='installed_app_meta')
