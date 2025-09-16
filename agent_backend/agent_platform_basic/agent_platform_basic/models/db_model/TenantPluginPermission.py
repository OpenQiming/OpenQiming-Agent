from sqlalchemy import Column, String, DateTime, text, PrimaryKeyConstraint, Index, UniqueConstraint, Boolean
from agent_platform_basic.extensions.ext_database import Base, db
from .string_uuid import StringUUID
import enum
from sqlalchemy.orm import Mapped, mapped_column, reconstructor

class TenantPluginPermission(Base):
    class InstallPermission(enum.StrEnum):
        EVERYONE = "everyone"
        ADMINS = "admins"
        NOBODY = "noone"

    class DebugPermission(enum.StrEnum):
        EVERYONE = "everyone"
        ADMINS = "admins"
        NOBODY = "noone"

    __tablename__ = "account_plugin_permissions"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="account_plugin_permission_pkey"),
        db.UniqueConstraint("tenant_id", name="unique_tenant_plugin"),
    )

    id: Mapped[str] = mapped_column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    tenant_id: Mapped[str] = mapped_column(StringUUID, nullable=False)
    install_permission: Mapped[InstallPermission] = mapped_column(
        db.String(16), nullable=False, server_default="everyone"
    )
    debug_permission: Mapped[DebugPermission] = mapped_column(db.String(16), nullable=False, server_default="noone")
