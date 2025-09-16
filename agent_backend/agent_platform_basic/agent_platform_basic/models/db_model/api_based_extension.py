from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Index, Text

from agent_platform_basic.extensions.ext_database import Base
from .string_uuid import StringUUID

""" 

@Date    ：2024/7/9 12:09 
@Version: 1.0
@Description:

"""


class APIBasedExtension(Base):
    __tablename__ = 'api_based_extensions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='api_based_extension_pkey'),
        Index('api_based_extension_tenant_idx', 'tenant_id'),
    )

    id = Column(StringUUID, server_default=text('uuid_generate_v4()'))
    tenant_id = Column(StringUUID, nullable=False)
    name = Column(String(255), nullable=False)
    api_endpoint = Column(String(255), nullable=False)
    api_key = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
