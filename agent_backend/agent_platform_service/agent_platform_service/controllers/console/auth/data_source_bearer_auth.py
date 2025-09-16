from flask_login import current_user
from flask_restful import Resource, reqparse
from agent_platform_basic.exceptions.base_http_exception import Forbidden

from agent_platform_basic.exceptions.controllers.console.auth import ApiKeyAuthFailedError
from agent_platform_basic.libs.login import login_required
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.services.auth.api_key_auth_service import ApiKeyAuthService


class ApiKeyAuthDataSource(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def get(self):
        data_source_api_key_bindings = ApiKeyAuthService.get_provider_auth_list(current_user.current_tenant_id)
        if data_source_api_key_bindings:
            return {
                'sources': [{
                    'id': data_source_api_key_binding.id,
                    'category': data_source_api_key_binding.category,
                    'provider': data_source_api_key_binding.provider,
                    'disabled': data_source_api_key_binding.disabled,
                    'created_at': int(data_source_api_key_binding.created_at.timestamp()),
                    'updated_at': int(data_source_api_key_binding.updated_at.timestamp()),
                }
                    for data_source_api_key_binding in
                    data_source_api_key_bindings]
            }
        return {'sources': []}


class ApiKeyAuthDataSourceBinding(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def post(self):
        # The role of the current user in the table must be admin or owner
        if not current_user.is_editor:
            raise Forbidden()
        parser = reqparse.RequestParser()
        parser.add_argument('category', type=str, required=True, nullable=False, location='json')
        parser.add_argument('provider', type=str, required=True, nullable=False, location='json')
        parser.add_argument('credentials', type=dict, required=True, nullable=False, location='json')
        args = parser.parse_args()
        ApiKeyAuthService.validate_api_key_auth_args(args)
        try:
            ApiKeyAuthService.create_provider_auth(current_user.current_tenant_id, args)
        except Exception as e:
            raise ApiKeyAuthFailedError(str(e))
        return {'result': 'success'}, 200


class ApiKeyAuthDataSourceBindingDelete(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def delete(self, binding_id):
        # The role of the current user in the table must be admin or owner
        if not current_user.is_editor:
            raise Forbidden()

        ApiKeyAuthService.delete_provider_auth(current_user.current_tenant_id, binding_id)

        return {'result': 'success'}, 200


api.add_resource(ApiKeyAuthDataSource, '/api-key-auth/data-source')
api.add_resource(ApiKeyAuthDataSourceBinding, '/api-key-auth/data-source/binding')
api.add_resource(ApiKeyAuthDataSourceBindingDelete, '/api-key-auth/data-source/<uuid:binding_id>')
