from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

""" 
@Date    ：2024/7/14 22:09 
@Version: 1.0
@Description:

"""

class TenantDefaultModel(db.Model):
    __tablename__ = 'tenant_default_models'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='tenant_default_model_pkey'),
        db.Index('tenant_default_model_tenant_id_provider_type_idx', 'tenant_id', 'provider_name', 'model_type'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    provider_name = db.Column(db.String(255), nullable=False)
    model_name = db.Column(db.String(255), nullable=False)
    model_type = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
