import logging
from sqlalchemy import select
from typing import Optional, cast

from agent_platform_common.configs import agent_platform_config
from agent_platform_core.app.apps.async_base_app_queue_manager import AsyncAppQueueManager
from agent_platform_core.app.apps.metabolic.app_config_manager import MetabolicAppConfig
from agent_platform_core.app.apps.async_workflow_app_runner import AsyncWorkflowBasedAppRunner
from agent_platform_core.app.entities.app_invoke_entities import (
    InvokeFrom,
    WorkflowAppGenerateEntity,
)
from agent_platform_core.workflow.callbacks import WorkflowCallback, WorkflowLoggingCallback
from agent_platform_core.workflow.entities.variable_pool import VariablePool
from agent_platform_core.workflow.enums import SystemVariableKey
from agent_platform_core.workflow.async_workflow_entry import WorkflowEntry
from agent_platform_basic.extensions.ext_database import async_db
from agent_platform_core.models.enum_model.enums import UserFrom
from agent_platform_core.models.db_model.model import App, EndUser
from agent_platform_core.models.enum_model.workflow import WorkflowType

logger = logging.getLogger(__name__)


class AsyncMetabolicAppRunner(AsyncWorkflowBasedAppRunner):
    """
    Workflow Application Runner
    """

    def __init__(
        self,
        application_generate_entity: WorkflowAppGenerateEntity,
        queue_manager: AsyncAppQueueManager,
        workflow_semaphore_id: Optional[str] = None,
    ) -> None:
        """
        :param application_generate_entity: application generate entity
        :param queue_manager: application queue manager
        :param workflow_semaphore_id: workflow semaphore id
        """
        self.application_generate_entity = application_generate_entity
        self.queue_manager = queue_manager
        self.workflow_semaphore_id = workflow_semaphore_id

    async def run(self) -> None:
        """
        Run application
        :return:
        """
        app_config = self.application_generate_entity.app_config
        app_config = cast(MetabolicAppConfig, app_config)

        user_id = None
        async with async_db.AsyncSessionLocal() as session:
            if self.application_generate_entity.invoke_from in {InvokeFrom.WEB_APP, InvokeFrom.SERVICE_API}:
                end_user = await session.execute(
                    select(EndUser).filter(EndUser.id == self.application_generate_entity.user_id))
                end_user = end_user.scalar_one_or_none()
                if end_user:
                    user_id = end_user.session_id
            else:
                user_id = self.application_generate_entity.user_id

            app_record = await session.execute(select(App).filter(App.id == app_config.app_id))
            app_record = app_record.scalar_one_or_none()
        if not app_record:
            raise ValueError("App not found")

        workflow = await self.get_workflow(app_model=app_record, workflow_id=app_config.workflow_id)
        if not workflow:
            raise ValueError("Workflow not initialized")

        workflow_callbacks: list[WorkflowCallback] = []
        if agent_platform_config.DEBUG:
            workflow_callbacks.append(WorkflowLoggingCallback())

        # if only single iteration run is requested
        if self.application_generate_entity.single_iteration_run:
            # if only single iteration run is requested
            graph, variable_pool = await self._get_graph_and_variable_pool_of_single_iteration(
                workflow=workflow,
                node_id=self.application_generate_entity.single_iteration_run.node_id,
                user_inputs=self.application_generate_entity.single_iteration_run.inputs,
            )
        else:
            inputs = self.application_generate_entity.inputs
            files = self.application_generate_entity.files

            # Create a variable pool.
            system_inputs = {
                SystemVariableKey.FILES: files,
                SystemVariableKey.USER_ID: user_id,
                SystemVariableKey.APP_ID: app_config.app_id,
                SystemVariableKey.WORKFLOW_ID: app_config.workflow_id,
                SystemVariableKey.WORKFLOW_RUN_ID: self.application_generate_entity.workflow_run_id,
            }

            variable_pool = VariablePool(
                system_variables=system_inputs,
                user_inputs=inputs,
                environment_variables=workflow.environment_variables,
                conversation_variables=[],
            )

            # init graph
            graph = self._init_graph(graph_config=workflow.graph_dict)

        # RUN WORKFLOW
        workflow_entry = WorkflowEntry(
            tenant_id=workflow.tenant_id,
            app_id=workflow.app_id,
            workflow_id=workflow.id,
            workflow_type=WorkflowType.value_of(workflow.type),
            graph=graph,
            graph_config=workflow.graph_dict,
            user_id=self.application_generate_entity.user_id,
            user_from=(
                UserFrom.ACCOUNT
                if self.application_generate_entity.invoke_from in {InvokeFrom.EXPLORE, InvokeFrom.DEBUGGER}
                else UserFrom.END_USER
            ),
            invoke_from=self.application_generate_entity.invoke_from,
            call_depth=self.application_generate_entity.call_depth,
            variable_pool=variable_pool,
            semaphore_id=self.workflow_semaphore_id,
        )

        generator = workflow_entry.run(callbacks=workflow_callbacks)

        async for event in generator:
            await self._handle_event(workflow_entry, event)
