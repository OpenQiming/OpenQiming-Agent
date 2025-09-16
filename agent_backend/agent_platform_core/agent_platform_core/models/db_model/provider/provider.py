from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
from agent_platform_core.models.enum_model.provider import ProviderType
""" 
@Date    ：2024/7/14 21:52 
@Version: 1.0
@Description:

"""
class Provider(db.Model):
    """
    Provider model representing the API providers and their configurations.
    """
    __tablename__ = 'providers'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='provider_pkey'),
        db.Index('provider_tenant_id_provider_idx', 'tenant_id', 'provider_name'),
        db.UniqueConstraint('tenant_id', 'provider_name', 'provider_type', 'quota_type', name='unique_provider_name_type_quota')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    provider_name = db.Column(db.String(255), nullable=False)
    provider_type = db.Column(db.String(40), nullable=False, server_default=db.text("'custom'::character varying"))
    encrypted_config = db.Column(db.Text, nullable=True)
    is_valid = db.Column(db.Boolean, nullable=False, server_default=db.text('false'))
    last_used = db.Column(db.DateTime, nullable=True)

    quota_type = db.Column(db.String(40), nullable=True, server_default=db.text("''::character varying"))
    quota_limit = db.Column(db.BigInteger, nullable=True)
    quota_used = db.Column(db.BigInteger, default=0)

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    def __repr__(self):
        return f"<Provider(id={self.id}, tenant_id={self.tenant_id}, provider_name='{self.provider_name}', provider_type='{self.provider_type}')>"

    @property
    def token_is_set(self):
        """
         Returns True if the encrypted_config is not None, indicating that the token is set.
         """
        return self.encrypted_config is not None

    @property
    def is_enabled(self):
        """
        Returns True if the provider is enabled.
        """
        if self.provider_type == ProviderType.SYSTEM.value:
            return self.is_valid
        else:
            return self.is_valid and self.token_is_set





