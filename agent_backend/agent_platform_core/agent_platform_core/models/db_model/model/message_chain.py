from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:29 
@Version: 1.0
@Description:

"""


class MessageChain(db.Model):
    __tablename__ = 'message_chains'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='message_chain_pkey'),
        db.Index('message_chain_message_id_idx', 'message_id')
    )

    id = db.Column(StringUUID, nullable=False, server_default=db.text('uuid_generate_v4()'))
    message_id = db.Column(StringUUID, nullable=False)
    type = db.Column(db.String(255), nullable=False)
    input = db.Column(db.Text, nullable=True)
    output = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
