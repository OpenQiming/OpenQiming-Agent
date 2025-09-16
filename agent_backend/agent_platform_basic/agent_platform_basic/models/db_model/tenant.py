import json

from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Text
from agent_platform_basic.extensions.ext_database import Base
from .string_uuid import StringUUID

"""
@Date    ：2024/7/13 10:26 
@Version: 1.0
@Description:
    租户相关实体
"""


class Tenant(Base):
    __tablename__ = 'tenants'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='tenant_pkey'),
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    name = Column(String(255), nullable=False)
    encrypt_public_key = Column(Text)
    plan = Column(String(255), nullable=False, server_default=text("'basic'::character varying"))
    status = Column(String(255), nullable=False, server_default=text("'normal'::character varying"))
    custom_config = Column(Text)
    tenant_desc = Column(Text)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    updated_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    province = Column(String(100))

    @property
    def custom_config_dict(self) -> dict:
        return json.loads(self.custom_config) if self.custom_config else {}

    @custom_config_dict.setter
    def custom_config_dict(self, value: dict):
        self.custom_config = json.dumps(value, ensure_ascii=False)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
        }
        