from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
"""
@Date    ：2024/7/14 22:06 
@Version: 1.0
@Description:

"""

class ProviderModelSetting(db.Model):
    """
    Provider model settings for record the model enabled status and load balancing status.
    """
    __tablename__ = 'provider_model_settings'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='provider_model_setting_pkey'),
        db.Index('provider_model_setting_tenant_provider_model_idx', 'tenant_id', 'provider_name', 'model_type'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    provider_name = db.Column(db.String(255), nullable=False)
    model_name = db.Column(db.String(255), nullable=False)
    model_type = db.Column(db.String(40), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, server_default=db.text('true'))
    load_balancing_enabled = db.Column(db.Boolean, nullable=False, server_default=db.text('false'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
