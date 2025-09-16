import json

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""

@Date    ：2024/7/15 8:51 
@Version: 1.0
@Description:

"""


class BuiltinToolProvider(db.Model):
    """
    This table stores the tool provider information for built-in tools for each tenant.
    """
    __tablename__ = 'tool_builtin_providers'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='tool_builtin_provider_pkey'),
        # one tenant can only have one tool provider with the same name
        db.UniqueConstraint('tenant_id', 'provider', name='unique_builtin_tool_provider')
    )

    # id of the tool provider
    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    # id of the tenant
    tenant_id = db.Column(StringUUID, nullable=True)
    # who created this tool provider
    user_id = db.Column(StringUUID, nullable=False)
    # name of the tool provider
    provider = db.Column(db.String(40), nullable=False)
    # credential of the tool provider
    encrypted_credentials = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @property
    def credentials(self) -> dict:
        return json.loads(self.encrypted_credentials)
