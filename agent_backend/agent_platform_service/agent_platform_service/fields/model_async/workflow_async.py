from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from agent_platform_basic.models.db_model import Account
from agent_platform_basic.libs import DbUtils


class WorkflowAsync:
    def __init__(self, session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

    async def async_tool_published(self,
                                   app_id: str) -> bool:
        from agent_platform_core.models.db_model.tools import WorkflowToolProvider
        result = await self.session.execute(
            select(WorkflowToolProvider).filter(WorkflowToolProvider.app_id == app_id)
        )
        result = result.scalar_one_or_none()
        return result is not None

    async def updated_by_account(self,
                                 updated_by: str):
        execute = await self.session.execute(
            select(Account).filter(Account.id == updated_by)
        )
        account = execute.scalar_one() if updated_by else None
        return account

    async def created_by_account(self,
                                 created_by: str):
        execute = await self.session.execute(
            select(Account).filter(Account.id == created_by)
        )
        account = execute.scalar_one() if created_by else None
        return account
