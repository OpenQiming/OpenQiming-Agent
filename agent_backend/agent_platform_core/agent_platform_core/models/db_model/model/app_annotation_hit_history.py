from sqlalchemy import Float

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID, Account
from .message_annotation import MessageAnnotation

"""
@Date    ：2024/7/15 9:22 
@Version: 1.0
@Description:

"""


class AppAnnotationHitHistory(db.Model):
    __tablename__ = 'app_annotation_hit_histories'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='app_annotation_hit_histories_pkey'),
        db.Index('app_annotation_hit_histories_app_idx', 'app_id'),
        db.Index('app_annotation_hit_histories_account_idx', 'account_id'),
        db.Index('app_annotation_hit_histories_annotation_idx', 'annotation_id'),
        db.Index('app_annotation_hit_histories_message_idx', 'message_id'),
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    app_id = db.Column(StringUUID, nullable=False)
    annotation_id = db.Column(StringUUID, nullable=False)
    source = db.Column(db.Text, nullable=False)
    question = db.Column(db.Text, nullable=False)
    account_id = db.Column(StringUUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    score = db.Column(Float, nullable=False, server_default=db.text('0'))
    message_id = db.Column(StringUUID, nullable=False)
    annotation_question = db.Column(db.Text, nullable=False)
    annotation_content = db.Column(db.Text, nullable=False)

    @property
    def account(self):
        account = (db.session.query(Account)
                   .join(MessageAnnotation, MessageAnnotation.account_id == Account.id)
                   .filter(MessageAnnotation.id == self.annotation_id).first())
        return account

    @property
    def annotation_create_account(self):
        account = db.session.query(Account).filter(Account.id == self.account_id).first()
        return account
