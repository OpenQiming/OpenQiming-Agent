from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/14 22:47 
@Version: 1.0
@Description:

"""

class TenantPreferredModelProvider(db.Model):
    __tablename__ = 'tenant_preferred_model_providers'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='tenant_preferred_model_provider_pkey'),
        db.Index('tenant_preferred_model_provider_tenant_provider_idx', 'tenant_id', 'provider_name'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    provider_name = db.Column(db.String(255), nullable=False)
    preferred_provider_type = db.Column(db.String(40), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
