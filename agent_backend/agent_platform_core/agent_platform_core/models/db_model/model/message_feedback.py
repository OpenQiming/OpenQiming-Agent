from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID, Account

"""
@Date    ：2024/7/15 9:15 
@Version: 1.0
@Description:

"""


class MessageFeedback(db.Model):
    __tablename__ = 'message_feedbacks'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='message_feedback_pkey'),
        db.Index('message_feedback_app_idx', 'app_id'),
        db.Index('message_feedback_message_idx', 'message_id', 'from_source'),
        db.Index('message_feedback_conversation_idx', 'conversation_id', 'from_source', 'rating')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    app_id = db.Column(StringUUID, nullable=False)
    conversation_id = db.Column(StringUUID, nullable=False)
    message_id = db.Column(StringUUID, nullable=False)
    rating = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    from_source = db.Column(db.String(255), nullable=False)
    from_end_user_id = db.Column(StringUUID)
    from_account_id = db.Column(StringUUID)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @property
    def from_account(self):
        account = db.session.query(Account).filter(Account.id == self.from_account_id).first()
        return account
