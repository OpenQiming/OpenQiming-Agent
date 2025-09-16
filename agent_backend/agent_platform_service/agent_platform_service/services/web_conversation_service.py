from typing import Optional, Union

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.libs.infinite_scroll_pagination import InfiniteScrollPagination
from agent_platform_basic.models.db_model import Account
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.models.db_model.model import App, EndUser
from agent_platform_service.models.db_model.web import PinnedConversation
from agent_platform_service.services.conversation_service import ConversationService


class WebConversationService:
    @classmethod
    def pagination_by_last_id(cls, app_model: App, user: Optional[Union[Account, EndUser]],
                              last_id: Optional[str], limit: int, invoke_from: InvokeFrom,
                              pinned: Optional[bool] = None, name: Optional[str] = None) -> InfiniteScrollPagination:
        include_ids = None
        exclude_ids = None
        if pinned is not None:
            pinned_conversations = db.session.query(PinnedConversation).filter(
                PinnedConversation.app_id == app_model.id,
                PinnedConversation.created_by_role == ('account' if isinstance(user, Account) else 'end_user'),
                PinnedConversation.created_by == user.id
            ).order_by(PinnedConversation.created_at.desc()).all()
            pinned_conversation_ids = [pc.conversation_id for pc in pinned_conversations]
            if pinned:
                include_ids = pinned_conversation_ids
            else:
                exclude_ids = pinned_conversation_ids

        return ConversationService.pagination_by_last_id(
            app_model=app_model,
            user=user,
            last_id=last_id,
            limit=limit,
            invoke_from=invoke_from,
            include_ids=include_ids,
            exclude_ids=exclude_ids,
            name=name,
        )

    @classmethod
    def pin(cls, app_model: App, conversation_id: str, user: Optional[Union[Account, EndUser]]):
        pinned_conversation = db.session.query(PinnedConversation).filter(
            PinnedConversation.app_id == app_model.id,
            PinnedConversation.conversation_id == conversation_id,
            PinnedConversation.created_by_role == ('account' if isinstance(user, Account) else 'end_user'),
            PinnedConversation.created_by == user.id
        ).first()

        if pinned_conversation:
            return

        # conversation = ConversationService.get_conversation(
        #     app_model=app_model,
        #     conversation_id=conversation_id,
        #     user=user
        # )

        conversation = ConversationService.get_conversation_rename(
            app_model=app_model,
            conversation_id=conversation_id,
            user=user
        )

        pinned_conversation = PinnedConversation(
            app_id=app_model.id,
            conversation_id=conversation.id,
            created_by_role='account' if isinstance(user, Account) else 'end_user',
            created_by=user.id
        )

        db.session.add(pinned_conversation)
        db.session.commit()

    @classmethod
    def unpin(cls, app_model: App, conversation_id: str, user: Optional[Union[Account, EndUser]]):
        pinned_conversation = db.session.query(PinnedConversation).filter(
            PinnedConversation.app_id == app_model.id,
            PinnedConversation.conversation_id == conversation_id,
            PinnedConversation.created_by_role == ('account' if isinstance(user, Account) else 'end_user'),
            PinnedConversation.created_by == user.id
        ).first()

        if not pinned_conversation:
            return

        db.session.delete(pinned_conversation)
        db.session.commit()
