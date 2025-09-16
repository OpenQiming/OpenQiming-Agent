import logging
import time

import click
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.models.db_model.dataset import AppDatasetJoin
from agent_platform_core.models.db_model.model import (
    ApiToken,
    AppAnnotationHitHistory,
    AppAnnotationSetting,
    AppModelConfig,
    Conversation,
    EndUser,
    InstalledApp,
    Message,
    MessageAgentThought,
    MessageChain,
    MessageFeedback,
    MessageFile,
    RecommendedApp,
    Site,
    TagBinding, MessageAnnotation,
)
from agent_platform_core.models.db_model.tools import WorkflowToolProvider
from agent_platform_core.models.db_model.workflow import Workflow, WorkflowAppLog, WorkflowNodeExecution, WorkflowRun
from agent_platform_service.models.db_model.web import PinnedConversation, SavedMessage


async def remove_app_and_related_data_task_async(app_id: str, session: AsyncSession):
    logging.info(click.style(f'Start deleting app and related data: {app_id}', fg='green'))
    start_at = time.perf_counter()
    try:
        # Use a transaction to ensure all deletions succeed or none do
        # with session.begin():
        # Delete related data
        await _delete_app_model_configs(app_id, session)
        await _delete_app_site(app_id, session)
        await _delete_app_api_tokens(app_id, session)
        await _delete_installed_apps(app_id, session)
        await _delete_recommended_apps(app_id, session)
        await _delete_app_annotation_data(app_id, session)
        await _delete_app_dataset_joins(app_id, session)
        await _delete_app_workflows(app_id, session)
        await _delete_app_conversations(app_id, session)
        await _delete_app_messages(app_id, session)
        await _delete_workflow_tool_providers(app_id, session)
        await _delete_app_tag_bindings(app_id, session)
        await _delete_end_users(app_id, session)

        # If we reach here, the transaction was successful
        await session.commit()

        end_at = time.perf_counter()
        logging.info(click.style(f'App and related data deleted: {app_id} latency: {end_at - start_at}', fg='green'))

    except SQLAlchemyError as e:
        await session.rollback()
        logging.exception(
            click.style(f"Database error occurred while deleting app {app_id} and related data", fg='red'))
        raise Exception(click.style(f"Database error occurred while deleting app {app_id} and related data", fg='red')) # Retry after 60 seconds

    except Exception as e:
        logging.exception(click.style(f"Error occurred while deleting app {app_id} and related data", fg='red'))
        raise Exception(click.style(f"Error occurred while deleting app {app_id} and related data", fg='red'))  # Retry after 60 seconds


async def _delete_app_model_configs(app_id: str, session: AsyncSession):
    await session.execute(delete(AppModelConfig).filter(AppModelConfig.app_id == app_id))


async def _delete_app_site(app_id: str, session: AsyncSession):
    await session.execute(delete(Site).filter(Site.app_id == app_id))


async def _delete_app_api_tokens(app_id: str, session: AsyncSession):
    await session.execute(delete(ApiToken).filter(ApiToken.app_id == app_id))


async def _delete_installed_apps(app_id: str, session: AsyncSession):
    await session.execute(delete(InstalledApp).filter(InstalledApp.app_id == app_id))


async def _delete_recommended_apps(app_id: str, session: AsyncSession):
    await session.execute(delete(RecommendedApp).filter(RecommendedApp.app_id == app_id))


async def _delete_app_annotation_data(app_id: str, session: AsyncSession):
    await session.execute(delete(AppAnnotationHitHistory).filter(AppAnnotationHitHistory.app_id == app_id))
    await session.execute(delete(AppAnnotationSetting).filter(AppAnnotationSetting.app_id == app_id))


async def _delete_app_dataset_joins(app_id: str, session: AsyncSession):
    await session.execute(delete(AppDatasetJoin).filter(AppDatasetJoin.app_id == app_id))


async def _delete_app_workflows(app_id: str, session: AsyncSession):
    data = await session.execute(select(Workflow.id).filter(Workflow.app_id == app_id))
    data = data.scalars().all()
    await session.execute(delete(WorkflowRun).filter(
        WorkflowRun.workflow_id.in_(
            data
        )
    ))
    data2 = await session.execute(select(Workflow.id).filter(Workflow.app_id == app_id))
    data2 = data2.scalars().all()
    await session.execute(delete(WorkflowNodeExecution).filter(
        WorkflowNodeExecution.workflow_id.in_(
            data2
        )
    ))
    await session.execute(delete(WorkflowAppLog).filter(WorkflowAppLog.app_id == app_id))
    await session.execute(delete(Workflow).filter(Workflow.app_id == app_id))


async def _delete_app_conversations(app_id: str, session: AsyncSession):
    data = await session.execute(select(Conversation.id).filter(Conversation.app_id == app_id))
    data = data.scalars().all()
    await session.execute(delete(PinnedConversation).filter(
        PinnedConversation.conversation_id.in_(
            data
        )
    ))
    await session.execute(delete(Conversation).filter(Conversation.app_id == app_id))


async def _delete_app_messages(app_id: str, session: AsyncSession):
    message_ids = await session.execute(select(Message.id).filter(Message.app_id == app_id))
    message_ids = message_ids.scalars().all()
    await session.execute(delete(MessageFeedback).filter(MessageFeedback.message_id.in_(message_ids)))
    await session.execute(delete(MessageAnnotation).filter(MessageAnnotation.message_id.in_(message_ids)))
    await session.execute(delete(MessageChain).filter(MessageChain.message_id.in_(message_ids)))
    await session.execute(delete(MessageAgentThought).filter(MessageAgentThought.message_id.in_(message_ids)))
    await session.execute(delete(MessageFile).filter(MessageFile.message_id.in_(message_ids)))
    await session.execute(delete(SavedMessage).filter(SavedMessage.message_id.in_(message_ids)))
    await session.execute(delete(Message).filter(Message.app_id == app_id))


async def _delete_workflow_tool_providers(app_id: str, session: AsyncSession):
    await session.execute(delete(WorkflowToolProvider).where(WorkflowToolProvider.app_id == app_id))


async def _delete_app_tag_bindings(app_id: str, session: AsyncSession):
    await session.execute(delete(TagBinding).where(TagBinding.target_id == app_id))


async def _delete_end_users(app_id: str, session: AsyncSession):
    await session.execute(delete(EndUser).where(EndUser.app_id == app_id))
