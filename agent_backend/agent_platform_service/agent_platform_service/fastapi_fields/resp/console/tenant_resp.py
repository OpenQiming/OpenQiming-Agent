from typing import Optional, List

from pydantic import BaseModel

from agent_platform_basic.models.db_model import Tenant
from agent_platform_service.fastapi_fields.resp.console.tenant_account import TenantAccountResp
from agent_platform_service.fields.model_async.config.handle_extra_fields import create_instance
from agent_platform_service.fields.model_async.tenant_async import TenantAsync


class TenantResp(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    accounts: Optional[List[TenantAccountResp]] = None

    @classmethod
    async def from_tenant(cls, tenant: Tenant, session):
        if tenant is None:
            return None
        return cls(id=tenant.id, name=tenant.name, description=tenant.tenant_desc,
                   accounts=await create_instance(TenantAsync, 'async_get_tenant_member',
                                                  method_args={'tenant_id': tenant.id}, session=session))