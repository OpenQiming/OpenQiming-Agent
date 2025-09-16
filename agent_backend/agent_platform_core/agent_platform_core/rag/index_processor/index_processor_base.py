"""Abstract interface for document loader implementations."""
from abc import ABC, abstractmethod
from typing import Optional

from flask import current_app

from agent_platform_core.model_manager import ModelInstance
from agent_platform_core.models.db_model.dataset import Dataset, DatasetProcessRule
from agent_platform_core.rag.extractor.entity.extract_setting import ExtractSetting
from agent_platform_core.rag.models.document import Document
from agent_platform_core.rag.splitter.fixed_text_splitter import (
    EnhanceRecursiveCharacterTextSplitter,
    FixedRecursiveCharacterTextSplitter,
)
from agent_platform_core.rag.splitter.text_splitter import TextSplitter


class BaseIndexProcessor(ABC):
    """Interface for extract files.
    """

    @abstractmethod
    def extract(self, extract_setting: ExtractSetting, **kwargs) -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    def transform(self, documents: list[Document], **kwargs) -> list[Document]:
        raise NotImplementedError

    @abstractmethod
    def load(self, dataset: Dataset, documents: list[Document], with_keywords: bool = True, **kwargs):
        raise NotImplementedError

    def clean(self, dataset: Dataset, node_ids: Optional[list[str]], with_keywords: bool = True, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, retrival_method: str, query: str, dataset: Dataset, top_k: int,
                 score_threshold: float, reranking_model: dict) -> list[Document]:
        raise NotImplementedError

    def _get_splitter(self, processing_rule: dict,
                      embedding_model_instance: Optional[ModelInstance]) -> TextSplitter:
        """
        Get the NodeParser object according to the processing rule.
        """
        if processing_rule['mode'] == "custom":
            # The user-defined segmentation rule
            rules = processing_rule['rules']
            segmentation = rules["segmentation"]
            max_segmentation_tokens_length = int(current_app.config['INDEXING_MAX_SEGMENTATION_TOKENS_LENGTH'])
            if segmentation["max_tokens"] < 50 or segmentation["max_tokens"] > max_segmentation_tokens_length:
                raise ValueError(f"Custom segment length should be between 50 and {max_segmentation_tokens_length}.")

            separator = segmentation["separator"]
            if separator:
                separator = separator.replace('\\n', '\n')

            character_splitter = FixedRecursiveCharacterTextSplitter.from_encoder(
                chunk_size=segmentation["max_tokens"],
                chunk_overlap=segmentation.get('chunk_overlap', 0),
                fixed_separator=separator,
                separators=["\n\n", "。", ". ", " ", ""],
                embedding_model_instance=embedding_model_instance
            )
        else:
            # Automatic segmentation
            character_splitter = EnhanceRecursiveCharacterTextSplitter.from_encoder(
                chunk_size=DatasetProcessRule.AUTOMATIC_RULES['segmentation']['max_tokens'],
                chunk_overlap=DatasetProcessRule.AUTOMATIC_RULES['segmentation']['chunk_overlap'],
                separators=["\n\n", "。", ". ", " ", ""],
                embedding_model_instance=embedding_model_instance
            )

        return character_splitter
