from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID
from sqlalchemy.orm import Mapped, mapped_column
import sqlalchemy as sa
from agent_platform_core.models.enum_model.enums import UserFrom
from agent_platform_core.models.enum_model.enums import CreatedByRole
from datetime import datetime
"""
@Date    ：2024/7/14 23:41 
@Version: 1.0
@Description:

"""


class UploadFile(db.Model):
    __tablename__ = 'upload_files'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='upload_file_pkey'),
        db.Index('upload_file_tenant_idx', 'tenant_id')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=False)
    storage_type = db.Column(db.String(255), nullable=False)
    key = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    extension = db.Column(db.String(255), nullable=False)
    mime_type = db.Column(db.String(255), nullable=True)
    created_by_role = db.Column(db.String(255), nullable=False, server_default=db.text("'account'::character varying"))
    created_by = db.Column(StringUUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    used = db.Column(db.Boolean, nullable=False, server_default=db.text('false'))
    used_by = db.Column(StringUUID, nullable=True)
    used_at = db.Column(db.DateTime, nullable=True)
    hash = db.Column(db.String(255), nullable=True)
    source_url = db.Column(db.Text, nullable=True, default="")

    def __init__(
            self,
            *,
            tenant_id: str,
            storage_type: str,
            key: str,
            name: str,
            size: int,
            extension: str,
            mime_type: str,
            created_by_role: CreatedByRole,
            created_by: str,
            created_at: datetime,
            used: bool,
            used_by: str | None = None,
            used_at: datetime | None = None,
            hash: str | None = None,
            source_url: str = "",
    ):
        self.tenant_id = tenant_id
        self.storage_type = storage_type
        self.key = key
        self.name = name
        self.size = size
        self.extension = extension
        self.mime_type = mime_type
        if isinstance(created_by_role, str):
            self.created_by_role = created_by_role
        else:
            self.created_by_role = created_by_role.value
        self.created_by = created_by
        self.created_at = created_at
        self.used = used
        self.used_by = used_by
        self.used_at = used_at
        self.hash = hash
        self.source_url = source_url
