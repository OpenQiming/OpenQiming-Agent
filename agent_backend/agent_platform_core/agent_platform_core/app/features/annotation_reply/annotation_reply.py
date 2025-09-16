import logging
import uuid
from typing import Optional

from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom
from agent_platform_core.rag.datasource.vdb.vector_factory import Vector
from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.models.db_model.dataset import Dataset, DatasetCollectionBinding
from agent_platform_core.models.db_model.model import App, AppAnnotationSetting, Message, MessageAnnotation, \
    AppAnnotationHitHistory

logger = logging.getLogger(__name__)


def add_annotation_history(annotation_id: str, app_id: str, annotation_question: str,
                           annotation_content: str, query: str, user_id: str,
                           message_id: str, from_source: str, score: float):
    # add hit count to annotation
    db.session.query(MessageAnnotation).filter(
        MessageAnnotation.id == annotation_id
    ).update(
        {MessageAnnotation.hit_count: MessageAnnotation.hit_count + 1},
        synchronize_session=False
    )

    annotation_hit_history = AppAnnotationHitHistory(
        annotation_id=annotation_id,
        app_id=app_id,
        account_id=user_id,
        question=query,
        source=from_source,
        score=score,
        message_id=message_id,
        annotation_question=annotation_question,
        annotation_content=annotation_content
    )
    db.session.add(annotation_hit_history)
    db.session.commit()


def get_dataset_collection_binding(
    provider_name: str, model_name: str, collection_type: str = "dataset"
) -> DatasetCollectionBinding:
    dataset_collection_binding = (
        db.session.query(DatasetCollectionBinding)
        .filter(
            DatasetCollectionBinding.provider_name == provider_name,
            DatasetCollectionBinding.model_name == model_name,
            DatasetCollectionBinding.type == collection_type,
        )
        .order_by(DatasetCollectionBinding.created_at)
        .first()
    )

    if not dataset_collection_binding:
        dataset_collection_binding = DatasetCollectionBinding(
            provider_name=provider_name,
            model_name=model_name,
            collection_name=Dataset.gen_collection_name_by_id(str(uuid.uuid4())),
            type=collection_type,
        )
        db.session.add(dataset_collection_binding)
        db.session.commit()
    return dataset_collection_binding


class AnnotationReplyFeature:
    def query(
        self, app_record: App, message: Message, query: str, user_id: str, invoke_from: InvokeFrom
    ) -> Optional[MessageAnnotation]:
        """
        Query app annotations to reply
        :param app_record: app record
        :param message: message
        :param query: query
        :param user_id: user id
        :param invoke_from: invoke from
        :return:
        """
        annotation_setting = (
            db.session.query(AppAnnotationSetting).filter(AppAnnotationSetting.app_id == app_record.id).first()
        )

        if not annotation_setting:
            return None

        collection_binding_detail = annotation_setting.collection_binding_detail

        try:
            score_threshold = annotation_setting.score_threshold or 1
            embedding_provider_name = collection_binding_detail.provider_name
            embedding_model_name = collection_binding_detail.model_name

            dataset_collection_binding = get_dataset_collection_binding(
                embedding_provider_name, embedding_model_name, "annotation"
            )

            dataset = Dataset(
                id=app_record.id,
                tenant_id=app_record.tenant_id,
                indexing_technique="high_quality",
                embedding_model_provider=embedding_provider_name,
                embedding_model=embedding_model_name,
                collection_binding_id=dataset_collection_binding.id,
            )

            vector = Vector(dataset, attributes=["doc_id", "annotation_id", "app_id"])

            documents = vector.search_by_vector(
                query=query, top_k=1, score_threshold=score_threshold, filter={"group_id": [dataset.id]}
            )

            if documents:
                annotation_id = documents[0].metadata["annotation_id"]
                score = documents[0].metadata["score"]
                annotation = db.session.query(MessageAnnotation).filter(MessageAnnotation.id == annotation_id).first()
                if annotation:
                    if invoke_from in {InvokeFrom.SERVICE_API, InvokeFrom.WEB_APP}:
                        from_source = "api"
                    else:
                        from_source = "console"

                    # insert annotation history
                    add_annotation_history(
                        annotation.id,
                        app_record.id,
                        annotation.question,
                        annotation.content,
                        query,
                        user_id,
                        message.id,
                        from_source,
                        score,
                    )

                    return annotation
        except Exception as e:
            logger.warning(f"Query annotation failed, exception: {str(e)}.")
            return None

        return None
