import json
from enum import Enum
from json import JSONDecodeError
from typing import Optional

from agent_platform_basic.extensions.ext_redis import redis_client, async_redis_client


class ToolParameterCacheType(Enum):
    PARAMETER = "tool_parameter"
    PARAMETER_ASYNC = "tool_parameter_async"

class ToolParameterCache:
    def __init__(
        self, tenant_id: str, provider: str, tool_name: str, cache_type: ToolParameterCacheType, identity_id: str
    ):
        self.cache_key = (
            f"{cache_type.value}_secret:tenant_id:{tenant_id}:provider:{provider}:tool_name:{tool_name}"
            f":identity_id:{identity_id}"
        )

    def get(self) -> Optional[dict]:
        """
        Get cached model provider credentials.

        :return:
        """
        cached_tool_parameter = redis_client.get(self.cache_key)
        if cached_tool_parameter:
            try:
                cached_tool_parameter = cached_tool_parameter.decode("utf-8")
                cached_tool_parameter = json.loads(cached_tool_parameter)
            except JSONDecodeError:
                return None

            return cached_tool_parameter
        else:
            return None

    def set(self, parameters: dict) -> None:
        """
        Cache model provider credentials.

        :param credentials: provider credentials
        :return:
        """
        redis_client.setex(self.cache_key, 86400, json.dumps(parameters))

    def delete(self) -> None:
        """
        Delete cached model provider credentials.

        :return:
        """
        redis_client.delete(self.cache_key)

class ToolParameterCacheAsync:
    def __init__(self,
            tenant_id: str,
            provider: str,
            tool_name: str,
            cache_type: ToolParameterCacheType,
            identity_id: str
        ):
        self.cache_key = f"{cache_type.value}_secret:tenant_id:{tenant_id}:provider:{provider}:tool_name:{tool_name}:identity_id:{identity_id}"

    async def get(self) -> Optional[dict]:
        """
        Get cached model provider credentials.

        :return:
        """
        cached_tool_parameter = await async_redis_client.get(self.cache_key)
        if cached_tool_parameter:
            try:
                cached_tool_parameter = cached_tool_parameter.decode("utf-8")
                cached_tool_parameter = json.loads(cached_tool_parameter)
            except JSONDecodeError:
                return None

            return cached_tool_parameter
        else:
            return None
    async def set(self, parameters: dict) -> None:
        """
        Cache model provider credentials.

        :return:
        """
        await async_redis_client.setex(self.cache_key, 86400, json.dumps(parameters))

    async def delete(self) -> None:
        """
        Delete cached model provider credentials.

        :return:
        """
        await async_redis_client.delete(self.cache_key)