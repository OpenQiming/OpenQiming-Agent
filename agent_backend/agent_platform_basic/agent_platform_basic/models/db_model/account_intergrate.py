from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, UniqueConstraint
from agent_platform_basic.extensions.ext_database import Base
from .string_uuid import StringUUID


class AccountIntegrate(Base):
    __tablename__ = 'account_integrates'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='account_integrate_pkey'),
        UniqueConstraint('account_id', 'provider', name='unique_account_provider'),
        UniqueConstraint('provider', 'open_id', name='unique_provider_open_id')
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    account_id = Column(StringUUID, nullable=False)
    provider = Column(String(16), nullable=False)
    open_id = Column(String(255), nullable=False)
    encrypted_token = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
