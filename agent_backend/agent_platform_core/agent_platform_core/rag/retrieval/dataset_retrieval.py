import asyncio
import logging
import math
from collections import Counter
from typing import Optional, cast, Any

from sqlalchemy import select

from agent_platform_core.callback_handler.async_index_tool_callback_handler import AsyncDatasetIndexToolCallbackHandler
from agent_platform_core.rag.datasource.keyword.jieba.jieba_keyword_table_handler import JiebaKeywordTableHandler

from agent_platform_core.rag.data_post_processor.data_post_processor import DataPostProcessor

from agent_platform_core.rag.entities.metadata_entities import MetadataCondition

from agent_platform_core.async_model_manager import AsyncModelManager, AsyncModelInstance

from agent_platform_basic.extensions.ext_database import db, async_db
from agent_platform_core.app.app_config.entities import DatasetEntity, DatasetRetrieveConfigEntity
from agent_platform_core.app.entities.app_invoke_entities import InvokeFrom, ModelConfigWithCredentialsEntity
from agent_platform_core.callback_handler.index_tool_callback_handler import DatasetIndexToolCallbackHandler
from agent_platform_core.entities.agent_entities import PlanningStrategy
from agent_platform_core.memory.token_buffer_memory import TokenBufferMemory
# from agent_platform_core.model_manager import ModelInstance, ModelManager
from agent_platform_core.model_runtime.entities.message_entities import PromptMessageTool
from agent_platform_core.model_runtime.entities.model_entities import ModelFeature, ModelType
from agent_platform_core.model_runtime.model_providers.__base.large_language_model import LargeLanguageModel
from agent_platform_core.models.db_model.dataset import Dataset, DatasetQuery, DocumentSegment
from agent_platform_core.models.db_model.dataset import Document as DatasetDocument
from agent_platform_core.ops.ops_trace_manager import TraceQueueManager, TraceTask, TraceTaskName
from agent_platform_core.ops.utils import measure_time
from agent_platform_core.rag.datasource.retrieval_service import RetrievalService
from agent_platform_core.rag.models.document import Document
from agent_platform_core.rag.rerank.rerank_type import RerankMode
from agent_platform_core.rag.retrieval.retrival_methods import RetrievalMethod
from agent_platform_core.rag.retrieval.router.multi_dataset_function_call_router import FunctionCallMultiDatasetRouter
from agent_platform_core.rag.retrieval.router.multi_dataset_react_route import ReactMultiDatasetRouter
from agent_platform_core.tools.tool.dataset_retriever.async_dataset_retriever_base_tool import \
    AsyncDatasetRetrieverBaseTool
from agent_platform_core.tools.tool.dataset_retriever.async_dataset_retriever_tool import AsyncDatasetRetrieverTool
from agent_platform_core.tools.tool.dataset_retriever.dataset_multi_retriever_tool import DatasetMultiRetrieverTool
from agent_platform_core.tools.tool.dataset_retriever.dataset_retriever_base_tool import DatasetRetrieverBaseTool
from agent_platform_core.tools.tool.dataset_retriever.dataset_retriever_tool import DatasetRetrieverTool

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


class DatasetRetrieval:
    def __init__(self, application_generate_entity=None):
        self.application_generate_entity = application_generate_entity

    async def retrieve(
            self, app_id: str, user_id: str, tenant_id: str,
            model_config: ModelConfigWithCredentialsEntity,
            config: DatasetEntity,
            query: str,
            invoke_from: InvokeFrom,
            show_retrieve_source: bool,
            hit_callback: DatasetIndexToolCallbackHandler,
            message_id: str,
            memory: Optional[TokenBufferMemory] = None,
    ) -> Optional[str]:
        """
        Retrieve dataset.
        :param app_id: app_id
        :param user_id: user_id
        :param tenant_id: tenant id
        :param model_config: model config
        :param config: dataset config
        :param query: query
        :param invoke_from: invoke from
        :param show_retrieve_source: show retrieve source
        :param hit_callback: hit callback
        :param message_id: message id
        :param memory: memory
        :return:
        """
        dataset_ids = config.dataset_ids
        if len(dataset_ids) == 0:
            return None
        retrieve_config = config.retrieve_config

        # check model is support tool calling
        model_type_instance = model_config.provider_model_bundle.model_type_instance
        model_type_instance = cast(LargeLanguageModel, model_type_instance)

        model_manager = AsyncModelManager()
        model_instance = await model_manager.get_model_instance(
            tenant_id=tenant_id,
            model_type=ModelType.LLM,
            provider=model_config.provider,
            model=model_config.model
        )

        # get model schema
        model_schema = model_type_instance.get_model_schema(
            model=model_config.model,
            credentials=model_config.credentials
        )

        if not model_schema:
            return None

        planning_strategy = PlanningStrategy.REACT_ROUTER
        features = model_schema.features
        if features:
            if ModelFeature.TOOL_CALL in features \
                    or ModelFeature.MULTI_TOOL_CALL in features:
                planning_strategy = PlanningStrategy.ROUTER
        available_datasets = []
        for dataset_id in dataset_ids:
            # get dataset from dataset id
            dataset = db.session.query(Dataset).filter(
                Dataset.tenant_id == tenant_id,
                Dataset.id == dataset_id
            ).first()

            # pass if dataset is not available
            if not dataset:
                continue

            # pass if dataset is not available
            if (dataset and dataset.available_document_count == 0
                    and dataset.available_document_count == 0):
                continue

            available_datasets.append(dataset)
        all_documents = []
        user_from = 'account' if invoke_from in [InvokeFrom.EXPLORE, InvokeFrom.DEBUGGER] else 'end_user'
        if retrieve_config.retrieve_strategy == DatasetRetrieveConfigEntity.RetrieveStrategy.SINGLE:
            all_documents = await self.single_retrieve(
                app_id, tenant_id, user_id, user_from, available_datasets, query,
                model_instance,
                model_config, planning_strategy, message_id
            )
        elif retrieve_config.retrieve_strategy == DatasetRetrieveConfigEntity.RetrieveStrategy.MULTIPLE:
            all_documents = await self.multiple_retrieve(
                app_id, tenant_id, user_id, user_from,
                available_datasets, query, retrieve_config.top_k,
                retrieve_config.score_threshold,
                retrieve_config.reranking_model.get('reranking_provider_name'),
                retrieve_config.reranking_model.get('reranking_model_name'),
                message_id,
            )

        document_score_list = {}
        for item in all_documents:
            if item.metadata.get('score'):
                document_score_list[item.metadata['doc_id']] = item.metadata['score']

        document_context_list = []
        index_node_ids = [document.metadata['doc_id'] for document in all_documents]
        segments = DocumentSegment.query.filter(
            DocumentSegment.dataset_id.in_(dataset_ids),
            DocumentSegment.completed_at.isnot(None),
            DocumentSegment.status == 'completed',
            DocumentSegment.enabled == True,
            DocumentSegment.index_node_id.in_(index_node_ids)
        ).all()

        if segments:
            index_node_id_to_position = {id: position for position, id in enumerate(index_node_ids)}
            sorted_segments = sorted(segments,
                                     key=lambda segment: index_node_id_to_position.get(segment.index_node_id,
                                                                                       float('inf')))
            for segment in sorted_segments:
                if segment.answer:
                    document_context_list.append(f'question:{segment.get_sign_content()} answer:{segment.answer}')
                else:
                    document_context_list.append(segment.get_sign_content())
            if show_retrieve_source:
                context_list = []
                resource_number = 1
                for segment in sorted_segments:
                    dataset = Dataset.query.filter_by(
                        id=segment.dataset_id
                    ).first()
                    document = DatasetDocument.query.filter(DatasetDocument.id == segment.document_id,
                                                            DatasetDocument.enabled == True,
                                                            DatasetDocument.archived == False,
                                                            ).first()
                    if dataset and document:
                        source = {
                            'position': resource_number,
                            'dataset_id': dataset.id,
                            'dataset_name': dataset.name,
                            'document_id': document.id,
                            'document_name': document.name,
                            'data_source_type': document.data_source_type,
                            'segment_id': segment.id,
                            'retriever_from': invoke_from.to_source(),
                            'score': document_score_list.get(segment.index_node_id, None)
                        }

                        if invoke_from.to_source() == 'dev':
                            source['hit_count'] = segment.hit_count
                            source['word_count'] = segment.word_count
                            source['segment_position'] = segment.position
                            source['index_node_hash'] = segment.index_node_hash
                        if segment.answer:
                            source['content'] = f'question:{segment.content} \nanswer:{segment.answer}'
                        else:
                            source['content'] = segment.content
                        context_list.append(source)
                    resource_number += 1
                if hit_callback:
                    hit_callback.return_retriever_resource_info(context_list)

            return str("\n".join(document_context_list))
        return ''

    async def single_retrieve(
            self, app_id: str,
            tenant_id: str,
            user_id: str,
            user_from: str,
            available_datasets: list,
            query: str,
            model_instance: AsyncModelInstance,
            model_config: ModelConfigWithCredentialsEntity,
            planning_strategy: PlanningStrategy,
            message_id: Optional[str] = None,
    ):
        tools = []
        for dataset in available_datasets:
            description = dataset.description
            if not description:
                description = 'useful for when you want to answer queries about the ' + dataset.name

            description = description.replace('\n', '').replace('\r', '')
            message_tool = PromptMessageTool(
                name=dataset.id,
                description=description,
                parameters={
                    "type": "object",
                    "properties": {},
                    "required": [],
                }
            )
            tools.append(message_tool)
        dataset_id = None
        if planning_strategy == PlanningStrategy.REACT_ROUTER:
            react_multi_dataset_router = ReactMultiDatasetRouter()
            dataset_id = await react_multi_dataset_router.invoke(query, tools, model_config, model_instance,
                                                           user_id, tenant_id)

        elif planning_strategy == PlanningStrategy.ROUTER:
            function_call_router = FunctionCallMultiDatasetRouter()
            dataset_id = await function_call_router.invoke(query, tools, model_config, model_instance)

        if dataset_id:
            async with async_db.AsyncSessionLocal() as session:
            # get retrieval model config
                result = await session.execute(
                    select(Dataset).filter(Dataset.id == dataset_id)
                )
                dataset = result.scalars().first()
            if dataset:
                retrieval_model_config = dataset.retrieval_model \
                    if dataset.retrieval_model else default_retrieval_model

                # get top k
                top_k = retrieval_model_config['top_k']
                # get retrieval method
                if dataset.indexing_technique == "economy":
                    retrival_method = 'keyword_search'
                else:
                    retrival_method = retrieval_model_config['search_method']
                # get reranking model
                reranking_model = retrieval_model_config['reranking_model'] \
                    if retrieval_model_config['reranking_enable'] else None
                # get score threshold
                score_threshold = .0
                score_threshold_enabled = retrieval_model_config.get("score_threshold_enabled")
                if score_threshold_enabled:
                    score_threshold = retrieval_model_config.get("score_threshold")

                with measure_time() as timer:
                    results = await RetrievalService.async_retrieve(
                        retrival_method=retrival_method, dataset_id=dataset.id,
                        query=query,
                        top_k=top_k, score_threshold=score_threshold,
                        reranking_model=reranking_model
                    )
                await self._on_query(query, [dataset_id], app_id, user_from, user_id)

                if results:
                    await self._on_retrival_end(results, message_id, timer)

                return results
        return []

    async def multiple_retrieve(
            self,
            app_id: str,
            tenant_id: str,
            user_id: str,
            user_from: str,
            available_datasets: list,
            query: str,
            top_k: int,
            score_threshold: float,
            reranking_mode: str,
            reranking_model: Optional[dict] = None,
            weights: Optional[dict[str, Any]] = None,
            reranking_enable: bool = True,
            message_id: Optional[str] = None,
            metadata_filter_document_ids: Optional[dict[str, list[str]]] = None,
            metadata_condition: Optional[MetadataCondition] = None,
    ):
        if not available_datasets:
            return []

        all_documents = []
        dataset_ids = [dataset.id for dataset in available_datasets]
        index_type_check = all(
            item.indexing_technique == available_datasets[0].indexing_technique for item in available_datasets
        )
        if not index_type_check and (not reranking_enable or reranking_mode != RerankMode.RERANKING_MODEL):
            raise ValueError(
                "The configured knowledge base list have different indexing technique, please set reranking model."
            )
        index_type = available_datasets[0].indexing_technique

        logging.info(f"index_type::: {index_type}")
        if index_type == "high_quality":
            embedding_model_check = all(
                item.embedding_model == available_datasets[0].embedding_model for item in available_datasets
            )
            embedding_model_provider_check = all(
                item.embedding_model_provider == available_datasets[0].embedding_model_provider
                for item in available_datasets
            )
            if (
                    reranking_enable
                    and reranking_mode == "weighted_score"
                    and (not embedding_model_check or not embedding_model_provider_check)
            ):
                raise ValueError(
                    "The configured knowledge base list have different embedding model, please set reranking model."
                )
            if reranking_enable and reranking_mode == RerankMode.WEIGHTED_SCORE:
                if weights is not None:
                    weights["vector_setting"]["embedding_provider_name"] = available_datasets[
                        0
                    ].embedding_model_provider
                    weights["vector_setting"]["embedding_model_name"] = available_datasets[0].embedding_model
        retrieval_tasks = []

        for dataset in available_datasets:
            index_type = dataset.indexing_technique
            document_ids_filter = None

            if dataset.provider != "external":
                if metadata_condition and not metadata_filter_document_ids:
                    continue
                if metadata_filter_document_ids:
                    document_ids = metadata_filter_document_ids.get(dataset.id, [])
                    if document_ids:
                        document_ids_filter = document_ids
                    else:
                        continue

            logging.info(f"=====create_task===== {all_documents}")
            # 创建异步任务
            task = asyncio.create_task(
                self._retriever(
                    dataset_id=dataset.id,
                    query=query,
                    top_k=top_k,
                    all_documents=all_documents,
                    # document_ids_filter=document_ids_filter,
                    # metadata_condition=metadata_condition,
                )
            )
            retrieval_tasks.append(task)

        # 等待所有任务完成
        retrieval_results = await asyncio.gather(*retrieval_tasks, return_exceptions=True)

        with measure_time() as timer:
            if reranking_enable:
                # do rerank for searched documents
                data_post_processor = DataPostProcessor(tenant_id, reranking_mode, reranking_model, weights, False)

                all_documents = data_post_processor.invoke(
                    query=query, documents=all_documents, score_threshold=score_threshold, top_n=top_k
                )
            else:
                print("index_type:::", index_type, all_documents)
                if index_type == "economy":
                    all_documents = self.calculate_keyword_score(query, all_documents, top_k)
                elif index_type == "high_quality":
                    all_documents = self.calculate_vector_score(all_documents, top_k, score_threshold)

        await self._on_query(query, dataset_ids, app_id, user_from, user_id)

        if all_documents:
            await self._on_retrival_end(all_documents, message_id, timer)

        return all_documents

    async def _on_retrival_end(
        self, documents: list[Document], message_id: Optional[str] = None, timer: Optional[dict] = None
    ) -> None:
        """Handle retrival end."""
        async with async_db.AsyncSessionLocal() as session:
            for document in documents:
                stmt = select(DocumentSegment).filter(
                    DocumentSegment.index_node_id == document.metadata['doc_id']
                )
                if 'dataset_id' in document.metadata:
                    stmt = stmt.filter(DocumentSegment.dataset_id == document.metadata['dataset_id'])

                result = await session.execute(stmt)
                segments = result.scalars().all()

                for segment in segments:
                    segment.hit_count += 1  # 修改对象字段

            await session.commit()  #

        # get tracing instance
        trace_manager: TraceQueueManager = self.application_generate_entity.trace_manager if self.application_generate_entity else None
        if trace_manager:
            trace_manager.add_trace_task(
                TraceTask(
                    TraceTaskName.DATASET_RETRIEVAL_TRACE,
                    message_id=message_id,
                    documents=documents,
                    timer=timer
                )
            )

    async def _on_query(self, query: str, dataset_ids: list[str], app_id: str, user_from: str, user_id: str) -> None:
        """
        Handle query.
        """
        if not query:
            return
        async with async_db.AsyncSessionLocal() as session:
            dataset_queries = []
            for dataset_id in dataset_ids:
                dataset_query = DatasetQuery(
                    dataset_id=dataset_id,
                    content=query,
                    source='app',
                    source_app_id=app_id,
                    created_by_role=user_from,
                    created_by=user_id
                )
                dataset_queries.append(dataset_query)

            if dataset_queries:
                session.add_all(dataset_queries)  # 使用异步 session 添加对象
                await session.commit()

    async def _retriever(self, dataset_id: str, query: str, top_k: int, all_documents: list):
        async with async_db.AsyncSessionLocal() as session:
            result = await session.execute(
                select(Dataset).filter(Dataset.id == dataset_id)
            )
            dataset = result.scalar_one_or_none()
            print("_retriever: dataset:::", dataset)
            if not dataset:
                return []

        # get retrieval model , if the model is not setting , using default
        retrieval_model = dataset.retrieval_model if dataset.retrieval_model else default_retrieval_model
        print("retrieval_model:::", retrieval_model, dataset.indexing_technique)
        if dataset.indexing_technique == "economy":
            # use keyword table query
            documents = await RetrievalService.async_retrieve(retrival_method='keyword_search',
                                                  dataset_id=dataset.id,
                                                  query=query,
                                                  top_k=top_k
                                                  )
            if documents:
                all_documents.extend(documents)
        else:
            print("top_k:::", top_k, query)
            if top_k > 0:
                # retrieval source
                documents = await RetrievalService.async_retrieve(retrival_method=retrieval_model['search_method'],
                                                      dataset_id=dataset.id,
                                                      query=query,
                                                      top_k=top_k,
                                                      score_threshold=retrieval_model['score_threshold']
                                                      if retrieval_model['score_threshold_enabled'] else None,
                                                      reranking_model=retrieval_model['reranking_model']
                                                      if retrieval_model['reranking_enable'] else None
                                                      )

                all_documents.extend(documents)

    def to_dataset_retriever_tool(self, tenant_id: str,
                                  dataset_ids: list[str],
                                  retrieve_config: DatasetRetrieveConfigEntity,
                                  return_resource: bool,
                                  invoke_from: InvokeFrom,
                                  hit_callback: DatasetIndexToolCallbackHandler) \
            -> Optional[list[DatasetRetrieverBaseTool]]:
        """
        A dataset tool is a tool that can be used to retrieve information from a dataset
        :param tenant_id: tenant id
        :param dataset_ids: dataset ids
        :param retrieve_config: retrieve config
        :param return_resource: return resource
        :param invoke_from: invoke from
        :param hit_callback: hit callback
        """
        tools = []
        available_datasets = []
        for dataset_id in dataset_ids:
            # get dataset from dataset id
            dataset = db.session.query(Dataset).filter(
                Dataset.tenant_id == tenant_id,
                Dataset.id == dataset_id
            ).first()

            # pass if dataset is not available
            if not dataset:
                continue

            # pass if dataset is not available
            if (dataset and dataset.available_document_count == 0
                    and dataset.available_document_count == 0):
                continue

            available_datasets.append(dataset)

        if retrieve_config.retrieve_strategy == DatasetRetrieveConfigEntity.RetrieveStrategy.SINGLE:
            # get retrieval model config
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

            for dataset in available_datasets:
                retrieval_model_config = dataset.retrieval_model \
                    if dataset.retrieval_model else default_retrieval_model

                # get top k
                top_k = retrieval_model_config['top_k']

                # get score threshold
                score_threshold = None
                score_threshold_enabled = retrieval_model_config.get("score_threshold_enabled")
                if score_threshold_enabled:
                    score_threshold = retrieval_model_config.get("score_threshold")

                tool = DatasetRetrieverTool.from_dataset(
                    dataset=dataset,
                    top_k=top_k,
                    score_threshold=score_threshold,
                    hit_callbacks=[hit_callback],
                    return_resource=return_resource,
                    retriever_from=invoke_from.to_source()
                )

                tools.append(tool)
        elif retrieve_config.retrieve_strategy == DatasetRetrieveConfigEntity.RetrieveStrategy.MULTIPLE:
            tool = DatasetMultiRetrieverTool.from_dataset(
                dataset_ids=[dataset.id for dataset in available_datasets],
                tenant_id=tenant_id,
                top_k=retrieve_config.top_k or 2,
                score_threshold=retrieve_config.score_threshold,
                hit_callbacks=[hit_callback],
                return_resource=return_resource,
                retriever_from=invoke_from.to_source(),
                reranking_provider_name=retrieve_config.reranking_model.get('reranking_provider_name'),
                reranking_model_name=retrieve_config.reranking_model.get('reranking_model_name')
            )

            tools.append(tool)

        return tools

    async def async_to_dataset_retriever_tool(self, tenant_id: str,
                                  dataset_ids: list[str],
                                  retrieve_config: DatasetRetrieveConfigEntity,
                                  return_resource: bool,
                                  invoke_from: InvokeFrom,
                                  hit_callback: AsyncDatasetIndexToolCallbackHandler,
                                  user_id: str,
                                  inputs: dict,) \
            -> Optional[list[AsyncDatasetRetrieverBaseTool]]:
        """
        A dataset tool is a tool that can be used to retrieve information from a dataset
        :param tenant_id: tenant id
        :param dataset_ids: dataset ids
        :param retrieve_config: retrieve config
        :param return_resource: return resource
        :param invoke_from: invoke from
        :param hit_callback: hit callback
        """
        tools = []
        available_datasets = []
        async with async_db.AsyncSessionLocal() as session:
            for dataset_id in dataset_ids:

                stmt = select(Dataset).filter(
                    Dataset.tenant_id == tenant_id,
                    Dataset.id == dataset_id
                )
                result = await session.execute(stmt)
                dataset = result.scalars().first()
                print("dataset:::dataset:::", dataset, tenant_id, dataset_id)
                if not dataset:
                    continue

                if dataset.provider != "external" and await dataset.async_available_document_count == 0:
                    continue

                available_datasets.append(dataset)
        print("available_datasets:::", available_datasets, retrieve_config.retrieve_strategy, tenant_id, dataset_ids)
        if retrieve_config.retrieve_strategy == DatasetRetrieveConfigEntity.RetrieveStrategy.SINGLE:
            # get retrieval model config
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

            for dataset in available_datasets:
                retrieval_model_config = dataset.retrieval_model \
                    if dataset.retrieval_model else default_retrieval_model

                # get top k
                top_k = retrieval_model_config['top_k']

                # get score threshold
                score_threshold = None
                score_threshold_enabled = retrieval_model_config.get("score_threshold_enabled")
                if score_threshold_enabled:
                    score_threshold = retrieval_model_config.get("score_threshold")

                tool = AsyncDatasetRetrieverTool.from_dataset(
                    dataset=dataset,
                    top_k=top_k,
                    score_threshold=score_threshold,
                    hit_callbacks=[hit_callback],
                    return_resource=return_resource,
                    retriever_from=invoke_from.to_source(),
                    retrieve_config=retrieve_config,
                    user_id = user_id,
                    inputs = inputs,
                )

                tools.append(tool)
        elif retrieve_config.retrieve_strategy == DatasetRetrieveConfigEntity.RetrieveStrategy.MULTIPLE:
            tool = DatasetMultiRetrieverTool.from_dataset(
                dataset_ids=[dataset.id for dataset in available_datasets],
                tenant_id=tenant_id,
                top_k=retrieve_config.top_k or 2,
                score_threshold=retrieve_config.score_threshold,
                hit_callbacks=[hit_callback],
                return_resource=return_resource,
                retriever_from=invoke_from.to_source(),
                reranking_provider_name=retrieve_config.reranking_model.get('reranking_provider_name'),
                reranking_model_name=retrieve_config.reranking_model.get('reranking_model_name')
            )

            tools.append(tool)

        return tools


    def calculate_keyword_score(self, query: str, documents: list[Document], top_k: int) -> list[Document]:
        """
        Calculate keywords scores
        :param query: search query
        :param documents: documents for reranking
        :param top_k: top k

        :return:
        """
        keyword_table_handler = JiebaKeywordTableHandler()
        query_keywords = keyword_table_handler.extract_keywords(query, None)
        documents_keywords = []
        for document in documents:
            if document.metadata is not None:
                # get the document keywords
                document_keywords = keyword_table_handler.extract_keywords(document.page_content, None)
                document.metadata["keywords"] = document_keywords
                documents_keywords.append(document_keywords)

        # Counter query keywords(TF)
        query_keyword_counts = Counter(query_keywords)

        # total documents
        total_documents = len(documents)

        # calculate all documents' keywords IDF
        all_keywords = set()
        for document_keywords in documents_keywords:
            all_keywords.update(document_keywords)

        keyword_idf = {}
        for keyword in all_keywords:
            # calculate include query keywords' documents
            doc_count_containing_keyword = sum(1 for doc_keywords in documents_keywords if keyword in doc_keywords)
            # IDF
            keyword_idf[keyword] = math.log((1 + total_documents) / (1 + doc_count_containing_keyword)) + 1

        query_tfidf = {}

        for keyword, count in query_keyword_counts.items():
            tf = count
            idf = keyword_idf.get(keyword, 0)
            query_tfidf[keyword] = tf * idf

        # calculate all documents' TF-IDF
        documents_tfidf = []
        for document_keywords in documents_keywords:
            document_keyword_counts = Counter(document_keywords)
            document_tfidf = {}
            for keyword, count in document_keyword_counts.items():
                tf = count
                idf = keyword_idf.get(keyword, 0)
                document_tfidf[keyword] = tf * idf
            documents_tfidf.append(document_tfidf)

        def cosine_similarity(vec1, vec2):
            intersection = set(vec1.keys()) & set(vec2.keys())
            numerator = sum(vec1[x] * vec2[x] for x in intersection)

            sum1 = sum(vec1[x] ** 2 for x in vec1)
            sum2 = sum(vec2[x] ** 2 for x in vec2)
            denominator = math.sqrt(sum1) * math.sqrt(sum2)

            if not denominator:
                return 0.0
            else:
                return float(numerator) / denominator

        similarities = []
        for document_tfidf in documents_tfidf:
            similarity = cosine_similarity(query_tfidf, document_tfidf)
            similarities.append(similarity)

        for document, score in zip(documents, similarities):
            # format document
            if document.metadata is not None:
                document.metadata["score"] = score
        documents = sorted(documents, key=lambda x: x.metadata.get("score", 0) if x.metadata else 0, reverse=True)
        return documents[:top_k] if top_k else documents

    def calculate_vector_score(
        self, all_documents: list[Document], top_k: int, score_threshold: float
    ) -> list[Document]:
        filter_documents = []
        for document in all_documents:
            if score_threshold is None or (document.metadata and document.metadata.get("score", 0) >= score_threshold):
                filter_documents.append(document)

        if not filter_documents:
            return []
        filter_documents = sorted(
            filter_documents, key=lambda x: x.metadata.get("score", 0) if x.metadata else 0, reverse=True
        )
        return filter_documents[:top_k] if top_k else filter_documents