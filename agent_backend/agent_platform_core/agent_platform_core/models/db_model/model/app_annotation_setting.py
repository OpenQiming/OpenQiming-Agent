from sqlalchemy import Float

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID, Account

""" 
@Date    ：2024/7/14 23:56 
@Version: 1.0
@Description:

"""


class AppAnnotationSetting(db.Model):
    __tablename__ = 'app_annotation_settings'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='app_annotation_settings_pkey'),
        db.Index('app_annotation_settings_app_idx', 'app_id')
    )

    id = db.Column(StringUUID, server_default=db.text('uuid_generate_v4()'))
    app_id = db.Column(StringUUID, nullable=False)
    score_threshold = db.Column(Float, nullable=False, server_default=db.text('0'))
    collection_binding_id = db.Column(StringUUID, nullable=False)
    created_user_id = db.Column(StringUUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))
    updated_user_id = db.Column(StringUUID, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.text('CURRENT_TIMESTAMP(0)'))

    @property
    def created_account(self):
        account = (db.session.query(Account)
                   .join(AppAnnotationSetting, AppAnnotationSetting.created_user_id == Account.id)
                   .filter(AppAnnotationSetting.id == self.annotation_id).first())
        return account

    @property
    def updated_account(self):
        account = (db.session.query(Account)
                   .join(AppAnnotationSetting, AppAnnotationSetting.updated_user_id == Account.id)
                   .filter(AppAnnotationSetting.id == self.annotation_id).first())
        return account

    @property
    def collection_binding_detail(self):
        from agent_platform_core.models.db_model.dataset import DatasetCollectionBinding
        collection_binding_detail = (db.session.query(DatasetCollectionBinding)
                                     .filter(DatasetCollectionBinding.id == self.collection_binding_id).first())
        return collection_binding_detail
