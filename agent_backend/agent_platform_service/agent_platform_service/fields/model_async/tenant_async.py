from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform_basic.libs import DbUtils
from agent_platform_basic.models.db_model import TenantAccountJoin, Account
from agent_platform_basic.models.enum_model.tenant import TenantAccountRole
from agent_platform_service.fastapi_fields.resp.console.tenant_account import TenantAccountResp


class TenantAsync:
    def __init__(self, session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

    async def async_get_tenant_member(self, tenant_id: str):
        results = await self.session.execute(select(TenantAccountJoin).filter(TenantAccountJoin.tenant_id == tenant_id,
                                                                         TenantAccountJoin.role != TenantAccountRole.OWNER))
        results = results.scalars().all()
        # 查询用户
        accounts = await self.session.execute(select(Account).filter(Account.id.in_([result.account_id for result in results])))
        accounts = accounts.scalars().all()
        accountsRsp = []
        for account in accounts:
            result = next((r for r in results if r.account_id == account.id), None)
            account = TenantAccountResp(account_id = account.id, role = result.role, name = account.name, employee_number = account.employee_number)
            accountsRsp.append(account)
        return accountsRsp

