from typing import Optional

from pydantic import Field
from agent_platform_common.configs.extra.sentry_config import SentryConfig

"""
@Date: 2024/07/08
@Version: 1.0
@Description:
    ExtraService Config
"""


class ExtraServiceConfig(
    SentryConfig
):
    QIMING_GET_USERINFO_URL: Optional[str] = Field(
        description='qiming get user info url',
        default=None,
    )

    DEFAULT_TENANT_NAME: Optional[str] = Field(
        description='default tenant name',
        default=None,
    )

    GLOBAL_TENANT_ID: Optional[str] = Field(
        description='global tenant id',
        default=None,
    )

    GLOBAL_SHARE_TENANT_ID: Optional[str] = Field(
        description='global share tenant id',
        default=None,
    )

    LLAMA_MODEL_NAME_70B: Optional[str] = Field(
        description='model name',
        default=None,
    )

    X_APP_ID: Optional[str] = Field(
        description='x-app-id',
        default=None,
    )

    X_APP_KEY: Optional[str] = Field(
        description='x-app-key',
        default=None,
    )

    TOOL_CHAIN_CHANGE_USE_PATH: Optional[str] = Field(
        description='when model used or unused，send tool chain message',
        default=None,
    )

    BASE_TOOLCHAIN_INTERFACE_ENDPOINT: Optional[str] = Field(
        description='tool chain interface endpoint',
        default=None,
    )

    BASE_WORKFLOW_API_ENDPOINT: Optional[str] = Field(
        description='workflow-api endpoint',
        default=None,
    )

    WORKFLOW_PATH: Optional[str] = Field(
        description='workflow path',
        default=None,
    )

    WORKFLOW_API_SERVICE: Optional[str] = Field(
        description='workflow_api service',
        default="workflow-api",
    )

    INTF_RESTFUL_SERVICE: Optional[str] = Field(
        description='intf-restful service',
        default="intf-restful-service",
    )

    TOOL_CHAIN_STATISTICS_PATH: Optional[str] = Field(
        description='statistics path',
        default=None,
    )
    HISTORY_VERSION_NUMBER: Optional[int] = Field(
        description='HISTORY_VERSION_NUMBER',
        default=5,
    )

    RAG_ASSISTANT_LIST_URL: Optional[str] = Field(
        description='RAG Assistant List URL',
        default=None,
    )

    RAG_INTERFACE_ENDPOINT: Optional[str] = Field(
        description='RAG Interface Endpoint',
        default=None
    )

    RAG_AGENT_SERVICE: Optional[str] = Field(
        description='RAG Agent Service',
        default='serviceAgent'
    )

    ASSISTANT_RAG_TAG_X_APP_ID: Optional[str] = Field(
        description='assistant-rag-tag-x-app-id',
        default=None,
    )

    ASSISTANT_RAG_TAG_X_APP_KEY: Optional[str] = Field(
        description='assistant-rag-tag-x-app-key',
        default=None,
    )

    ASSISTANT_RAG_X_APP_ID: Optional[str] = Field(
        description='assistant-rag-x-app-id',
        default=None,
    )

    ASSISTANT_RAG_X_APP_KEY: Optional[str] = Field(
        description='assistant-rag-x-app-key',
        default=None,
    )

    ROOT_PATH: Optional[str] = Field(description=''
                                     , default=None, )

    BASE_KNOWLEDGE_API_ENDPOINT: Optional[str] = Field(
    description='kb base url',
    default=None,
    )

    KAFKA_IP: Optional[str] = Field(
        description='kafka ip',
        default=None,
    )

    KAFKA_TOPIC: Optional[str] = Field(
        description='kafka topic',
        default=None,
    )

    KAFKA_USER: Optional[str] = Field(
        description='kafka name',
        default=None,
    )

    KAFKA_PASSWORD: Optional[str] = Field(
        description='kafka password',
        default=None,
    )

    HOST_IP: Optional[str] = Field(
        description='kafka topic',
        default=None,
    )

    ES_IP: Optional[str] = Field(
        description='es ip',
        default=None,
    )

    ES_INDEX: Optional[str] = Field(
        description='es index',
        default=None,
    )

    ES_USER: Optional[str] = Field(
        description='es user',
        default=None,
    )

    ES_PASSWORD: Optional[str] = Field(
        description='es password',
        default=None,
    )

    PLATFORM_VERSION: Optional[str] = Field(
        description='platform version',
        default=None,
    )

