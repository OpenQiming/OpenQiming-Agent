import json

from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Index, Text, Boolean

from agent_platform_basic.extensions.ext_database import Base
from .string_uuid import StringUUID


class DataSourceApiKeyAuthBinding(Base):
    __tablename__ = 'data_source_api_key_auth_bindings'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='data_source_api_key_auth_binding_pkey'),
        Index('data_source_api_key_auth_binding_tenant_id_idx', 'tenant_id'),
        Index('data_source_api_key_auth_binding_provider_idx', 'provider'),
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    tenant_id = Column(StringUUID, nullable=False)
    category = Column(String(255), nullable=False)
    provider = Column(String(255), nullable=False)
    credentials = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    disabled = Column(Boolean, nullable=True, server_default=text('false'))

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': self.tenant_id,
            'category': self.category,
            'provider': self.provider,
            'credentials': json.loads(self.credentials),
            'created_at': self.created_at.timestamp(),
            'updated_at': self.updated_at.timestamp(),
            'disabled': self.disabled
        }
