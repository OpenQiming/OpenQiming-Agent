import json

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID, Account, Tenant
from agent_platform_core.models.db_model.model import App
from agent_platform_core.tools.entities.tool_entities import ApiProviderSchemaType, WorkflowToolParameterConfiguration

"""
@Date    ：2024/7/15 8:59 
@Version: 1.0
@Description:

"""


class WorkflowToolProvider(db.Model):
    """
    The table stores the workflow providers.
    """
    __tablename__ = 'tool_workflow_providers'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='tool_workflow_provider_pkey'),
        db.UniqueConstraint('name', 'tenant_id', name='unique_workflow_tool_provider'),
        db.UniqueConstraint('tenant_id', 'app_id', name='unique_workflow_tool_provider_app_id'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    # name of the workflow provider
    name = db.Column(db.String(40), nullable=False)
    # label of the workflow provider
    label = db.Column(db.String(255), nullable=False, server_default='')
    # icon
    icon = db.Column(db.String(255), nullable=False)
    # app id of the workflow provider
    app_id = db.Column(StringUUID, nullable=False)
    # workflow id of the workflow provider
    workflow_id = db.Column(StringUUID, nullable=False)
    # version of the workflow provider
    version = db.Column(db.String(255), nullable=False, server_default='')
    # who created this tool
    user_id = db.Column(StringUUID, nullable=False)
    # tenant id
    tenant_id = db.Column(StringUUID, nullable=False)
    # description of the provider
    description = db.Column(db.Text, nullable=False)
    # parameter configuration
    parameter_configuration = db.Column(db.Text, nullable=False, server_default='[]')
    # privacy policy
    privacy_policy = db.Column(db.String(255), nullable=True, server_default='')

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    code_content = db.Column(db.Text, nullable=True)

    @property
    def schema_type(self) -> ApiProviderSchemaType:
        return ApiProviderSchemaType.value_of(self.schema_type_str)

    @property
    def user(self) -> Account:
        return db.session.query(Account).filter(Account.id == self.user_id).first()

    @property
    def tenant(self) -> Tenant:
        return db.session.query(Tenant).filter(Tenant.id == self.tenant_id).first()

    @property
    def parameter_configurations(self) -> list[WorkflowToolParameterConfiguration]:
        return [
            WorkflowToolParameterConfiguration(**config)
            for config in json.loads(self.parameter_configuration)
        ]

    @property
    def app(self) -> App:
        return db.session.query(App).filter(App.id == self.app_id).first()
