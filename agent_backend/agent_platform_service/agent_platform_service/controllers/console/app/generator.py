from flask_login import current_user
from flask_restful import Resource, reqparse

from agent_platform_basic.exceptions.controllers.console.app import (
    CompletionRequestError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.libs.login import login_required
from agent_platform_core.errors.error import (
    ModelCurrentlyNotSupportError,
    ProviderTokenNotInitError,
    QuotaExceededError
)
from agent_platform_core.llm_generator.llm_generator import LLMGenerator
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required


class RuleGenerateApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('audiences', type=str, required=True, nullable=False, location='json')
        parser.add_argument('hoping_to_solve', type=str, required=True, nullable=False, location='json')
        args = parser.parse_args()

        account = current_user

        try:
            rules = LLMGenerator.generate_rule_config(
                account.current_tenant_id,
                args['audiences'],
                args['hoping_to_solve']
            )
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except InvokeError as e:
            raise CompletionRequestError(e.description)

        return rules


api.add_resource(RuleGenerateApi, '/rule-generate')
