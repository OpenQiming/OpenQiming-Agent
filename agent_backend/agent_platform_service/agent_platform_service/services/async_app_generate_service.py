from collections.abc import Generator
from typing import Any, Union, Mapping
from fastapi import Depends

from openai._exceptions import RateLimitError

from agent_platform_basic.extensions.ext_database import async_db
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.app.apps.advanced_chat.async_app_generator import AdvancedChatAppGenerator
from agent_platform_core.app.features.rate_limiting.async_rate_limit import AsyncRateLimit
from agent_platform_basic.models.db_model import Account
from agent_platform_core.app.apps.metabolic.async_app_generator import AsyncMetabolicAppGenerator
from agent_platform_core.app.apps.workflow.async_app_generator import AsyncWorkflowAppGenerator
from agent_platform_core.app.apps.agent_chat.async_app_generator import AsyncAgentChatAppGenerator
# from agent_platform_core.app.apps.advanced_chat.app_generator import AdvancedChatAppGenerator
# from agent_platform_core.app.apps.agent_chat.app_generator import AgentChatAppGenerator
# from agent_platform_core.app.apps.chat.app_generator import ChatAppGenerator
# from agent_platform_core.app.apps.completion.app_generator import CompletionAppGenerator
# from agent_platform_core.app.apps.workflow.app_generator import WorkflowAppGenerator
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.errors.error import InvokeRateLimitError
from agent_platform_core.models.db_model.model import App, EndUser
from agent_platform_core.models.db_model.workflow import Workflow
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.services.workflow_service import WorkflowService


class AsyncAppGenerateService:

    def __init__(self,
                 async_workflow_app_generator: AsyncWorkflowAppGenerator = Depends(AsyncWorkflowAppGenerator),
                 async_agent_chat_app_generator: AsyncAgentChatAppGenerator = Depends(AsyncAgentChatAppGenerator),
                 async_metabolic_app_generator: AsyncMetabolicAppGenerator = Depends(AsyncMetabolicAppGenerator),
                 async_advanced_chat_app_generator:AdvancedChatAppGenerator = Depends(AdvancedChatAppGenerator)):
        self.async_workflow_app_generator = async_workflow_app_generator
        self.async_agent_chat_app_generator = async_agent_chat_app_generator
        self.async_metabolic_app_generator = async_metabolic_app_generator
        self.async_advanced_chat_app_generator = async_advanced_chat_app_generator

    async def generate(
        self,
        app_model: App,
        user: Union[Account, EndUser],
        args: Mapping[str, Any],
        invoke_from: InvokeFrom,
        streaming: bool = True,
    ):
        """
        App Content Generate
        :param app_model: app model
        :param user: user
        :param args: args
        :param invoke_from: invoke from
        :param streaming: streaming
        :return:
        """
        max_active_request = self._get_max_active_requests(app_model)
        rate_limit = await AsyncRateLimit.create(app_model.id, max_active_request)
        request_id = AsyncRateLimit.gen_request_key()
        try:
            request_id = await rate_limit.enter(request_id)
            # if app_model.mode == AppMode.COMPLETION.value:
            #     return rate_limit.generate(
            #         generator=CompletionAppGenerator().generate(
            #             app_model=app_model,
            #             user=user,
            #             args=args,
            #             invoke_from=invoke_from,
            #             streaming=streaming,
            #         ),
            #         request_id=request_id,
            #     )
            print(f"=============2======={app_model.mode}")
            if app_model.mode == AppMode.AGENT_CHAT.value or app_model.is_agent:
                generator = await self.async_agent_chat_app_generator.generate(
                    app_model=app_model,
                    user=user,
                    args=args,
                    invoke_from=invoke_from,
                    streaming=streaming,
                )
                return rate_limit.generate(
                    generator=generator,
                    request_id=request_id,
                )
            # elif app_model.mode == AppMode.CHAT.value:
            #     return rate_limit.generate(
            #         generator=ChatAppGenerator().generate(
            #             app_model=app_model,
            #             user=user,
            #             args=args,
            #             invoke_from=invoke_from,
            #             streaming=streaming,
            #         ),
            #         request_id=request_id,
            #     )
            elif app_model.mode == AppMode.ADVANCED_CHAT.value:
                print(f"args:::", args)
                workflow = await self._get_workflow(app_model, invoke_from)
                generator = await self.async_advanced_chat_app_generator.generate(
                    app_model=app_model,
                    workflow=workflow,
                    user=user,
                    args=args,
                    invoke_from=invoke_from,
                    streaming=streaming,
                )

                return rate_limit.generate(
                    generator=generator,
                    request_id=request_id,
                )
            elif app_model.mode == AppMode.WORKFLOW.value or app_model.mode == AppMode.METABOLIC.value:
                workflow = await self._get_workflow(app_model, invoke_from)
                generator = await self.async_workflow_app_generator.generate(
                    app_model=app_model,
                    workflow=workflow,
                    user=user,
                    args=args,
                    invoke_from=invoke_from,
                    streaming=streaming,
                    call_depth=0,
                    workflow_semaphore_id=None,
                )
                return rate_limit.generate(
                    generator=generator,
                    request_id=request_id,
                )
            else:
                raise ValueError(f"Invalid app mode {app_model.mode}")
        except RateLimitError as e:
            raise InvokeRateLimitError(str(e))
        finally:
            if not streaming:
                await rate_limit.exit(request_id)

    @staticmethod
    def _get_max_active_requests(app_model: App) -> int:
        max_active_requests = app_model.max_active_requests
        if app_model.max_active_requests is None:
            max_active_requests = int(agent_platform_config.APP_MAX_ACTIVE_REQUESTS)
        return max_active_requests

    async def generate_single_iteration(self, app_model: App, user: Account, node_id: str, args: Any, streaming: bool = True):
        # if app_model.mode == AppMode.ADVANCED_CHAT.value:
        #     workflow = cls._get_workflow(app_model, InvokeFrom.DEBUGGER)
        #     return AdvancedChatAppGenerator().single_iteration_generate(
        #         app_model=app_model,
        #         workflow=workflow,
        #         node_id=node_id,
        #         user=user,
        #         args=args,
        #         streaming=streaming,
        #     )
        if app_model.mode == AppMode.WORKFLOW.value:
            workflow = await self._get_workflow(app_model, InvokeFrom.DEBUGGER)
            return await self.async_workflow_app_generator.single_iteration_generate(
                app_model=app_model, workflow=workflow, node_id=node_id, user=user, args=args, streaming=streaming
            )
        else:
            raise ValueError(f"Invalid app mode {app_model.mode}")

    @classmethod
    def generate_more_like_this(
        cls,
        app_model: App,
        user: Union[Account, EndUser],
        message_id: str,
        invoke_from: InvokeFrom,
        streaming: bool = True,
    ) -> Union[dict, Generator]:
        """
        Generate more like this
        :param app_model: app model
        :param user: user
        :param message_id: message id
        :param invoke_from: invoke from
        :param streaming: streaming
        :return:
        """
        # return CompletionAppGenerator().generate_more_like_this(
        #     app_model=app_model, message_id=message_id, user=user, invoke_from=invoke_from, stream=streaming
        # )
        pass

    async def _get_workflow(self, app_model: App, invoke_from: InvokeFrom) -> Workflow:
        """
        Get workflow
        :param app_model: app model
        :param invoke_from: invoke from
        :return:
        """
        # fetch workflow by app_model
        async with async_db.AsyncSessionLocal() as session:
            workflow_service = WorkflowService(session)

        if invoke_from == InvokeFrom.DEBUGGER:
            # fetch draft workflow by app_model
            workflow = await workflow_service.get_draft_workflow_async(app_model=app_model)

            if not workflow:
                raise ValueError("Workflow not initialized")
        else:
            # fetch published workflow by app_model
            workflow = await workflow_service.get_published_workflow_async(app_model=app_model)

            if not workflow:
                raise ValueError("Workflow not published")

        return workflow
