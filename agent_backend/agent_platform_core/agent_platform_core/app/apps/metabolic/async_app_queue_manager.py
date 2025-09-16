from agent_platform_core.app.apps.async_base_app_queue_manager import AsyncAppQueueManager, GenerateTaskStoppedError, PublishFrom
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.app.entities.queue_entities import (
    AppQueueEvent,
    QueueErrorEvent,
    QueueMessageEndEvent,
    QueueStopEvent,
    QueueWorkflowFailedEvent,
    QueueWorkflowSucceededEvent,
    WorkflowQueueMessage,
)


class AsyncMetabolicAppQueueManager(AsyncAppQueueManager):
    def __init__(self, task_id: str, user_id: str, invoke_from: InvokeFrom, app_mode: str) -> None:
        super().__init__(task_id, user_id, invoke_from)

        self._app_mode = app_mode

    async def _publish(self, event: AppQueueEvent, pub_from: PublishFrom) -> None:
        """
        Publish event to queue
        :param event:
        :param pub_from:
        :return:
        """
        message = WorkflowQueueMessage(task_id=self._task_id, app_mode=self._app_mode, event=event)

        await self._q.put(message)

        if isinstance(
            event,
            QueueStopEvent
            | QueueErrorEvent
            | QueueMessageEndEvent
            | QueueWorkflowSucceededEvent
            | QueueWorkflowFailedEvent,
        ):
            await self.stop_listen()

        if pub_from == PublishFrom.APPLICATION_MANAGER and self._is_stopped():
            raise GenerateTaskStoppedError()
