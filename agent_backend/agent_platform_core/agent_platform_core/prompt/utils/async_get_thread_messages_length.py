from sqlalchemy import select

from .extract_thread_messages import extract_thread_messages
from agent_platform_basic.extensions.ext_database import async_db
from agent_platform_core.models.db_model.model import Message


async def get_thread_messages_length(conversation_id: str) -> int:
    """
    Get the number of thread messages based on the parent message id.
    """
    # Fetch all messages related to the conversation
    async with async_db.AsyncSessionLocal() as session:
        query = await session.execute(select(
                Message
            )
            .filter(
                Message.conversation_id == conversation_id,
            )
            .order_by(Message.created_at.desc()))

    messages = query.scalars().all()

    # Extract thread messages
    thread_messages = extract_thread_messages(messages)

    # Exclude the newly created message with an empty answer
    if thread_messages and not thread_messages[0].answer:
        thread_messages.pop(0)

    return len(thread_messages)
