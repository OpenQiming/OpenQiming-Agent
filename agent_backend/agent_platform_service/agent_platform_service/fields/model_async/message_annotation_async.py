"""

@Date    ：2024/9/13 17:10 
@Version: 1.0
@Description:

"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from agent_platform_basic.libs import DbUtils
from agent_platform_basic.models.db_model import Account


class MessageAnnotationAsync:
    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

    async def async_get_account(self, account_id):
        account_scalar = await self.session.execute(select(Account).filter(Account.id == account_id))
        return account_scalar.scalar_one_or_none()

    async def async_annotation_create_account(self, account_id):
        account_scalar = await self.session.execute(select(Account).filter(Account.id == account_id))
        return account_scalar.scalar_one_or_none()
