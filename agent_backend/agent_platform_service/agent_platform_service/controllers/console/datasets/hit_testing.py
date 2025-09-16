import logging

from flask_login import current_user
from flask_restful import Resource, marshal, reqparse
from werkzeug.exceptions import Forbidden, InternalServerError, NotFound

from agent_platform_basic.exceptions.controllers.console.app import (
    CompletionRequestError,
    ProviderModelCurrentlyNotSupportError,
    ProviderNotInitializeError,
    ProviderQuotaExceededError,
)
from agent_platform_basic.exceptions.controllers.console.datasets import DatasetNotInitializedError
from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.exceptions.services.account import NoPermissionError
from agent_platform_basic.exceptions.services.index import IndexNotInitializedError
from agent_platform_basic.libs.login import login_required
from agent_platform_core.errors.error import (
    LLMBadRequestError,
    ModelCurrentlyNotSupportError,
    ProviderTokenNotInitError,
    QuotaExceededError,
)
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.fields.hit_testing_fields import hit_testing_record_fields
from agent_platform_service.services.dataset_service import DatasetService
from agent_platform_service.services.hit_testing_service import HitTestingService


class HitTestingApi(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    def post(self, dataset_id):
        dataset_id_str = str(dataset_id)

        dataset = DatasetService.get_dataset(dataset_id_str)
        if dataset is None:
            raise NotFound("Dataset not found.")

        # try:
        #     DatasetService.check_dataset_permission(dataset, current_user, tenant_id)
        # except NoPermissionError as e:
        #     raise Forbidden(str(e))

        parser = reqparse.RequestParser()
        parser.add_argument('query', type=str, location='json')
        parser.add_argument('retrieval_model', type=dict, required=False, location='json')
        args = parser.parse_args()

        HitTestingService.hit_testing_args_check(args)

        try:
            response = HitTestingService.retrieve(
                dataset=dataset,
                query=args['query'],
                account=current_user,
                retrieval_model=args['retrieval_model'],
                limit=10
            )

            return {"query": response['query'], 'records': marshal(response['records'], hit_testing_record_fields)}
        except IndexNotInitializedError:
            raise DatasetNotInitializedError()
        except ProviderTokenNotInitError as ex:
            raise ProviderNotInitializeError(ex.description)
        except QuotaExceededError:
            raise ProviderQuotaExceededError()
        except ModelCurrentlyNotSupportError:
            raise ProviderModelCurrentlyNotSupportError()
        except LLMBadRequestError:
            raise ProviderNotInitializeError(
                "No Embedding Model or Reranking Model available. Please configure a valid provider "
                "in the Settings -> Model Provider.")
        except InvokeError as e:
            raise CompletionRequestError(e.description)
        except ValueError as e:
            raise ValueError(str(e))
        except Exception as e:
            logging.exception("Hit testing failed.")
            raise InternalServerError(str(e))


api.add_resource(HitTestingApi, '/datasets/<uuid:dataset_id>/hit-testing')
