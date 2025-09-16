from agent_platform_core.app.apps.async_base_app_queue_manager import AsyncAppQueueManager, GenerateTaskStoppedError, PublishFrom
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.app.entities.queue_entities import (
    AppQueueEvent,
    MessageQueueMessage,
    QueueAdvancedChatMessageEndEvent,
    QueueErrorEvent,
    QueueMessage,
    QueueMessageEndEvent,
    QueueStopEvent,
)


class AsyncMessageBasedAppQueueManager(AsyncAppQueueManager):
    def __init__(
        self, task_id: str, user_id: str, invoke_from: InvokeFrom, conversation_id: str, app_mode: str, message_id: str
    ) -> None:
        super().__init__(task_id, user_id, invoke_from)

        self._conversation_id = str(conversation_id)
        self._app_mode = app_mode
        self._message_id = str(message_id)

    def construct_queue_message(self, event: AppQueueEvent) -> QueueMessage:
        return MessageQueueMessage(
            task_id=self._task_id,
            message_id=self._message_id,
            conversation_id=self._conversation_id,
            app_mode=self._app_mode,
            event=event,
        )

    async def _publish(self, event: AppQueueEvent, pub_from: PublishFrom) -> None:
        """
        Publish event to queue
        :param event:
        :param pub_from:
        :return:
        """
        message = MessageQueueMessage(
            task_id=self._task_id,
            message_id=self._message_id,
            conversation_id=self._conversation_id,
            app_mode=self._app_mode,
            event=event,
        )

        await self._q.put(message)

        if isinstance(
            event, QueueStopEvent | QueueErrorEvent | QueueMessageEndEvent | QueueAdvancedChatMessageEndEvent
        ):
            await self.stop_listen()

        if pub_from == PublishFrom.APPLICATION_MANAGER and await self._is_stopped():
            raise GenerateTaskStoppedError()
