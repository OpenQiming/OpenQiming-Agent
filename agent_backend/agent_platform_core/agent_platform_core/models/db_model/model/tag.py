from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/14 23:51 
@Version: 1.0
@Description:

"""


class Tag(db.Model):
    __tablename__ = 'tags'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='tag_pkey'),
        db.Index('tag_type_idx', 'type'),
        db.Index('tag_name_idx', 'name'),
    )

    TAG_TYPE_LIST = ['knowledge', 'app']

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    tenant_id = db.Column(StringUUID, nullable=True)
    type = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    created_by = db.Column(StringUUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
