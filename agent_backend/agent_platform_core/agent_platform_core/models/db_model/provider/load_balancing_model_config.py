from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
""" 
@Date    ：2024/7/14 23:02 
@Version: 1.0
@Description:

"""

class LoadBalancingModelConfig(db.Model):
    """
    Configurations for load balancing models.
    """
    __tablename__ = 'load_balancing_model_configs'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='load_balancing_model_config_pkey'),
        db.Index('load_balancing_model_config_tenant_provider_model_idx', 'tenant_id', 'provider_name', 'model_type'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    provider_name = db.Column(db.String(255), nullable=False)
    model_name = db.Column(db.String(255), nullable=False)
    model_type = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    encrypted_config = db.Column(db.Text, nullable=True)
    enabled = db.Column(db.Boolean, nullable=False, server_default=db.text('true'))
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
