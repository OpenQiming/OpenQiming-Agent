from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.libs.helper import generate_string
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:27 
@Version: 1.0
@Description:

"""


class ApiToken(db.Model):
    __tablename__ = 'api_tokens'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='api_token_pkey'),
        db.Index('api_token_app_id_type_idx', 'app_id', 'type'),
        db.Index('api_token_token_idx', 'token', 'type'),
        db.Index('api_token_tenant_idx', 'tenant_id', 'type')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    app_id = db.Column(StringUUID, nullable=True)
    tenant_id = db.Column(StringUUID, nullable=True)
    type = db.Column(db.String(16), nullable=False)
    token = db.Column(db.String(255), nullable=False)
    last_used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @staticmethod
    def generate_api_key(prefix, n):
        while True:
            result = prefix + generate_string(n)
            while db.session.query(ApiToken).filter(ApiToken.token == result).count() > 0:
                result = prefix + generate_string(n)

            return result
