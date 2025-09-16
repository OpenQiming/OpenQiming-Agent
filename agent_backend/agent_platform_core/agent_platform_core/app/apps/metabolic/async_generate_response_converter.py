import json
from typing import cast, AsyncGenerator

from agent_platform_core.app.apps.async_base_app_generate_response_converter import AsyncAppGenerateResponseConverter
from agent_platform_core.app.entities.task_entities import (
    ErrorStreamResponse,
    NodeFinishStreamResponse,
    NodeStartStreamResponse,
    PingStreamResponse,
    WorkflowAppBlockingResponse,
    WorkflowAppStreamResponse,
)


class AsyncMetabolicAppGenerateResponseConverter(AsyncAppGenerateResponseConverter):
    _blocking_response_type = WorkflowAppBlockingResponse

    @classmethod
    def convert_blocking_full_response(cls, blocking_response: WorkflowAppBlockingResponse) -> dict:
        """
        Convert blocking full response.
        :param blocking_response: blocking response
        :return:
        """
        return blocking_response.to_dict()

    @classmethod
    def convert_blocking_simple_response(cls, blocking_response: WorkflowAppBlockingResponse) -> dict:
        """
        Convert blocking simple response.
        :param blocking_response: blocking response
        :return:
        """
        return cls.convert_blocking_full_response(blocking_response)

    @classmethod
    async def convert_stream_full_response(
        cls, stream_response: AsyncGenerator[WorkflowAppStreamResponse, None]
    ) -> AsyncGenerator[str, None]:
        """
        Convert stream full response.
        :param stream_response: stream response
        :return:
        """
        async for chunk in stream_response:
            chunk = cast(WorkflowAppStreamResponse, chunk)
            sub_stream_response = chunk.stream_response

            if isinstance(sub_stream_response, PingStreamResponse):
                yield "ping"
                continue

            response_chunk = {
                "event": sub_stream_response.event.value,
                "workflow_run_id": chunk.workflow_run_id,
            }

            if isinstance(sub_stream_response, ErrorStreamResponse):
                data = cls._error_to_stream_response(sub_stream_response.err)
                response_chunk.update(data)
            else:
                response_chunk.update(sub_stream_response.to_dict())
            yield json.dumps(response_chunk, ensure_ascii=False)

    @classmethod
    async def convert_stream_simple_response(
        cls, stream_response: AsyncGenerator[WorkflowAppStreamResponse, None]
    ) -> AsyncGenerator[str, None]:
        """
        Convert stream simple response.
        :param stream_response: stream response
        :return:
        """
        async for chunk in stream_response:
            chunk = cast(WorkflowAppStreamResponse, chunk)
            sub_stream_response = chunk.stream_response

            if isinstance(sub_stream_response, PingStreamResponse):
                yield "ping"
                continue

            response_chunk = {
                "event": sub_stream_response.event.value,
                "workflow_run_id": chunk.workflow_run_id,
            }

            if isinstance(sub_stream_response, ErrorStreamResponse):
                data = cls._error_to_stream_response(sub_stream_response.err)
                response_chunk.update(data)
            elif isinstance(sub_stream_response, NodeStartStreamResponse | NodeFinishStreamResponse):
                response_chunk.update(sub_stream_response.to_ignore_detail_dict())
            else:
                response_chunk.update(sub_stream_response.to_dict())
            yield json.dumps(response_chunk, ensure_ascii=False)
