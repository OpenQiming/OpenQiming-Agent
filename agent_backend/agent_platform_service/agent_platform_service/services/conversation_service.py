from typing import Optional, Union

from sqlalchemy import or_, select

from agent_platform_basic.exceptions.services.conversation import (
    ConversationNotExistsError,
    LastConversationNotExistsError
)
from agent_platform_basic.exceptions.services.message import MessageNotExistsError
from agent_platform_basic.extensions.ext_database import db, async_db
from agent_platform_basic.libs.infinite_scroll_pagination import InfiniteScrollPagination
from agent_platform_basic.models.db_model import Account
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.llm_generator.llm_generator import LLMGenerator
from agent_platform_core.models.db_model.model import App, Conversation, EndUser, Message


class ConversationService:
    @classmethod
    def pagination_by_last_id(cls, app_model: App, user: Optional[Union[Account, EndUser]],
                              last_id: Optional[str], limit: int,
                              invoke_from: InvokeFrom,
                              include_ids: Optional[list] = None,
                              exclude_ids: Optional[list] = None,
                              name: Optional[str] = None) -> InfiniteScrollPagination:
        if not user:
            return InfiniteScrollPagination(data=[], limit=limit, has_more=False)

        base_query = db.session.query(Conversation).filter(
            Conversation.is_deleted == False,
            Conversation.app_id == app_model.id,
            Conversation.from_source == ('api' if isinstance(user, EndUser) else 'console'),
            Conversation.from_end_user_id == (user.id if isinstance(user, EndUser) else None),
            Conversation.from_account_id == (user.id if isinstance(user, Account) else None),
            or_(Conversation.invoke_from.is_(None), Conversation.invoke_from == invoke_from.value),
            Conversation.name.ilike(f'%{name}%') if name else True
        )

        if include_ids is not None:
            base_query = base_query.filter(Conversation.id.in_(include_ids))

        if exclude_ids is not None:
            base_query = base_query.filter(~Conversation.id.in_(exclude_ids))

        if last_id:
            last_conversation = base_query.filter(
                Conversation.id == last_id,
            ).first()

            if not last_conversation:
                raise LastConversationNotExistsError()

            conversations = base_query.filter(
                Conversation.created_at < last_conversation.created_at,
                Conversation.id != last_conversation.id
            ).order_by(Conversation.created_at.desc()).limit(limit).all()
        else:
            conversations = base_query.order_by(Conversation.created_at.desc()).limit(limit).all()

        has_more = False
        if len(conversations) == limit:
            current_page_first_conversation = conversations[-1]
            rest_count = base_query.filter(
                Conversation.created_at < current_page_first_conversation.created_at,
                Conversation.id != current_page_first_conversation.id
            ).count()

            if rest_count > 0:
                has_more = True

        return InfiniteScrollPagination(
            data=conversations,
            limit=limit,
            has_more=has_more
        )

    @classmethod
    def rename(cls, app_model: App, conversation_id: str,
               user: Optional[Union[Account, EndUser]], name: str, auto_generate: bool):
        # conversation = cls.get_conversation(app_model, conversation_id, user)
        conversation = cls.get_conversation_rename(app_model, conversation_id, user)

        if auto_generate:
            return cls.auto_generate_name(app_model, conversation)
        else:
            conversation.name = name
            db.session.commit()

        return conversation

    @classmethod
    def auto_generate_name(cls, app_model: App, conversation: Conversation):
        # get conversation first message
        message = db.session.query(Message) \
            .filter(
            Message.app_id == app_model.id,
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.asc()).first()

        if not message:
            raise MessageNotExistsError()

        # generate conversation name
        try:
            name = LLMGenerator.generate_conversation_name(
                app_model.tenant_id, message.query, conversation.id, app_model.id
            )
            conversation.name = name
        except:
            pass

        db.session.commit()

        return conversation

    @classmethod
    def get_conversation_rename(cls, app_model: App, conversation_id: str, user: Optional[Union[Account, EndUser]]):
        conversation = db.session.query(Conversation) \
            .filter(
            Conversation.id == conversation_id,
            Conversation.app_id == app_model.id,
            Conversation.from_source == ('api' if isinstance(user, EndUser) else 'console'),
            Conversation.from_end_user_id == (user.id if isinstance(user, EndUser) else None),
            Conversation.from_account_id == (user.id if isinstance(user, Account) else None),
            Conversation.is_deleted == False
        ).first()

        if not conversation:
            raise ConversationNotExistsError()

        return conversation

    @classmethod
    async def get_conversation(cls, app_model: App, conversation_id: str, user: Optional[Union[Account, EndUser]]):
        conversation = db.session.query(Conversation) \
            .filter(
            Conversation.id == conversation_id,
            Conversation.app_id == app_model.id,
            Conversation.from_source == ('api' if isinstance(user, EndUser) else 'console'),
            Conversation.from_end_user_id == (user.id if isinstance(user, EndUser) else None),
            Conversation.from_account_id == (user.id if isinstance(user, Account) else None),
            Conversation.is_deleted == False
        ).first()

        if not conversation:
            raise ConversationNotExistsError()

        return conversation

    @classmethod
    def delete(cls, app_model: App, conversation_id: str, user: Optional[Union[Account, EndUser]]):
        conversation = cls.get_conversation_rename(app_model, conversation_id, user)

        conversation.is_deleted = True
        db.session.commit()
