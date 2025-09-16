from enum import StrEnum
from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.models.enum_model.base import Base
from sqlalchemy import Float, Index, PrimaryKeyConstraint, func, text

"""
@Date    ：2024/7/12 15:29 
@Version: 1.0
@Description:
    应用相关枚举
"""


class AppMode(StrEnum):
    COMPLETION = "completion"
    WORKFLOW = "workflow"
    CHAT = "chat"
    ADVANCED_CHAT = "advanced-chat"
    AGENT_CHAT = "agent-chat"
    CHANNEL = "channel"
    METABOLIC = "metabolic"
    TOOL = "tool"
    BIGMODEL = "bigmodel"

    @classmethod
    def value_of(cls, value: str) -> "AppMode":
        """
        Get value of given mode.

        :param value: mode value
        :return: mode
        """
        for mode in cls:
            if mode.value == value:
                return mode
        raise ValueError(f"invalid mode value {value}")

class DifySetup(Base):
    __tablename__ = "dify_setups"
    __table_args__ = (db.PrimaryKeyConstraint("version", name="dify_setup_pkey"),)

    version = db.Column(db.String(255), nullable=False)
    setup_at = db.Column(db.DateTime, nullable=False, server_default=func.current_timestamp())