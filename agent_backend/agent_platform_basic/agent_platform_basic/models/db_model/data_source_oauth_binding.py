from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Index, Boolean

from agent_platform_basic.extensions.ext_database import Base
from .string_uuid import StringUUID


class DataSourceOauthBinding(Base):
    __tablename__ = 'data_source_oauth_bindings'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='source_binding_pkey'),
        Index('source_binding_tenant_id_idx', 'tenant_id'),
        Index('source_info_idx', "source_info", postgresql_using='gin')
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    tenant_id = Column(StringUUID, nullable=False)
    access_token = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    source_info = Column(JSONB, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    disabled = Column(Boolean, nullable=True, server_default=text('false'))
