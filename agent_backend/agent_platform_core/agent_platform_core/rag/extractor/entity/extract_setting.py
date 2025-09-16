from typing import Optional, Literal

from pydantic import BaseModel, ConfigDict

from agent_platform_core.models.db_model.dataset import Document
from agent_platform_core.models.db_model.model import UploadFile


class NotionInfo(BaseModel):
    """
    Notion import info.
    """
    notion_workspace_id: str
    notion_obj_id: str
    notion_page_type: str
    document: Document = None
    tenant_id: str
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data) -> None:
        super().__init__(**data)


class WebsiteInfo(BaseModel):
    """
    website import info.
    """
    provider: str
    job_id: str
    url: str
    mode: str
    tenant_id: str
    only_main_content: bool = False

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data) -> None:
        super().__init__(**data)


class ExtractSetting(BaseModel):
    """
    Model class for provider response.
    """
    datasource_type: str
    upload_file: Optional[UploadFile] = None
    notion_info: Optional[NotionInfo] = None
    website_info: Optional[WebsiteInfo] = None
    document_model: Optional[str] = None
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, **data) -> None:
        super().__init__(**data)


class RerankingModel(BaseModel):
    reranking_provider_name: Optional[str] = None
    reranking_model_name: Optional[str] = None


class WeightVectorSetting(BaseModel):
    vector_weight: float
    embedding_provider_name: str
    embedding_model_name: str


class WeightKeywordSetting(BaseModel):
    keyword_weight: float


class WeightModel(BaseModel):
    weight_type: Optional[str] = None
    vector_setting: Optional[WeightVectorSetting] = None
    keyword_setting: Optional[WeightKeywordSetting] = None


class RetrievalModel(BaseModel):
    search_method: Literal["hybrid_search", "semantic_search", "full_text_search"]
    reranking_enable: bool
    reranking_model: Optional[RerankingModel] = None
    reranking_mode: Optional[str] = None
    top_k: int
    score_threshold_enabled: bool
    score_threshold: Optional[float] = None
    weights: Optional[WeightModel] = None
