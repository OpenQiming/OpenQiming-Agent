from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:29 
@Version: 1.0
@Description:

"""


class ApiRequest(db.Model):
    __tablename__ = 'api_requests'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='api_request_pkey'),
        db.Index('api_request_token_idx', 'tenant_id', 'api_token_id')
    )

    id = db.Column(StringUUID, nullable=False, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    api_token_id = db.Column(StringUUID, nullable=False)
    path = db.Column(db.String(255), nullable=False)
    request = db.Column(db.Text, nullable=True)
    response = db.Column(db.Text, nullable=True)
    ip = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
