from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
""" 
@Date    ：2024/7/14 22:03 
@Version: 1.0
@Description:

"""

class ProviderModel(db.Model):
    """
    Provider model representing the API provider_models and their configurations.
    """
    __tablename__ = 'provider_models'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='provider_model_pkey'),
        db.Index('provider_model_tenant_id_provider_idx', 'tenant_id', 'provider_name'),
        db.UniqueConstraint('tenant_id', 'provider_name', 'model_name', 'model_type', name='unique_provider_model_name')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    provider_name = db.Column(db.String(255), nullable=False)
    model_name = db.Column(db.String(255), nullable=False)
    model_type = db.Column(db.String(40), nullable=False)
    encrypted_config = db.Column(db.Text, nullable=True)
    is_valid = db.Column(db.Boolean, nullable=False, server_default=db.text('false'))
    employee_number = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
