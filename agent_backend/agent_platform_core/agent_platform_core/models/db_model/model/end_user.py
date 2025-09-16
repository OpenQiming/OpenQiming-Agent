from flask_login import UserMixin

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:26 
@Version: 1.0
@Description:

"""


class EndUser(UserMixin, db.Model):
    __tablename__ = 'end_users'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='end_user_pkey'),
        db.Index('end_user_session_id_idx', 'session_id', 'type'),
        db.Index('end_user_tenant_session_id_idx', 'tenant_id', 'session_id', 'type'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    app_id = db.Column(StringUUID, nullable=True)
    type = db.Column(db.String(255), nullable=False)
    external_user_id = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255))
    is_anonymous = db.Column(db.Boolean, nullable=False, server_default=db.text('true'))
    session_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
