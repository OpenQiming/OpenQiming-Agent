import logging

from flask_restful import Resource, reqparse

from agent_platform_basic.exceptions.model_runtime.validate import CredentialsValidateFailedError
from agent_platform_service.controllers.interface import api
from agent_platform_service.services.account_service import AccountService
from agent_platform_service.services.model_load_balancing_service import ModelLoadBalancingService
from agent_platform_service.services.model_provider_service import ModelProviderService


class CreateToolChainInterface(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('model_name', type=str, required=True, nullable=False, location='json')
        parser.add_argument('task_id', type=str, required=True, nullable=False, location='json')
        parser.add_argument('employee_number', type=str, required=False, nullable=True, location='json')
        parser.add_argument('endpoint_url', type=str, required=False, nullable=True, location='json')
        params = parser.parse_args()
        logging.info(f"create_params:{params}")
        provider = 'tool_chain'
        account_service = AccountService()
        current_tenant = account_service.get_tenant_by_employee_number(params.get('employee_number'))
        tenant_id = current_tenant.id
        model = params.get('model_name') + '_' + params.get('task_id')

        args = {
            'model': model,
            'model_type': 'llm',
            'credentials': {
                "mode": "chat",
                "context_size": "512",
                "max_tokens_to_sample": "512",
                "stream_mode_delimiter": "\\r\\n\\r\\n",
                "endpoint_url": params.get('endpoint_url'),
                "task_id": params.get('task_id'),
                "employee_number": params.get('employee_number')
            },
            'load_balancing': {
                "enabled": False,
                "configs": []
            }
        }
        model_load_balancing_service = ModelLoadBalancingService()

        model_load_balancing_service.disable_model_load_balancing(
            tenant_id=tenant_id,
            provider=provider,
            model=model,
            model_type=args['model_type']
        )

        if args.get('config_from', '') != 'predefined-model':
            model_provider_service = ModelProviderService()

            try:
                model_provider_service.save_model_credentials(
                    tenant_id=tenant_id,
                    provider=provider,
                    model=model,
                    model_type=args['model_type'],
                    credentials=args['credentials']
                )
            except CredentialsValidateFailedError as ex:
                raise ValueError(str(ex))

        return {'result': 'success'}, 200


class DeleteToolChainInterface(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('model_name', type=str, required=True, nullable=False, location='json')
        parser.add_argument('task_id', type=str, required=True, nullable=False, location='json')
        params = parser.parse_args()

        account_service = AccountService()
        tenant_id = account_service.get_tenant_id_by_model_name(params.get('model_name') + '_' + params.get('task_id'))
        logging.info(f"delete_tenant_id:{tenant_id}")
        if tenant_id is None:
            # 模型未找到, 无需删除, 直接返回成功
            return {'result': 'success'}, 200
        provider = 'tool_chain'

        model_provider_service = ModelProviderService()
        model_provider_service.remove_model_credentials(
            tenant_id=tenant_id,
            provider=provider,
            model=params.get('model_name') + '_' + params.get('task_id'),
            model_type='llm',
            del_setting=True
        )

        return {'result': 'success'}, 200


api.add_resource(CreateToolChainInterface, '/tool_chain/models/create')
api.add_resource(DeleteToolChainInterface, '/tool_chain/models/delete')
