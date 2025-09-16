from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:18 
@Version: 1.0
@Description:

"""


class MessageFile(db.Model):
    __tablename__ = 'message_files'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='message_file_pkey'),
        db.Index('message_file_message_idx', 'message_id'),
        db.Index('message_file_created_by_idx', 'created_by')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    message_id = db.Column(StringUUID, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    transfer_method = db.Column(db.String(255), nullable=False)
    url = db.Column(db.Text, nullable=True)
    belongs_to = db.Column(db.String(255), nullable=True)
    upload_file_id = db.Column(StringUUID, nullable=True)
    created_by_role = db.Column(db.String(255), nullable=False)
    created_by = db.Column(StringUUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
