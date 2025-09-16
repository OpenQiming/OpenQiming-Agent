import logging
import time
from typing import Optional, Union

from sqlalchemy import select

from agent_platform_core.app.apps.async_base_app_queue_manager import AsyncAppQueueManager
from agent_platform_core.app.entities.app_invoke_entities import (
    AppGenerateEntity,
)
from agent_platform_core.app.entities.queue_entities import (
    QueueErrorEvent,
)
from agent_platform_core.app.entities.task_entities import (
    ErrorStreamResponse,
    PingStreamResponse,
    TaskState,
)
from agent_platform_core.errors.error import QuotaExceededError
from agent_platform_core.model_runtime.errors.invoke import InvokeAuthorizationError, InvokeError
from agent_platform_core.moderation.async_output_moderation import ModerationRule, AsyncOutputModeration
from agent_platform_basic.extensions.ext_database import async_db
from agent_platform_basic.models.db_model.account import Account
from agent_platform_core.models.db_model.model import EndUser, Message

logger = logging.getLogger(__name__)


class AsyncBasedGenerateTaskPipeline:
    """
    BasedGenerateTaskPipeline is a class that generate stream output and state management for Application.
    """

    _task_state: TaskState
    _application_generate_entity: AppGenerateEntity

    def __init__(
        self,
        application_generate_entity: AppGenerateEntity,
        queue_manager: AsyncAppQueueManager,
        user: Union[Account, EndUser],
        stream: bool,
    ) -> None:
        """
        Initialize GenerateTaskPipeline.
        :param application_generate_entity: application generate entity
        :param queue_manager: queue manager
        :param user: user
        :param stream: stream
        """
        self._application_generate_entity = application_generate_entity
        self._queue_manager = queue_manager
        self._user = user
        self._start_at = time.perf_counter()
        self._output_moderation_handler = self._init_output_moderation()
        self._stream = stream

    async def _handle_error(self, event: QueueErrorEvent, message: Optional[Message] = None):
        """
        Handle error event.
        :param event: event
        :param message: message
        :return:
        """
        logger.debug("error: %s", event.error)
        e = event.error

        if isinstance(e, InvokeAuthorizationError):
            err = InvokeAuthorizationError("Incorrect API key provided")
        elif isinstance(e, InvokeError | ValueError):
            err = e
        else:
            err = Exception(e.description if getattr(e, "description", None) is not None else str(e))

        if message:
            async with async_db.AsyncSessionLocal() as session:
                refetch_message = await session.execute(select(Message).filter(Message.id == message.id))
                refetch_message = refetch_message.scalar_one_or_none()

                if refetch_message:
                    err_desc = self._error_to_desc(err)
                    refetch_message.status = "error"
                    refetch_message.error = err_desc

                    await session.commit()

        return err

    def _error_to_desc(self, e: Exception) -> str:
        """
        Error to desc.
        :param e: exception
        :return:
        """
        if isinstance(e, QuotaExceededError):
            return (
                "Your quota for Agent Platform Hosted Model Provider has been exhausted. "
                "Please go to Settings -> Model Provider to complete your own provider credentials."
            )

        message = getattr(e, "description", str(e))
        if not message:
            message = "Internal Server Error, please contact support."

        return message

    def _error_to_stream_response(self, e: Exception):
        """
        Error to stream response.
        :param e: exception
        :return:
        """
        return ErrorStreamResponse(task_id=self._application_generate_entity.task_id, err=e)

    def _ping_stream_response(self) -> PingStreamResponse:
        """
        Ping stream response.
        :return:
        """
        return PingStreamResponse(task_id=self._application_generate_entity.task_id)

    def _init_output_moderation(self) -> Optional[AsyncOutputModeration]:
        """
        Init output moderation.
        :return:
        """
        app_config = self._application_generate_entity.app_config
        sensitive_word_avoidance = app_config.sensitive_word_avoidance

        if sensitive_word_avoidance:
            return AsyncOutputModeration(
                tenant_id=app_config.tenant_id,
                app_id=app_config.app_id,
                rule=ModerationRule(type=sensitive_word_avoidance.type, config=sensitive_word_avoidance.config),
                queue_manager=self._queue_manager,
            )

    async def _handle_output_moderation_when_task_finished(self, completion: str) -> Optional[str]:
        """
        Handle output moderation when task finished.
        :param completion: completion
        :return:
        """
        # response moderation
        if self._output_moderation_handler:
            self._output_moderation_handler.stop_thread()

            completion = await self._output_moderation_handler.moderation_completion(
                completion=completion, public_event=False
            )

            self._output_moderation_handler = None

            return completion

        return None
