from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Index, UniqueConstraint, Boolean
from agent_platform_basic.extensions.ext_database import Base
from .string_uuid import StringUUID


class TenantAccountJoin(Base):
    __tablename__ = 'tenant_account_joins'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tenant_account_join_pkey'),
        Index('tenant_account_join_account_id_idx', 'account_id'),
        Index('tenant_account_join_tenant_id_idx', 'tenant_id'),
        UniqueConstraint('tenant_id', 'account_id', name='unique_tenant_account_join')
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    tenant_id = Column(StringUUID, nullable=False)
    account_id = Column(StringUUID, nullable=False)
    current = Column(Boolean, nullable=False, server_default=text('false'))
    role = Column(String(16), nullable=False, server_default='normal')
    invited_by = Column(StringUUID, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
