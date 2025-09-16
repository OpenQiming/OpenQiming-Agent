import logging

from agent_platform_core.tools.entities.api_entities import UserToolProviderTypeLiteral
from agent_platform_core.tools.async_tool_manager import AsyncToolManager
from agent_platform_service.services.tools.tools_transform_service import ToolTransformService

logger = logging.getLogger(__name__)


class ToolCommonService:
    @staticmethod
    async def list_tool_providers(user_id: str, tenant_id: str, typ: UserToolProviderTypeLiteral = None):
        """
        list tool providers

        :return: the list of tool providers
        """
        providers = await AsyncToolManager.user_list_providers(user_id, tenant_id, typ)

        # add icon
        for provider in providers:
            ToolTransformService.repack_provider(provider)

        result = [provider.to_dict() for provider in providers]

        return result
