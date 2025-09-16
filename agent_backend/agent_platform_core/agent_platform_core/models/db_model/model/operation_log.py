from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
"""
@Date    ：2024/7/15 9:24 
@Version: 1.0
@Description:

"""
class OperationLog(db.Model):
    __tablename__ = 'operation_logs'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='operation_log_pkey'),
        db.Index('operation_log_account_action_idx', 'tenant_id', 'account_id', 'action')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    account_id = db.Column(StringUUID, nullable=False)
    action = db.Column(db.String(255), nullable=False)
    content = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    created_ip = db.Column(db.String(255), nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
