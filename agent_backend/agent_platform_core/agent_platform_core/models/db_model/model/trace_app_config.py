import json

from sqlalchemy import func

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:32 
@Version: 1.0
@Description:

"""


class TraceAppConfig(db.Model):
    __tablename__ = 'trace_app_config'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='tracing_app_config_pkey'),
        db.Index('tracing_app_config_app_id_idx', 'app_id'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    app_id = db.Column(StringUUID, nullable=False)
    tracing_provider = db.Column(db.String(255), nullable=True)
    tracing_config = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    is_active = db.Column(db.Boolean, nullable=False, server_default=db.text('true'))

    @property
    def tracing_config_dict(self):
        return self.tracing_config if self.tracing_config else {}

    @property
    def tracing_config_str(self):
        return json.dumps(self.tracing_config_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'app_id': self.app_id,
            'tracing_provider': self.tracing_provider,
            'tracing_config': self.tracing_config_dict,
            "is_active": self.is_active,
            "created_at": self.created_at.__str__() if self.created_at else None,
            'updated_at': self.updated_at.__str__() if self.updated_at else None,
        }
