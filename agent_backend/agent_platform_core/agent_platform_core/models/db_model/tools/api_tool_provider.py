import json

from sqlalchemy.orm import Mapped, mapped_column

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID, Account, Tenant
from agent_platform_core.tools.entities.tool_bundle import ApiToolBundle
from agent_platform_core.tools.entities.tool_entities import ApiProviderSchemaType

"""
@Date    ：2024/7/15 8:56 
@Version: 1.0
@Description:

"""


class ApiToolProvider(db.Model):
    """
    The table stores the api providers.
    """

    __tablename__ = "tool_api_providers"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="tool_api_provider_pkey"),
        db.UniqueConstraint("name", "tenant_id", name="unique_api_tool_provider"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    # name of the api provider
    name = db.Column(db.String(40), nullable=False)
    # icon
    icon = db.Column(db.String(255), nullable=False)
    # original schema
    schema = db.Column(db.Text, nullable=False)
    schema_type_str: Mapped[str] = db.Column(db.String(40), nullable=False)
    # who created this tool
    user_id = db.Column(StringUUID, nullable=False)
    # tenant id
    tenant_id = db.Column(StringUUID, nullable=False)
    # description of the provider
    description = db.Column(db.Text, nullable=False)
    # json format tools
    tools_str = db.Column(db.Text, nullable=False)
    # json format credentials
    credentials_str = db.Column(db.Text, nullable=False)
    # privacy policy
    privacy_policy = db.Column(db.String(255), nullable=True)
    # custom_disclaimer
    custom_disclaimer: Mapped[str] = mapped_column(db.TEXT, default="")
    # access type
    access_type = db.Column(db.Integer, nullable=True, server_default=db.text('1'))
    # version
    version = db.Column(db.String(255), nullable=False)
    # status
    status = db.Column(db.String(255), nullable=False)
    # header_image
    header_image = db.Column(db.Text)

    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP(0)"))

    @property
    def schema_type(self) -> ApiProviderSchemaType:
        return ApiProviderSchemaType.value_of(self.schema_type_str)

    @property
    def tools(self) -> list[ApiToolBundle]:
        return [ApiToolBundle(**tool) for tool in json.loads(self.tools_str)]

    @property
    def credentials(self) -> dict:
        return json.loads(self.credentials_str)

    @property
    def user(self) -> Account | None:
        return db.session.query(Account).filter(Account.id == self.user_id).first()

    @property
    def tenant(self) -> Tenant | None:
        return db.session.query(Tenant).filter(Tenant.id == self.tenant_id).first()
