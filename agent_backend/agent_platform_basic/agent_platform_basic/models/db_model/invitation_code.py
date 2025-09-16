from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Index, Integer

from agent_platform_basic.extensions.ext_database import Base
from .string_uuid import StringUUID

""" 
@Date    ：2024/7/13 10:39 
@Version: 1.0
@Description:

"""


class InvitationCode(Base):
    __tablename__ = 'invitation_codes'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='invitation_code_pkey'),
        Index('invitation_codes_batch_idx', 'batch'),
        Index('invitation_codes_code_idx', 'code', 'status')
    )

    id = Column(Integer, nullable=False)
    batch = Column(String(255), nullable=False)
    code = Column(String(32), nullable=False)
    status = Column(String(16), nullable=False, server_default=text("'unused'::character varying"))
    used_at = Column(DateTime)
    used_by_tenant_id = Column(StringUUID)
    used_by_account_id = Column(StringUUID)
    deprecated_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
