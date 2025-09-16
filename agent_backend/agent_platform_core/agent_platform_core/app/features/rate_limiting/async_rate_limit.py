import logging
import time
import uuid
from collections.abc import Mapping
from datetime import timedelta
from typing import Any, Optional, Union, AsyncGenerator

from agent_platform_core.errors.error import AppInvokeQuotaExceededError
from agent_platform_basic.extensions.ext_redis import async_redis_client

logger = logging.getLogger(__name__)


class AsyncRateLimit:
    _MAX_ACTIVE_REQUESTS_KEY = "agent_platform:rate_limit:{}:max_active_requests"
    _ACTIVE_REQUESTS_KEY = "agent_platform:rate_limit:{}:active_requests"
    _UNLIMITED_REQUEST_ID = "unlimited_request_id"
    _REQUEST_MAX_ALIVE_TIME = 10 * 60  # 10 minutes
    _ACTIVE_REQUESTS_COUNT_FLUSH_INTERVAL = 5 * 60  # recalculate request_count from request_detail every 5 minutes
    _instance_dict = {}

    def __new__(cls: type["AsyncRateLimit"], client_id: str, max_active_requests: int):
        if client_id not in cls._instance_dict:
            instance = super().__new__(cls)
            cls._instance_dict[client_id] = instance
        return cls._instance_dict[client_id]

    def __init__(self, client_id: str, max_active_requests: int):
        self.max_active_requests = max_active_requests
        if hasattr(self, "initialized"):
            return
        self.initialized = True
        self.client_id = client_id
        self.active_requests_key = self._ACTIVE_REQUESTS_KEY.format(client_id)
        self.max_active_requests_key = self._MAX_ACTIVE_REQUESTS_KEY.format(client_id)
        self.last_recalculate_time = float("-inf")

    @classmethod
    async def create(cls, client_id: str, max_active_requests: int):
        rate_limit = cls(client_id, max_active_requests)
        await rate_limit.flush_cache(use_local_value=True)
        return rate_limit

    async def flush_cache(self, use_local_value=False):
        self.last_recalculate_time = time.time()
        # flush max active requests
        if use_local_value or not await async_redis_client.exists(self.max_active_requests_key):
            async with async_redis_client.pipeline(transaction=True) as pipe:
                await (
                    pipe
                    .set(self.max_active_requests_key, self.max_active_requests)
                    .expire(self.max_active_requests_key, timedelta(days=1))
                    .execute()
                )
        else:
            val_byte = await async_redis_client.get(self.max_active_requests_key)
            if val_byte is not None:
                self.max_active_requests = int(val_byte.decode("utf-8"))
                await async_redis_client.expire(self.max_active_requests_key, timedelta(days=1))

        # flush max active requests (in-transit request list)
        if not await async_redis_client.exists(self.active_requests_key):
            return
        request_details = await async_redis_client.hgetall(self.active_requests_key)
        await async_redis_client.expire(self.active_requests_key, timedelta(days=1))
        timeout_requests = [
            k
            for k, v in request_details.items()
            if time.time() - float(v.decode("utf-8")) > AsyncRateLimit._REQUEST_MAX_ALIVE_TIME
        ]
        if timeout_requests:
            await async_redis_client.hdel(self.active_requests_key, *timeout_requests)

    async def enter(self, request_id: Optional[str] = None) -> str:
        if time.time() - self.last_recalculate_time > AsyncRateLimit._ACTIVE_REQUESTS_COUNT_FLUSH_INTERVAL:
            await self.flush_cache()
        if self.max_active_requests <= 0:
            return AsyncRateLimit._UNLIMITED_REQUEST_ID
        if not request_id:
            request_id = AsyncRateLimit.gen_request_key()

        active_requests_count = await async_redis_client.hlen(self.active_requests_key)
        if active_requests_count >= self.max_active_requests:
            raise AppInvokeQuotaExceededError(
                "Too many requests. Please try again later. The current maximum "
                "concurrent requests allowed is {}.".format(self.max_active_requests)
            )
        await async_redis_client.hset(self.active_requests_key, request_id, str(time.time()))
        return request_id

    async def exit(self, request_id: str):
        if request_id == AsyncRateLimit._UNLIMITED_REQUEST_ID:
            return
        await async_redis_client.hdel(self.active_requests_key, request_id)

    @staticmethod
    def gen_request_key() -> str:
        return str(uuid.uuid4())

    def generate(self, generator: Union[AsyncGenerator[str, None], Mapping[str, Any]], request_id: str):
        if isinstance(generator, Mapping):
            return generator
        else:
            return AsyncRateLimitGenerator(rate_limit=self, generator=generator, request_id=request_id)


class AsyncRateLimitGenerator:
    def __init__(self, rate_limit: AsyncRateLimit, generator: AsyncGenerator[str, None], request_id: str):
        self.rate_limit = rate_limit
        self.generator = generator
        self.request_id = request_id
        self.closed = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.closed:
            raise StopIteration
        try:
            return await self.generator.__anext__()
        except StopIteration:
            await self.aclose()
            raise

    async def aclose(self):
        if not self.closed:
            self.closed = True
            await self.rate_limit.exit(self.request_id)
            if self.generator is not None and hasattr(self.generator, "aclose"):
                await self.generator.aclose()
