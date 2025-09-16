import json
import re

from agent_platform_basic.extensions.ext_database import db, Base
from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Index, Text, Boolean, Integer, \
    UniqueConstraint
from sqlalchemy.orm import Mapped
from agent_platform_basic.models.db_model import StringUUID


class Apps_accounts_operation(Base):
    __tablename__ = 'apps_accounts_operation'
    __table_args__ = (
        UniqueConstraint(
            'app_id', 'tenant_id', 'account_id',
            name='uq_app_tenant_account_name'
        ),
    )

    id = Column(StringUUID, primary_key=True, server_default=text('uuid_generate_v4()'))  # 独立主键
    app_id = Column(StringUUID, nullable=False)  # 外键关联app表，非主
    tenant_id: Mapped[str] = Column(StringUUID, nullable=False)
    name = Column(String(255), nullable=False)
    account_id = Column(StringUUID, nullable=True)
    is_like = Column(Boolean, nullable=True, server_default=text("false"))
    is_subscription = Column(Boolean, nullable=True, server_default=text("false"))
    create_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
    update_time = Column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP(0)'))
