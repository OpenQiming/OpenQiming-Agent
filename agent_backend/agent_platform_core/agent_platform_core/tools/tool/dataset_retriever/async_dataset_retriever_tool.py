from typing import Optional

from sqlalchemy import select

from agent_platform_core.rag.entities.citation_metadata import RetrievalSourceMetadata

from agent_platform_core.rag.entities.context_entities import DocumentContext
from agent_platform_core.models.db_model.dataset import Document as DatasetDocument
from agent_platform_core.app.app_config.entities import DatasetRetrieveConfigEntity
from pydantic import BaseModel, Field

from agent_platform_basic.extensions.ext_database import async_db
from agent_platform_core.models.db_model.dataset import Dataset
from agent_platform_core.rag.datasource.retrieval_service import RetrievalService
from agent_platform_core.rag.retrieval.retrival_methods import RetrievalMethod
from agent_platform_core.tools.tool.dataset_retriever.async_dataset_retriever_base_tool import \
    AsyncDatasetRetrieverBaseTool

default_retrieval_model = {
    'search_method': RetrievalMethod.SEMANTIC_SEARCH,
    'reranking_enable': False,
    'reranking_model': {
        'reranking_provider_name': '',
        'reranking_model_name': ''
    },
    'top_k': 2,
    'score_threshold_enabled': False
}


class DatasetRetrieverToolInput(BaseModel):
    query: str = Field(..., description="Query for the dataset to be used to retrieve the dataset.")


class AsyncDatasetRetrieverTool(AsyncDatasetRetrieverBaseTool):
    """Tool for querying a Dataset."""
    name: str = "dataset"
    args_schema: type[BaseModel] = DatasetRetrieverToolInput
    description: str = "use this to retrieve a dataset. "
    dataset_id: str
    user_id: Optional[str] = None
    retrieve_config: DatasetRetrieveConfigEntity
    inputs: dict


    @classmethod
    def from_dataset(cls, dataset: Dataset, **kwargs):
        description = dataset.description
        if not description:
            description = 'useful for when you want to answer queries about the ' + dataset.name

        description = description.replace('\n', '').replace('\r', '')
        return cls(
            name=f"dataset_{dataset.id.replace('-', '_')}",
            tenant_id=dataset.tenant_id,
            dataset_id=dataset.id,
            description=description,
            **kwargs
        )

    async def _async_run(self, query: str) -> str:
        print("_async_run___query:::", query)
        async with async_db.AsyncSessionLocal() as session:
            stmt = select(Dataset).filter(
                Dataset.tenant_id == self.tenant_id,
                Dataset.id == self.dataset_id
            )
            result = await session.execute(stmt)
            dataset = result.scalars().first()

        if not dataset:
            return ''

        for hit_callback in self.hit_callbacks:
            await hit_callback.on_query(query, dataset.id)

        # get retrieval model , if the model is not setting , using default
        retrieval_model = dataset.retrieval_model if dataset.retrieval_model else default_retrieval_model

        retrieval_resource_list = []
        if dataset.indexing_technique == "economy":
            # use keyword table query
            documents = await RetrievalService.async_retrieve(retrival_method='keyword_search',
                                                  dataset_id=dataset.id,
                                                  query=query,
                                                  top_k=self.top_k,
                                                  )
            return str("\n".join([document.page_content for document in documents]))
        else:
            if self.top_k > 0:
                # retrieval source
                documents = await RetrievalService.async_retrieve(
                                      retrival_method=retrieval_model.get("search_method", "semantic_search"),
                                      dataset_id=dataset.id,
                                      query=query,
                                      top_k=self.top_k,
                                      score_threshold=retrieval_model.get("score_threshold", 0.0)
                                      if retrieval_model['score_threshold_enabled'] else 0.0,
                                      reranking_model=retrieval_model['reranking_model']
                                      if retrieval_model['reranking_enable'] else None,
                                      weights=retrieval_model.get("weights"),
                                      )
            else:
                documents = []

            for hit_callback in self.hit_callbacks:
                await hit_callback.on_tool_end(documents)
            document_score_list = {}
            if dataset.indexing_technique != "economy":
                for item in documents:
                    if item.metadata.get('score'):
                        document_score_list[item.metadata['doc_id']] = item.metadata['score']
            document_context_list = []
            print("documents:::documents", documents)
            records = await RetrievalService.async_format_retrieval_documents(documents)
            print("records:::records", records)
            if records:
                for record in records:
                    segment = record.segment
                    if segment.answer:
                        document_context_list.append(
                            DocumentContext(
                                content=f"question:{segment.get_sign_content()} answer:{segment.answer}",
                                score=record.score,
                            )
                        )
                    else:
                        document_context_list.append(
                            DocumentContext(
                                content=segment.get_sign_content(),
                                score=record.score,
                            )
                        )
                if self.return_resource:
                    async with async_db.AsyncSessionLocal() as session:
                        for record in records:
                            segment = record.segment
                            dataset_stmt = select(Dataset).filter_by(id=segment.dataset_id)
                            dataset_result = await session.execute(dataset_stmt)
                            dataset = dataset_result.scalars().first()

                            # 异步查询 DatasetDocument
                            document_stmt = select(DatasetDocument).filter(
                                DatasetDocument.id == segment.document_id,
                                DatasetDocument.enabled == True,
                                DatasetDocument.archived == False
                            )
                            document_result = await session.execute(document_stmt)
                            document = document_result.scalars().first()
                            print("document:::", document)
                            if dataset and document:
                                # source = RetrievalSourceMetadata(
                                #     dataset_id=dataset.id,
                                #     dataset_name=dataset.name,
                                #     document_id=document.id,  # type: ignore
                                #     document_name=document.name,  # type: ignore
                                #     data_source_type=document.data_source_type,  # type: ignore
                                #     segment_id=segment.id,
                                #     retriever_from=self.retriever_from,
                                #     score=record.score or 0.0,
                                #     doc_metadata=document.doc_metadata,  # type: ignore
                                # )
                                source = {
                                    "dataset_id": dataset.id,
                                    "dataset_name": dataset.name,
                                    "document_id": document.id,
                                    'document_name': document.name,
                                    'data_source_type': document.data_source_type,
                                    'segment_id': segment.id,
                                    'retriever_from': self.retriever_from,
                                    'score': document_score_list.get(segment.index_node_id, None),
                                    'doc_metadata': document.doc_metadata,
                                }

                                if self.retriever_from == "dev":
                                    source['hit_count'] = segment.hit_count
                                    source['word_count'] = segment.word_count
                                    source['segment_position'] = segment.position
                                    source['index_node_hash'] = segment.index_node_hash
                                if segment.answer:
                                    source['content'] = f'question:{segment.content} \nanswer:{segment.answer}'
                                else:
                                    source['content'] = segment.content
                                retrieval_resource_list.append(source)

            if self.return_resource and retrieval_resource_list:
                retrieval_resource_list = sorted(
                    retrieval_resource_list,
                    key=lambda x: x.get('score') or 0.0,
                    reverse=True,
                )
                for position, item in enumerate(retrieval_resource_list, start=1):  # type: ignore
                    item["position"] = position  # type: ignore
                for hit_callback in self.hit_callbacks:
                    await hit_callback.return_retriever_resource_info(retrieval_resource_list)
            if document_context_list:
                print("document_context_list::::", document_context_list)
                document_context_list = sorted(document_context_list, key=lambda x: x.score or 0.0, reverse=True)
                return str("\n".join([document_context.content for document_context in document_context_list]))
            return ""