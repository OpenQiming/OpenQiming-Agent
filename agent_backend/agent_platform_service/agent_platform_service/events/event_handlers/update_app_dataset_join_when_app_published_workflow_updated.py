from typing import cast

from sqlalchemy import select, delete

from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.models.db_model.dataset import AppDatasetJoin
from agent_platform_core.models.db_model.workflow import Workflow
from agent_platform_core.workflow.nodes import NodeType
# from agent_platform_core.workflow.nodes.knowledge_retrieval.entities import KnowledgeRetrievalNodeData
from agent_platform_service.events.app_event import app_published_workflow_was_updated


@app_published_workflow_was_updated.connect
async def handle(sender, **kwargs):
    app = sender
    published_workflow = kwargs.get('published_workflow')
    session = kwargs.get('session')
    published_workflow = cast(Workflow, published_workflow)
    dataset_ids = get_dataset_ids_from_workflow(published_workflow)

    app_dataset_join_scalar = await session.execute(select(AppDatasetJoin).filter(AppDatasetJoin.app_id == app.id))
    app_dataset_joins = app_dataset_join_scalar.scalars().all()

    removed_dataset_ids = []
    if not app_dataset_joins:
        added_dataset_ids = dataset_ids
    else:
        old_dataset_ids = set()
        for app_dataset_join in app_dataset_joins:
            old_dataset_ids.add(app_dataset_join.dataset_id)

        added_dataset_ids = dataset_ids - old_dataset_ids
        removed_dataset_ids = old_dataset_ids - dataset_ids

    if removed_dataset_ids:
        for dataset_id in removed_dataset_ids:
            await session.execute(
                delete(AppDatasetJoin).where(AppDatasetJoin.app_id == app.id, AppDatasetJoin.dataset_id == dataset_id))

    if added_dataset_ids:
        for dataset_id in added_dataset_ids:
            app_dataset_join = AppDatasetJoin(
                app_id=app.id,
                dataset_id=dataset_id
            )
            session.add(app_dataset_join)

    await session.commit()


def get_dataset_ids_from_workflow(published_workflow: Workflow) -> set:
    dataset_ids = set()
    graph = published_workflow.graph_dict
    if not graph:
        return dataset_ids

    nodes = graph.get('nodes', [])

    # fetch all knowledge retrieval nodes
    knowledge_retrieval_nodes = [node for node in nodes
                                 if node.get('data', {}).get('type') == NodeType.KNOWLEDGE_RETRIEVAL.value]

    if not knowledge_retrieval_nodes:
        return dataset_ids

    # for node in knowledge_retrieval_nodes:
    #     try:
    #         node_data = KnowledgeRetrievalNodeData(**node.get('data', {}))
    #         dataset_ids.update(node_data.dataset_ids)
    #     except Exception as e:
    #         continue

    return dataset_ids
