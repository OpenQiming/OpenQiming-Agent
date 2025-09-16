from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID, Account

"""
@Date    ：2024/7/15 9:19 
@Version: 1.0
@Description:

"""


class MessageAnnotation(db.Model):
    __tablename__ = 'message_annotations'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='message_annotation_pkey'),
        db.Index('message_annotation_app_idx', 'app_id'),
        db.Index('message_annotation_conversation_idx', 'conversation_id'),
        db.Index('message_annotation_message_idx', 'message_id')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    app_id = db.Column(StringUUID, nullable=False)
    conversation_id = db.Column(StringUUID, db.ForeignKey('conversations.id'), nullable=True)
    message_id = db.Column(StringUUID, nullable=True)
    question = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=False)
    hit_count = db.Column(db.Integer, nullable=False, server_default=db.text('0'))
    account_id = db.Column(StringUUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @property
    def account(self):
        account = db.session.query(Account).filter(Account.id == self.account_id).first()
        return account

    @property
    def annotation_create_account(self):
        account = db.session.query(Account).filter(Account.id == self.account_id).first()
        return account
