from typing import Optional

from sqlalchemy.orm import mapped_column, Mapped

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:02 
@Version: 1.0
@Description:

"""


class ToolFile(db.Model):
    __tablename__ = "tool_files"
    __table_args__ = (
        db.PrimaryKeyConstraint("id", name="tool_file_pkey"),
        db.Index("tool_file_conversation_id_idx", "conversation_id"),
    )

    id = db.Column(StringUUID, server_default=db.text("uuid_generate_v4()"))
    user_id: Mapped[str] = db.Column(StringUUID, nullable=False)
    tenant_id: Mapped[str] = db.Column(StringUUID, nullable=False)
    conversation_id: Mapped[Optional[str]] = db.Column(StringUUID, nullable=True)
    file_key: Mapped[str] = db.Column(db.String(255), nullable=False)
    mimetype: Mapped[str] = db.Column(db.String(255), nullable=False)
    original_url: Mapped[Optional[str]] = db.Column(db.String(2048), nullable=True)
    name: Mapped[str] = mapped_column(default="")
    size: Mapped[int] = mapped_column(default=-1)

    def __init__(
        self,
        *,
        user_id: str,
        tenant_id: str,
        conversation_id: Optional[str] = None,
        file_key: str,
        mimetype: str,
        original_url: Optional[str] = None,
        name: str,
        size: int,
    ):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.conversation_id = conversation_id
        self.file_key = file_key
        self.mimetype = mimetype
        self.original_url = original_url
        self.name = name
        self.size = size
