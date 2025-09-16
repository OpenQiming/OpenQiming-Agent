from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform_core.models.db_model.model import App


class ConversationAsync:
    def __init__(self,
                 session: AsyncSession):
        self.session = session

    async def get_app(self, app_id: str):
        results = await self.session.execute(select(App).filter(App.id == app_id))
        return results.scalar_one_or_none()