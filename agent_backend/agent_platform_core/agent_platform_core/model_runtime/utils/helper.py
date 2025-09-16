from typing import AsyncIterator, AsyncGenerator, Generator

import httpx
import pydantic
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


def dump_model(model: BaseModel) -> dict:
    if hasattr(pydantic, 'model_dump'):
        return pydantic.model_dump(model)
    else:
        return model.model_dump()


async def httpx_stream_aiter_lines(response: httpx.Response, delimiter: str) -> AsyncGenerator[str, None]:
    buffer = b""
    delimiter_bytes = delimiter.encode('utf-8')
    async for chunk in response.aiter_bytes():
        buffer += chunk
        while delimiter_bytes in buffer:
            line, buffer = buffer.split(delimiter_bytes, 1)
            logger.debug(line.decode('utf-8'))
            yield line.decode('utf-8')  # 手动解码
    if buffer:
        yield buffer.decode('utf-8')  # 处理剩余内容


def sync_http_stream_aiter_lines(response: httpx.Response, delimiter: str) -> Generator[str, None, None]:
    buffer = b""
    delimiter_bytes = delimiter.encode('utf-8')
    for chunk in response.iter_bytes():
        buffer += chunk
        while delimiter_bytes in buffer:
            line, buffer = buffer.split(delimiter_bytes, 1)
            logger.debug(line.decode('utf-8'))
            yield line.decode('utf-8')
    if buffer:
        yield buffer.decode('utf-8')
