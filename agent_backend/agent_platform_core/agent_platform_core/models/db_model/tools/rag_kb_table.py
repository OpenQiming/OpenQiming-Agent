import json
from datetime import datetime

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

class RagKbTableProvider(db.Model):
    """
    This table stores the knowledge base (KB) information for each tenant.
    """
    __tablename__ = 'kb_table'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='kb_table_pkey'),
        # one tenant can only have one knowledge base with the same name
        db.UniqueConstraint('tenant_id', 'kb_name', name='unique_kb_table_provider')
    )

    # id of the knowledge base
    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    # id of the tenant
    tenant_id = db.Column(db.String(255), nullable=False)
    # id of the knowledge base
    kb_id = db.Column(db.String(255), nullable=False)
    # name of the knowledge base
    kb_name = db.Column(db.String(255), nullable=False)
    # description of the knowledge base
    kb_desc = db.Column(db.Text, nullable=True)
    # who created this knowledge base
    creator = db.Column(db.String(255), nullable=False)
    # creation time of the knowledge base
    creation_time = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    # last update time of the knowledge base
    update_time = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    kb_icon = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<RagKbTableProvider(id={self.id}, tenant_id={self.tenant_id}, kb_name={self.kb_name})>"