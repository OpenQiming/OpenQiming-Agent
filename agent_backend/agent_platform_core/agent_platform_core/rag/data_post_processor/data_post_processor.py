from typing import Optional

from agent_platform_basic.exceptions.model_runtime.invoke import InvokeAuthorizationError
from agent_platform_core.model_manager import ModelManager
from agent_platform_core.model_runtime.entities.model_entities import ModelType
from agent_platform_core.rag.data_post_processor.reorder import ReorderRunner
from agent_platform_core.rag.models.document import Document
from agent_platform_core.rag.rerank.rerank import RerankRunner
from agent_platform_core.rag.rerank.rerank_base import BaseRerankRunner


class DataPostProcessor:
    """Interface for data post-processing document.
    """

    def __init__(
            self,
            tenant_id: str,
            reranking_mode: str,
            reranking_model: dict,
            weights: Optional[dict] = None,
            reorder_enabled: bool = False):
        self.rerank_runner = self._get_rerank_runner(reranking_mode, tenant_id, reranking_model, weights)
        self.reorder_runner = self._get_reorder_runner(reorder_enabled)

    def invoke(self, query: str, documents: list[Document], score_threshold: Optional[float] = None,
               top_n: Optional[int] = None, user: Optional[str] = None) -> list[Document]:
        if self.rerank_runner:
            documents = self.rerank_runner.run(query, documents, score_threshold, top_n, user)

        if self.reorder_runner:
            documents = self.reorder_runner.run(documents)

        return documents

    def _get_rerank_runner(
            self,
            reranking_mode: str,
            tenant_id: str,
            reranking_model: Optional[dict] = None,
            weights: Optional[dict] = None,
    ) -> Optional[BaseRerankRunner]:
        if reranking_model:
            try:
                model_manager = ModelManager()
                rerank_model_instance = model_manager.get_model_instance(
                    tenant_id=tenant_id,
                    provider=reranking_model['reranking_provider_name'],
                    model_type=ModelType.RERANK,
                    model=reranking_model['reranking_model_name']
                )
            except InvokeAuthorizationError:
                return None
            return RerankRunner(rerank_model_instance)
        return None

    def _get_reorder_runner(self, reorder_enabled) -> Optional[ReorderRunner]:
        if reorder_enabled:
            return ReorderRunner()
        return None


