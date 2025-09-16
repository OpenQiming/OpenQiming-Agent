from flask_restful import Resource, reqparse

from agent_platform_basic.libs.login import login_required
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.services.advanced_prompt_template_service import AdvancedPromptTemplateService


class AdvancedPromptTemplateList(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('app_mode', type=str, required=True, location='args')
        parser.add_argument('model_mode', type=str, required=True, location='args')
        parser.add_argument('has_context', type=str, required=False, default='true', location='args')
        parser.add_argument('model_name', type=str, required=True, location='args')
        args = parser.parse_args()

        return AdvancedPromptTemplateService.get_prompt(args)


api.add_resource(AdvancedPromptTemplateList, '/app/prompt-templates')
