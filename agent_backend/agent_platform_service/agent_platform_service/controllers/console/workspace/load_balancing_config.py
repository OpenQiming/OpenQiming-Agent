from fastapi import Depends
from flask_restful import Resource, reqparse
from starlette.requests import Request
from agent_platform_basic.exceptions.base_http_exception import Forbidden

from agent_platform_basic.models.db_model import Account
from agent_platform_service.controllers.console import api, console_api
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_core.model_runtime.entities.model_entities import ModelType
from agent_platform_basic.exceptions.model_runtime.validate import CredentialsValidateFailedError
from agent_platform_basic.libs.login import current_user, login_required
from agent_platform_basic.models.enum_model.tenant import TenantAccountRole
from agent_platform_service.services.auth_service import login_user
from agent_platform_service.services.model_load_balancing_service import ModelLoadBalancingService


class LoadBalancingCredentialsValidateApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def post(self, provider: str):
        if not TenantAccountRole.is_privileged_role(current_user.current_tenant.current_role):
            raise Forbidden()

        tenant_id = current_user.current_tenant_id

        parser = reqparse.RequestParser()
        parser.add_argument('model', type=str, required=True, nullable=False, location='json')
        parser.add_argument('model_type', type=str, required=True, nullable=False,
                            choices=[mt.value for mt in ModelType], location='json')
        parser.add_argument('credentials', type=dict, required=True, nullable=False, location='json')
        args = parser.parse_args()

        # validate model load balancing credentials
        model_load_balancing_service = ModelLoadBalancingService()

        result = True
        error = None

        try:
            model_load_balancing_service.validate_load_balancing_credentials(
                tenant_id=tenant_id,
                provider=provider,
                model=args['model'],
                model_type=args['model_type'],
                credentials=args['credentials']
            )
        except CredentialsValidateFailedError as ex:
            result = False
            error = str(ex)

        response = {'result': 'success' if result else 'error'}

        if not result:
            response['error'] = error

        return response

@console_api.post("/workspaces/current/model-providers/{provider}/models/load-balancing-configs/credentials-validate")
async def post(request: Request, provider: str,
               user: Account = Depends(login_user),
               model_load_balancing_service : ModelLoadBalancingService = Depends(ModelLoadBalancingService)):
    if not TenantAccountRole.is_privileged_role(user.current_tenant.current_role):
        raise Forbidden()

    tenant_id = user.current_tenant_id

    request_json = await request.get_json()
    result = True
    error = None

    return {"result": request_json['result']}


class LoadBalancingConfigCredentialsValidateApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def post(self, provider: str, config_id: str):
        if not TenantAccountRole.is_privileged_role(current_user.current_tenant.current_role):
            raise Forbidden()

        tenant_id = current_user.current_tenant_id

        parser = reqparse.RequestParser()
        parser.add_argument('model', type=str, required=True, nullable=False, location='json')
        parser.add_argument('model_type', type=str, required=True, nullable=False,
                            choices=[mt.value for mt in ModelType], location='json')
        parser.add_argument('credentials', type=dict, required=True, nullable=False, location='json')
        args = parser.parse_args()

        # validate model load balancing config credentials
        model_load_balancing_service = ModelLoadBalancingService()

        result = True
        error = None

        try:
            model_load_balancing_service.validate_load_balancing_credentials(
                tenant_id=tenant_id,
                provider=provider,
                model=args['model'],
                model_type=args['model_type'],
                credentials=args['credentials'],
                config_id=config_id,
            )
        except CredentialsValidateFailedError as ex:
            result = False
            error = str(ex)

        response = {'result': 'success' if result else 'error'}

        if not result:
            response['error'] = error

        return response


# Load Balancing Config
# api.add_resource(LoadBalancingCredentialsValidateApi,
#                  '/workspaces/current/model-providers/<string:provider>/models/load-balancing-configs/credentials-validate')

api.add_resource(LoadBalancingConfigCredentialsValidateApi,
                 '/workspaces/current/model-providers/<string:provider>/models/load-balancing-configs/<string:config_id>/credentials-validate')
