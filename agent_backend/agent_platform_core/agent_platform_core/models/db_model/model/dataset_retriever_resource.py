from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import StringUUID

"""
@Date    ：2024/7/15 9:31 
@Version: 1.0
@Description:

"""


class DatasetRetrieverResource(db.Model):
    __tablename__ = 'dataset_retriever_resources'
    __table_args__ = (
        db.PrimaryKeyConstraint('id', name='dataset_retriever_resource_pkey'),
        db.Index('dataset_retriever_resource_message_id_idx', 'message_id'),
    )

    id = db.Column(StringUUID, nullable=False, server_default=db.text('uuid_generate_v4()'))
    message_id = db.Column(StringUUID, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    dataset_id = db.Column(StringUUID, nullable=False)
    dataset_name = db.Column(db.Text, nullable=False)
    document_id = db.Column(StringUUID, nullable=False)
    document_name = db.Column(db.Text, nullable=False)
    data_source_type = db.Column(db.Text, nullable=False)
    segment_id = db.Column(StringUUID, nullable=False)
    score = db.Column(db.Float, nullable=True)
    content = db.Column(db.Text, nullable=False)
    hit_count = db.Column(db.Integer, nullable=True)
    word_count = db.Column(db.Integer, nullable=True)
    segment_position = db.Column(db.Integer, nullable=True)
    index_node_hash = db.Column(db.Text, nullable=True)
    retriever_from = db.Column(db.Text, nullable=False)
    created_by = db.Column(StringUUID, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.current_timestamp())
