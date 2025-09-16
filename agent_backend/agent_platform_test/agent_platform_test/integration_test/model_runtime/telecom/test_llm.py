"""
@Date    ：2024/7/25 14:22 
@Version: 1.0
@Description:

"""
from collections.abc import Generator

import pytest

from agent_platform_core.model_runtime.entities.llm_entities import LLMResult, LLMResultChunk, LLMResultChunkDelta
from agent_platform_core.model_runtime.entities.message_entities import (
    AssistantPromptMessage,
    PromptMessageTool,
    SystemPromptMessage,
    UserPromptMessage,
)
from agent_platform_basic.exceptions.model_runtime.validate import CredentialsValidateFailedError
from agent_platform_core.model_runtime.model_providers.telecom.llm.llm import TELECOMLargeLanguageModel

"""
Using QIming72B's OpenAI-compatible API as testing endpoint
"""


def test_validate_credentials():
    model = TELECOMLargeLanguageModel()

    with pytest.raises(CredentialsValidateFailedError):
        model.validate_credentials(
            model='qwen72B-res0522_phd25840_pd305_qhd1732_qhd24',
            credentials={
                'endpoint_url': 'http://10.238.190.77:28080/v1/',
                'mode': 'chat'
            }
        )

    model.validate_credentials(
        model='qwen72B-res0522_phd25840_pd305_qhd1732_qhd24',
        credentials={
            'endpoint_url': 'http://10.238.190.77:28080/v1/',
            'mode': 'chat'
        }
    )


def test_invoke_model():
    model = TELECOMLargeLanguageModel()

    response = model.invoke(
        model='qwen72B-res0522_phd25840_pd305_qhd1732_qhd24',
        credentials={
            'endpoint_url': 'http://10.238.190.77:28080/v1/',
            'mode': 'chat'
        },
        prompt_messages=[
            SystemPromptMessage(
                content='你是由电信公司训练的，名字是“启明大模型”。你是属于电信领域大模型，你擅长直接回答电信公司的领域类的问题。电信领域包括无线、核心网、家庭宽带、移动终端、iTV、云K歌、天翼云等业务。',
            ),
            UserPromptMessage(
                content='如何解决固话来电显示不正常的问题？'
            )
        ],
        model_parameters={
            'temperature': 1.0,
            'top_k': 2,
            'top_p': 0.5,
        },
        stop=['How'],
        stream=False,
        user="abc-123"
    )

    assert isinstance(response, LLMResult)
    assert len(response.message.content) > 0


def test_invoke_stream_model():
    model = TELECOMLargeLanguageModel()

    response = model.invoke(
        model='qwen72B-res0522_phd25840_pd305_qhd1732_qhd24',
        credentials={
            'endpoint_url': 'http://10.238.190.77:28080/v1/',
            'mode': 'chat',
            'stream_mode_delimiter': '\\n\\n'
        },
        prompt_messages=[
            SystemPromptMessage(
                content='你是由电信公司训练的，名字是“启明大模型”。你是属于电信领域大模型，你擅长直接回答电信公司的领域类的问题。电信领域包括无线、核心网、家庭宽带、移动终端、iTV、云K歌、天翼云等业务。',
            ),
            UserPromptMessage(
                content='如何解决固话来电显示不正常的问题？'
            )
        ],
        model_parameters={
            'temperature': 1.0,
            'top_k': 2,
            'top_p': 0.5,
        },
        stop=['How'],
        stream=True,
        user="abc-123"
    )

    assert isinstance(response, Generator)

    for chunk in response:
        assert isinstance(chunk, LLMResultChunk)
        assert isinstance(chunk.delta, LLMResultChunkDelta)
        assert isinstance(chunk.delta.message, AssistantPromptMessage)


def test_invoke_stream_model_without_delimiter():
    model = TELECOMLargeLanguageModel()

    response = model.invoke(
        model='qwen72B-res0522_phd25840_pd305_qhd1732_qhd24',
        credentials={
            'endpoint_url': 'http://10.238.190.77:28080/v1/',
            'mode': 'chat'
        },
        prompt_messages=[
            SystemPromptMessage(
                content='你是由电信公司训练的，名字是“启明大模型”。你是属于电信领域大模型，你擅长直接回答电信公司的领域类的问题。电信领域包括无线、核心网、家庭宽带、移动终端、iTV、云K歌、天翼云等业务。',
            ),
            UserPromptMessage(
                content='如何解决固话来电显示不正常的问题？'
            )
        ],
        model_parameters={
            'temperature': 1.0,
            'top_k': 2,
            'top_p': 0.5,
        },
        stop=['How'],
        stream=True,
        user="abc-123"
    )

    assert isinstance(response, Generator)

    for chunk in response:
        assert isinstance(chunk, LLMResultChunk)
        assert isinstance(chunk.delta, LLMResultChunkDelta)
        assert isinstance(chunk.delta.message, AssistantPromptMessage)

# # using Qiming72B as testing endpoint
# def test_invoke_chat_model_with_tools():
#     model = TELECOMLargeLanguageModel()
#
#     result = model.invoke(
#         model='qwen72B-res0522_phd25840_pd305_qhd1732_qhd24',
#         credentials={
#             'endpoint_url': 'http://10.238.190.77:28080/v1/',
#             'mode': 'chat'
#         },
#         prompt_messages=[
#             SystemPromptMessage(
#                 content='Follow the instructions',
#             ),
#             UserPromptMessage(
#                 content="Today's date？"
#             )
#         ],
#         tools=[
#             PromptMessageTool(
#                 name='current_time',
#                 description='A tool for getting the current time',
#                 parameters={
#                     "type": "string",
#                     "required": [
#                         "false"
#                     ]
#                 }
#             ),
#         ],
#         model_parameters={
#             'temperature': 0.5,
#             'max_tokens': 1024
#         },
#         stream=False,
#         user="abc-123"
#     )
#
#     assert isinstance(result, LLMResult)
#     assert isinstance(result.message, AssistantPromptMessage)
#     assert len(result.message.tool_calls) > 0


def test_get_num_tokens():
    model = TELECOMLargeLanguageModel()

    num_tokens = model.get_num_tokens(
        model='qwen72B-res0522_phd25840_pd305_qhd1732_qhd24',
        credentials={
            'endpoint_url': 'http://10.238.190.77:28080/v1/',
            'mode': 'chat'
        },
        prompt_messages=[
            SystemPromptMessage(
                content='你是由电信公司训练的，名字是“启明大模型”。你是属于电信领域大模型，你擅长直接回答电信公司的领域类的问题。电信领域包括无线、核心网、家庭宽带、移动终端、iTV、云K歌、天翼云等业务。',
            ),
            UserPromptMessage(
                content='如何解决固话来电显示不正常的问题？'
            )
        ])

    assert isinstance(num_tokens, int)
    assert num_tokens == 233
