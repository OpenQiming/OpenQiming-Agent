import logging

from agent_platform_basic.exceptions.model_runtime.validate import CredentialsValidateFailedError
from agent_platform_core.model_runtime.entities.model_entities import ModelType
from agent_platform_core.model_runtime.model_providers.__base.model_provider import ModelProvider

"""
@Date    ：2024/7/10 12:04 
@Version: 1.0
@Description:

"""
logger = logging.getLogger(__name__)


class ToolChainProvider(ModelProvider):

    def validate_provider_credentials(self, credentials: dict) -> None:
        """
        Validate provider credentials
        if validate failed, raise exception

        :param credentials: provider credentials, credentials form defined in `provider_credential_schema`.
        """
        try:
            model_instance = self.get_model_instance(ModelType.LLM)

            model_instance.validate_credentials(
                model=credentials.get('model', 'Qwen'),
                credentials=credentials
            )
        except CredentialsValidateFailedError as ex:
            raise ex
        except Exception as ex:
            logger.exception(f'{self.get_provider_schema().provider} credentials validate failed')
            raise ex
