"""

@Date    ：2024/9/24 15:22 
@Version: 1.0
@Description:

"""
from typing import Optional

from pydantic import BaseModel, Field


class Enabled(BaseModel):
    enabled: bool


class SensitiveWordAvoidance(Enabled):
    configs: dict
    type: str


class TextToSpeech(Enabled):
    voice: Optional[str] = None
    language: Optional[str] = None


class Model(BaseModel):
    mode: str
    name: str
    provider: str
    completion_params: dict


class Image(Enabled):
    detail: str
    number_limits: int
    transfer_methods: list[str]


class FileUpload(BaseModel):
    image: Image


class DatasetsConfig(BaseModel):
    datasets: dict
    retrieval_model: str


class Tool(Enabled):
    isDeleted: bool
    notAuthor: bool
    provider_id: str
    provider_name: str
    provider_type: str
    tool_name: str
    tool_parameters: dict


class AgentMode(Enabled):
    max_iteration: int
    prompt: Optional[str] = Field(None, description="Agent提示词模板")
    strategy: str
    tools: list[Tool]


class PublishAgentReq(BaseModel):
    user_input_form: list
    opening_statement: Optional[str] = Field(None, description="开场白")
    pre_prompt: Optional[str] = Field(None, description="提示词")
    model: Model
    agent_mode: AgentMode
    chat_prompt_config: dict
    completion_prompt_config: dict
    dataset_configs: DatasetsConfig
    dataset_query_variable: str
    file_upload: FileUpload
    prompt_type: str
    retriever_resource: Enabled
    speech_to_text: Enabled
    text_to_speech: TextToSpeech
    suggested_questions: list[str]
    suggested_questions_after_answer: Enabled
    more_like_this: Enabled
    header_image: Optional[str] = Field(None, description="header图片")
    name: Optional[str] = Field(None, description="应用名称")
