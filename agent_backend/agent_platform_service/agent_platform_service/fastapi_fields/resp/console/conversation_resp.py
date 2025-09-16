from typing import Optional

from pydantic import BaseModel, Field

from agent_platform_core.models.db_model.model import Conversation
from agent_platform_service.fastapi_fields.resp.console.annotation_fields import AnnotationFields
from agent_platform_service.fastapi_fields.resp.console.feedback_stat_fields import FeedBackStatFields
from agent_platform_service.fastapi_fields.resp.console.message_fields import MessageFields
from agent_platform_service.fastapi_fields.resp.console.model_config_fields import ModelConfig
from agent_platform_service.fields.model_async.conversation_async import ConversationAsync
from agent_platform_service.utils.apps_common_utils import result_page


class ConversationResp(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    from_source: Optional[str] = None
    from_end_user_id: Optional[str] = None
    from_end_user_session_id: Optional[str] = None
    from_account_id: Optional[str] = None
    name: Optional[str] = None
    summary: Optional[str] = None
    introduction: Optional[str] = None
    read_at: Optional[int] = None
    created_at: Optional[int] = None
    annotated: Optional[bool] = None
    config_fields: ModelConfig = Field(..., alias='model_config')
    message_count: Optional[int] = None
    user_feedback_stats: Optional[FeedBackStatFields] = None
    admin_feedback_stats: Optional[FeedBackStatFields] = None
    message: Optional[MessageFields] = None
    annotation: Optional[AnnotationFields] = None

    @classmethod
    async def to_conversation_with_message_details(cls, conversation: Conversation,
                                                   conversation_async: ConversationAsync):
        model_config = await conversation_async.model_config_async(conversation)
        message = await conversation_async.message_detail_fields_mapper_async(conversation)
        return cls(
            id=conversation.id,
            status=conversation.status,
            from_source=conversation.from_source,
            from_end_user_id=conversation.from_end_user_id,
            from_account_id=conversation.from_account_id,
            created_at=int(conversation.created_at.timestamp()) if conversation.created_at else None,
            model_config=ModelConfig(
                opening_statement=model_config.get('opening_statement'),
                suggested_questions=model_config.get('suggested_questions'),
                model=model_config.get('model'),
                user_input_form=model_config.get('user_input_form'),
                pre_prompt=model_config.get('pre_prompt'),
                agent_mode=model_config.get('agent_mode'),
            ),
            message=message,
        )

    @classmethod
    async def to_conversation(cls, conversation: Conversation,
                              conversation_async: ConversationAsync):
        model_config = await conversation_async.model_config_async(conversation)
        user_feedback_stats = await conversation_async.user_feedback_stats_async(conversation.id)
        admin_feedback_stats = await conversation_async.admin_feedback_stats_async(conversation.id)
        from_end_user_session_id = await conversation_async.from_end_user_session_id_async(
            conversation.from_end_user_id)
        message = await conversation_async.first_message_async(conversation.id)
        annotation = await conversation_async.annotation_async(conversation.id)

        return cls(
            id=conversation.id,
            status=conversation.status,
            from_source=conversation.from_source,
            from_end_user_id=conversation.from_end_user_id,
            from_end_user_session_id=from_end_user_session_id,
            from_account_id=conversation.from_account_id,
            read_at=int(conversation.read_at.timestamp()) if conversation.read_at else None,
            created_at=int(conversation.created_at.timestamp()) if conversation.created_at else None,
            annotation=annotation,
            model_config=ModelConfig(
                opening_statement=model_config.get('opening_statement'),
                suggested_questions=model_config.get('suggested_questions'),
                model=model_config.get('model'),
                user_input_form=model_config.get('user_input_form'),
                pre_prompt=model_config.get('pre_prompt'),
                agent_mode=model_config.get('agent_mode'),
            ),
            user_feedback_stats=user_feedback_stats,
            admin_feedback_stats=admin_feedback_stats,
            message=MessageFields(
                inputs=message.inputs,
                query=message.query,
                message=message.message[0]['text'] if message.message else '',
                answer=message.answer
            ),
        )

    @classmethod
    async def to_conversation_with_summary(cls, conversation: Conversation,
                                           conversation_async: ConversationAsync):
        model_config = await conversation_async.model_config_async(conversation)
        user_feedback_stats = await conversation_async.user_feedback_stats_async(conversation.id)
        admin_feedback_stats = await conversation_async.admin_feedback_stats_async(conversation.id)
        from_end_user_session_id = await conversation_async.from_end_user_session_id_async(
            conversation.from_end_user_id)
        message_count = await conversation_async.message_count_async(conversation.id)
        annotated = await conversation_async.annotated_async(conversation.id)
        summary = await conversation_async.summary_or_query_async(conversation)
        return cls(
            id=conversation.id,
            status=conversation.status,
            from_source=conversation.from_source,
            from_end_user_id=conversation.from_end_user_id,
            from_end_user_session_id=from_end_user_session_id,
            from_account_id=conversation.from_account_id,
            name=conversation.name,
            summary=summary,
            read_at=int(conversation.read_at.timestamp()) if conversation.read_at else None,
            created_at=int(conversation.created_at.timestamp()) if conversation.created_at else None,
            annotated=bool(annotated),
            model_config=model_config,
            user_feedback_stats=user_feedback_stats,
            admin_feedback_stats=admin_feedback_stats,
            message_count=message_count,
        )

    @classmethod
    async def to_conversation_details(cls, conversation: Conversation,
                                      conversation_async: ConversationAsync):
        model_config = await conversation_async.model_config_async(conversation)
        user_feedback_stats = await conversation_async.user_feedback_stats_async(conversation.id)
        admin_feedback_stats = await conversation_async.admin_feedback_stats_async(conversation.id)
        message_count = await conversation_async.message_count_async(conversation.id)
        annotated = await conversation_async.annotated_async(conversation.id)
        return cls(
            id=conversation.id,
            status=conversation.status,
            from_source=conversation.from_source,
            from_end_user_id=conversation.from_end_user_id,
            from_account_id=conversation.from_account_id,
            introduction=conversation.introduction,
            created_at=int(conversation.created_at.timestamp()) if conversation.created_at else None,
            annotated=bool(annotated),
            model_config=model_config,
            user_feedback_stats=user_feedback_stats,
            admin_feedback_stats=admin_feedback_stats,
            message_count=message_count,
        )


class PaginateConversationResp(BaseModel):
    data: list[ConversationResp]
    total: int
    page: int
    limit: int
    has_more: bool

    @classmethod
    def get_result(cls, datas, total, page, limit):
        result = result_page(datas, total, page, limit)
        return cls(
            data=result.get('data'),
            total=result.get('total'),
            page=result.get('page'),
            limit=result.get('limit'),
            has_more=result.get('has_more'),
        )
