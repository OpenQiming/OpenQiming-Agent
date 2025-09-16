from flask import request
from flask_restful import Resource, reqparse
from agent_platform_basic.exceptions.base_http_exception import Forbidden

from agent_platform_basic.libs.login import current_user, login_required
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.app.wraps import get_app_model
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.services.tools.code_tools_service import CodeToolsService


class CreateCodeTool(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    def post(self):
        if not current_user.is_editor:
            raise Forbidden()

        parser = reqparse.RequestParser()
        parser.add_argument('toolName', type=str, required=True, nullable=False, location='json')
        parser.add_argument('toolDesc', type=str, required=True, nullable=False, location='json')
        parser.add_argument('codeLanguage', type=str, required=True, choices=['python3', 'javascript'], nullable=False,
                            location='json')
        parser.add_argument('codeContent', type=str, required=True, nullable=False, location='json')
        parser.add_argument('isPublish', type=bool, required=True, nullable=False, location='json')
        data = request.json
        InVarParams = data.get('InVarParams', [])
        OutVarParams = data.get('OutVarParams', [])
        args = parser.parse_args()
        return CodeToolsService.do_create_main(
            args['toolName'],
            args['toolDesc'],
            args['codeLanguage'],
            args['codeContent'],
            InVarParams,
            OutVarParams,
            current_user,
            args['isPublish']
        )


class UpdateCodeTool(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model
    def post(self, app_model, tool_id):
        if not current_user.is_editor:
            raise Forbidden()

        parser = reqparse.RequestParser()
        parser.add_argument('toolName', type=str, required=True, nullable=False, location='json')
        parser.add_argument('toolDesc', type=str, required=True, nullable=False, location='json')
        parser.add_argument('codeLanguage', type=str, required=True, choices=['python3', 'javascript'], nullable=False,
                            location='json')
        parser.add_argument('codeContent', type=str, required=True, nullable=False, location='json')
        parser.add_argument('isPublish', type=bool, required=True, nullable=False, location='json')
        data = request.json
        InVarParams = data.get('InVarParams', [])
        OutVarParams = data.get('OutVarParams', [])
        args = parser.parse_args()
        return CodeToolsService.do_update_main(
            args['toolName'],
            args['toolDesc'],
            args['codeLanguage'],
            args['codeContent'],
            InVarParams,
            OutVarParams,
            current_user,
            args['isPublish'], app_model, tool_id
        )


api.add_resource(CreateCodeTool, '/CodeTool/create')
api.add_resource(UpdateCodeTool, '/CodeTool/<uuid:app_id>/update/<uuid:tool_id>')
