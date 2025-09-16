import json
from decimal import Decimal
from typing import Optional, Union, Generator, Mapping, cast, AsyncGenerator
from urllib.parse import urljoin

import httpx
import requests

from agent_platform_basic.exceptions.model_runtime.invoke import InvokeError
from agent_platform_basic.exceptions.model_runtime.validate import CredentialsValidateFailedError
from agent_platform_core.model_runtime.entities.common_entities import I18nObject
from agent_platform_core.model_runtime.entities.llm_entities import LLMResult, LLMMode, LLMResultChunk, \
    LLMResultChunkDelta
from agent_platform_core.model_runtime.entities.message_entities import PromptMessage, PromptMessageTool, \
    UserPromptMessage, \
    PromptMessageContentType, PromptMessageContent, ImagePromptMessageContent, AssistantPromptMessage, \
    SystemPromptMessage, ToolPromptMessage, PromptMessageFunction
from agent_platform_core.model_runtime.entities.model_entities import ParameterRule, DefaultParameterName, \
    ParameterType, PriceConfig, \
    ModelPropertyKey, AIModelEntity, ModelType, FetchFrom, ModelFeature
from agent_platform_core.model_runtime.model_providers.__base.large_language_model import LargeLanguageModel
from agent_platform_core.model_runtime.utils import helper

"""
@Date    ：2024/7/10 19:47
@Version: 1.0
@Description:

"""


class TELECOMLargeLanguageModel(LargeLanguageModel):
    """
    Model class for China TeleCOM large language model.
    """

    def _invoke(self, model: str, credentials: dict, prompt_messages: list[PromptMessage], model_parameters: dict,
                tools: Optional[list[PromptMessageTool]] = None, stop: Optional[list[str]] = None,
                stream: bool = True, user: Optional[str] = None) \
            -> Union[LLMResult, Generator]:
        """
        Invoke large language model

        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """

        # text completion model

        return self._generate(
            model=model,
            credentials=credentials,
            prompt_messages=prompt_messages,
            model_parameters=model_parameters,
            tools=tools,
            stop=stop,
            stream=stream,
            user=user
        )

    async def _async_invoke(self, model: str, credentials: dict, prompt_messages: list[PromptMessage],
                            model_parameters: dict,
                            tools: Optional[list[PromptMessageTool]] = None, stop: Optional[list[str]] = None,
                            stream: bool = True, user: Optional[str] = None) \
            -> Union[LLMResult, AsyncGenerator]:
        """
        Invoke large language model

        :param model: model name
        :param credentials: model credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param tools: tools for tool calling
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """

        # text completion model

        return await self._async_generate(
            model=model,
            credentials=credentials,
            prompt_messages=prompt_messages,
            model_parameters=model_parameters,
            tools=tools,
            stop=stop,
            stream=stream,
            user=user
        )

    def get_customizable_model_schema(self, model: str, credentials: dict) -> AIModelEntity:
        """
            generate custom model entities from credentials
        """
        features = []

        function_calling_type = credentials.get('function_calling_type', 'no_call')
        if function_calling_type in ['function_call']:
            features.append(ModelFeature.TOOL_CALL)
        elif function_calling_type in ['tool_call']:
            features.append(ModelFeature.MULTI_TOOL_CALL)

        stream_function_calling = credentials.get('stream_function_calling', 'supported')
        if stream_function_calling == 'supported':
            features.append(ModelFeature.STREAM_TOOL_CALL)

        vision_support = credentials.get('vision_support', 'not_support')
        if vision_support == 'support':
            features.append(ModelFeature.VISION)

        entity = AIModelEntity(
            model=model,
            label=I18nObject(en_US=model),
            model_type=ModelType.LLM,
            fetch_from=FetchFrom.CUSTOMIZABLE_MODEL,
            features=features,
            model_properties={
                ModelPropertyKey.CONTEXT_SIZE: int(credentials.get('context_size', "4096")),
                ModelPropertyKey.MODE: credentials.get('mode'),
            },
            parameter_rules=[
                ParameterRule(
                    name=DefaultParameterName.TEMPERATURE.value,
                    label=I18nObject(en_US="Temperature"),
                    type=ParameterType.FLOAT,
                    default=float(credentials.get('temperature', 0.7)),
                    min=0,
                    max=2,
                    precision=2
                ),
                ParameterRule(
                    name=DefaultParameterName.TOP_P.value,
                    label=I18nObject(en_US="Top P"),
                    type=ParameterType.FLOAT,
                    default=float(credentials.get('top_p', 1)),
                    min=0,
                    max=1,
                    precision=2
                ),
                ParameterRule(
                    name=DefaultParameterName.FREQUENCY_PENALTY.value,
                    label=I18nObject(en_US="Frequency Penalty"),
                    type=ParameterType.FLOAT,
                    default=float(credentials.get('frequency_penalty', 0)),
                    min=-2,
                    max=2
                ),
                ParameterRule(
                    name=DefaultParameterName.PRESENCE_PENALTY.value,
                    label=I18nObject(en_US="Presence Penalty"),
                    type=ParameterType.FLOAT,
                    default=float(credentials.get('presence_penalty', 0)),
                    min=-2,
                    max=2
                ),
                ParameterRule(
                    name=DefaultParameterName.MAX_TOKENS.value,
                    label=I18nObject(en_US="Max Tokens"),
                    type=ParameterType.INT,
                    default=512,
                    min=1,
                    max=int(credentials.get('max_tokens_to_sample', 4096)),
                )
            ],
            pricing=PriceConfig(
                input=Decimal(credentials.get('input_price', 0)),
                output=Decimal(credentials.get('output_price', 0)),
                unit=Decimal(credentials.get('unit', 0)),
                currency=credentials.get('currency', "USD")
            ),
        )

        if credentials['mode'] == 'chat':
            entity.model_properties[ModelPropertyKey.MODE] = LLMMode.CHAT.value
        elif credentials['mode'] == 'completion':
            entity.model_properties[ModelPropertyKey.MODE] = LLMMode.COMPLETION.value
        else:
            raise ValueError(f"Unknown completion type {credentials['completion_type']}")

        return entity

    @property
    def _invoke_error_mapping(self) -> dict[type[InvokeError], list[type[Exception]]]:
        pass

    async def async_get_num_tokens(self, model: str, credentials: dict, prompt_messages: list[PromptMessage],
                       tools: Optional[list[PromptMessageTool]] = None) -> int:
        return self._num_tokens_from_messages(model, credentials, prompt_messages, tools)

    def get_num_tokens(self, model: str, credentials: dict, prompt_messages: list[PromptMessage],
                       tools: Optional[list[PromptMessageTool]] = None) -> int:

        return self._num_tokens_from_messages(model, credentials, prompt_messages, tools)

    def _num_tokens_from_messages(self, model: str, credentials: dict, prompt_messages: list[PromptMessage],
                                  tools: Optional[list[PromptMessageTool]]):

        tokens_per_message = 3
        tokens_per_name = 1

        num_tokens = 0
        messages_dict = [(self._convert_prompt_message_to_dict(message, credentials)) for message in prompt_messages]
        for message in messages_dict:
            num_tokens += tokens_per_message
            for key, value in message.items():
                if isinstance(value, list):
                    text = ''
                    for item in value:
                        if isinstance(item, dict) and item['type'] == 'text':
                            text += item['text']
                    value = text
                if key == "tool_calls":
                    for tool_call in value:
                        for t_key, t_value in tool_call.items():
                            num_tokens += self._get_num_tokens_by_gpt2(t_key)
                            if t_key == "function":
                                for f_key, f_value in t_value.items():
                                    num_tokens += self._get_num_tokens_by_gpt2(f_key)
                                    num_tokens += self._get_num_tokens_by_gpt2(f_value)
                            else:
                                num_tokens += self._get_num_tokens_by_gpt2(t_key)
                                num_tokens += self._get_num_tokens_by_gpt2(t_value)
                else:
                    num_tokens += self._get_num_tokens_by_gpt2(str(value))

                if key == 'name':
                    num_tokens += tokens_per_name
        num_tokens += 3

        if tools:
            num_tokens += self._num_tokens_for_tools(tools)
        return num_tokens

    def _num_tokens_for_tools(self, tools: list[PromptMessageTool]) -> int:
        """
        Calculate num tokens for tool calling with tiktoken package.

        :param tools: tools for tool calling
        :return: number of tokens
        """
        num_tokens = 0
        for tool in tools:
            num_tokens += self._get_num_tokens_by_gpt2('type')
            num_tokens += self._get_num_tokens_by_gpt2('function')
            num_tokens += self._get_num_tokens_by_gpt2('function')

            # calculate num tokens for function object
            num_tokens += self._get_num_tokens_by_gpt2('name')
            num_tokens += self._get_num_tokens_by_gpt2(tool.name)
            num_tokens += self._get_num_tokens_by_gpt2('description')
            num_tokens += self._get_num_tokens_by_gpt2(tool.description)
            parameters = tool.parameters
            num_tokens += self._get_num_tokens_by_gpt2('parameters')
            if 'title' in parameters:
                num_tokens += self._get_num_tokens_by_gpt2('title')
                num_tokens += self._get_num_tokens_by_gpt2(parameters.get("title"))
            num_tokens += self._get_num_tokens_by_gpt2('type')
            num_tokens += self._get_num_tokens_by_gpt2(parameters.get("type"))
            if 'properties' in parameters:
                num_tokens += self._get_num_tokens_by_gpt2('properties')
                for key, value in parameters.get('properties').items():
                    num_tokens += self._get_num_tokens_by_gpt2(key)
                    for field_key, field_value in value.items():
                        num_tokens += self._get_num_tokens_by_gpt2(field_key)
                        if field_key == 'enum':
                            for enum_field in field_value:
                                num_tokens += 3
                                num_tokens += self._get_num_tokens_by_gpt2(enum_field)
                        else:
                            num_tokens += self._get_num_tokens_by_gpt2(field_key)
                            num_tokens += self._get_num_tokens_by_gpt2(str(field_value))
            if 'required' in parameters:
                num_tokens += self._get_num_tokens_by_gpt2('required')
                for required_field in parameters['required']:
                    num_tokens += 3
                    num_tokens += self._get_num_tokens_by_gpt2(required_field)

        return num_tokens

    def validate_credentials(self, model: str, credentials: Mapping) -> None:
        """
        Validate model credentials using requests to ensure compatibility with all providers following OpenAI's API standard.

        :param model: model name
        :param credentials: model credentials
        :return:
        """
        try:
            headers = {
                'Content-Type': 'application/json'
            }

            api_key = credentials.get('api_key')
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            endpoint_url = credentials['endpoint_url']
            if not endpoint_url.endswith('/'):
                endpoint_url += '/'

            # prepare the payload for a simple ping to the model
            data = {
                'model': model,
                'max_tokens': 5
            }

            completion_type = LLMMode.value_of(credentials['mode'])

            if completion_type is LLMMode.CHAT:
                data['messages'] = [
                    {
                        "role": "user",
                        "content": "ping"
                    },
                ]
                endpoint_url = urljoin(endpoint_url, 'chat/completions')
            elif completion_type is LLMMode.COMPLETION:
                data['prompt'] = 'ping'
                endpoint_url = urljoin(endpoint_url, 'completions')
            else:
                raise ValueError("Unsupported completion type for model configuration.")

            # send a post request to validate the credentials
            response = requests.post(
                endpoint_url,
                headers=headers,
                json=data,
                timeout=(10, 300)
            )

            if response.status_code != 200:
                raise CredentialsValidateFailedError(
                    f'Credentials validation failed with status code {response.status_code}')

            try:
                json_result = response.json()
            except json.JSONDecodeError as e:
                raise CredentialsValidateFailedError('Credentials validation failed: JSON decode error')

            if (completion_type is LLMMode.CHAT and json_result['object'] == ''):
                json_result['object'] = 'chat.completion'
            elif (completion_type is LLMMode.COMPLETION and json_result['object'] == ''):
                json_result['object'] = 'text_completion'

            if (completion_type is LLMMode.CHAT
                    and ('object' not in json_result or json_result['object'] != 'chat.completion')):
                raise CredentialsValidateFailedError(
                    'Credentials validation failed: invalid response object, must be \'chat.completion\'')
            elif (completion_type is LLMMode.COMPLETION
                  and ('object' not in json_result or json_result['object'] != 'text_completion')):
                raise CredentialsValidateFailedError(
                    'Credentials validation failed: invalid response object, must be \'text_completion\'')
        except CredentialsValidateFailedError:
            raise
        except Exception as ex:
            raise CredentialsValidateFailedError(f'An error occurred during credentials validation: {str(ex)}')

    def _generate(self, model: str, credentials: dict, prompt_messages: list[PromptMessage], model_parameters: dict,
                  tools: Optional[list[PromptMessageTool]] = None, stop: Optional[list[str]] = None,
                  stream: bool = True, user: Optional[str] = None) -> Union[LLMResult, Generator]:
        """
        Invoke llm completion model

        :param model: model name
        :param credentials: credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept-Charset': 'utf-8',
        }
        extra_headers = credentials.get('extra_headers')
        if extra_headers is not None:
            headers = {
                **headers,
                **extra_headers,
            }

        api_key = credentials.get('api_key')
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        endpoint_url = credentials["endpoint_url"]
        if not endpoint_url.endswith('/'):
            endpoint_url += '/'

        data = {
            "model": model,
            "stream": stream,
            **model_parameters,
            "max_tokens": 4096
        }

        completion_type = LLMMode.value_of(credentials['mode'])

        if completion_type is LLMMode.CHAT:
            endpoint_url = urljoin(endpoint_url, 'chat/completions')
            data['messages'] = [self._convert_prompt_message_to_dict(prompt_message, credentials) for prompt_message in
                                prompt_messages]
        elif completion_type is LLMMode.COMPLETION:
            endpoint_url = urljoin(endpoint_url, 'completions')
            data['prompt'] = prompt_messages[0].content
        else:
            raise ValueError("Unsupported completion type for model configuration.")

        # annotate tools with names , descriptions , etc
        function_calling_type = credentials.get('function_calling_type', 'no_call')
        formatted_tools = []
        if tools:
            if function_calling_type == 'function_call':
                data['functions'] = [
                    {"name": tool.name, "description": tool.description, "parameters": tool.parameters}
                    for tool in tools
                ]
            elif function_calling_type == 'tool_call':
                data["tool_choice"] = "auto"

                for tool in tools:
                    formatted_tools.append(helper.dump_model(PromptMessageFunction(function=tool)))

                data['tools'] = formatted_tools
        if stop:
            data['stop'] = stop

        if user:
            data["user"] = user

        response = requests.post(
            endpoint_url,
            headers=headers,
            json=data,
            timeout=(10, 300),
            stream=stream
        )

        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = 'utf-8'

        if response.status_code != 200:
            raise InvokeError(f"API request failed with status code {response.status_code}: {response.text}")

        if stream:
            return self._handle_generate_stream_response(model, credentials, response, prompt_messages)

        return self._handle_generate_response(model, credentials, response, prompt_messages)

    async def _async_generate(self, model: str, credentials: dict, prompt_messages: list[PromptMessage],
                              model_parameters: dict,
                              tools: Optional[list[PromptMessageTool]] = None, stop: Optional[list[str]] = None,
                              stream: bool = True, user: Optional[str] = None) -> Union[LLMResult, AsyncGenerator]:
        """
        Invoke llm completion model

        :param model: model name
        :param credentials: credentials
        :param prompt_messages: prompt messages
        :param model_parameters: model parameters
        :param stop: stop words
        :param stream: is stream response
        :param user: unique user id
        :return: full response or stream response chunk generator result
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept-Charset': 'utf-8',
        }
        extra_headers = credentials.get('extra_headers')
        if extra_headers is not None:
            headers = {
                **headers,
                **extra_headers,
            }

        api_key = credentials.get('api_key')
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        endpoint_url = credentials["endpoint_url"]
        if not endpoint_url.endswith('/'):
            endpoint_url += '/'

        data = {
            "model": model,
            "stream": stream,
            **model_parameters,
            "max_tokens": 4096
        }

        completion_type = LLMMode.value_of(credentials['mode'])

        if completion_type is LLMMode.CHAT:
            endpoint_url = urljoin(endpoint_url, 'chat/completions')
            data['messages'] = [self._convert_prompt_message_to_dict(prompt_message, credentials) for prompt_message in
                                prompt_messages]
        elif completion_type is LLMMode.COMPLETION:
            endpoint_url = urljoin(endpoint_url, 'completions')
            data['prompt'] = prompt_messages[0].content
        else:
            raise ValueError("Unsupported completion type for model configuration.")

        # annotate tools with names , descriptions , etc
        function_calling_type = credentials.get('function_calling_type', 'no_call')
        formatted_tools = []
        if tools:
            if function_calling_type == 'function_call':
                data['functions'] = [
                    {"name": tool.name, "description": tool.description, "parameters": tool.parameters}
                    for tool in tools
                ]
            elif function_calling_type == 'tool_call':
                data["tool_choice"] = "auto"

                for tool in tools:
                    formatted_tools.append(helper.dump_model(PromptMessageFunction(function=tool)))

                data['tools'] = formatted_tools
        if stop:
            data['stop'] = stop

        if user:
            data["user"] = user

        if stream:
            return self._async_handle_generate_stream_response(model, credentials, endpoint_url, headers, data,
                                                               prompt_messages)
        else:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(endpoint_url, headers=headers, json=data)
                return self._handle_generate_response(model, credentials, response, prompt_messages)

    def _handle_generate_stream_response(self, model: str, credentials: dict, response: requests.Response,
                                         prompt_messages: list[PromptMessage]) -> Generator:
        """
        功能：处理 LLM 流响应。
        参数：model 表示模型名称，credentials 表示模型凭证，response 表示流响应，prompt_messages 表示提示消息列表。
        返回值：返回一个生成器，生成 LLM 响应块。
        """
        # 初始化 full_assistant_content 为空字符串，chunk_index 为 0，用于记录完整的助手内容和块索引。
        full_assistant_content = ''
        chunk_index = 0

        def create_final_llm_result_chunk(index: int, message: AssistantPromptMessage, finish_reason: str) \
                -> LLMResultChunk:
            # calculate num tokens
            prompt_tokens = self._num_tokens_from_string(model, prompt_messages[0].content)
            completion_tokens = self._num_tokens_from_string(model, full_assistant_content)

            # transform usage
            usage = self._calc_response_usage(model, credentials, prompt_tokens, completion_tokens)

            return LLMResultChunk(
                model=model,
                prompt_messages=prompt_messages,
                delta=LLMResultChunkDelta(
                    index=index,
                    message=message,
                    finish_reason=finish_reason,
                    usage=usage
                )
            )

        # delimiter for stream response, need unicode_escape
        import codecs
        delimiter = credentials.get("stream_mode_delimiter", "\n\n")
        delimiter = codecs.decode(delimiter, "unicode_escape")

        tools_calls: list[AssistantPromptMessage.ToolCall] = []

        def increase_tool_call(new_tool_calls: list[AssistantPromptMessage.ToolCall]):
            def get_tool_call(tool_call_id: str):
                if not tool_call_id:
                    return tools_calls[-1]

                tool_call = next((tool_call for tool_call in tools_calls if tool_call.id == tool_call_id), None)
                if tool_call is None:
                    tool_call = AssistantPromptMessage.ToolCall(
                        id=tool_call_id,
                        type="function",
                        function=AssistantPromptMessage.ToolCall.ToolCallFunction(
                            name="",
                            arguments=""
                        )
                    )
                    tools_calls.append(tool_call)

                return tool_call

            for new_tool_call in new_tool_calls:
                # get tool call
                tool_call = get_tool_call(new_tool_call.function.name)
                # update tool call
                if new_tool_call.id:
                    tool_call.id = new_tool_call.id
                if new_tool_call.type:
                    tool_call.type = new_tool_call.type
                if new_tool_call.function.name:
                    tool_call.function.name = new_tool_call.function.name
                if new_tool_call.function.arguments:
                    tool_call.function.arguments += new_tool_call.function.arguments

        finish_reason = 'Unknown'

        for chunk in response.iter_lines(decode_unicode=True, delimiter=delimiter):
            chunk = chunk.strip()
            if chunk:
                # ignore sse comments
                if chunk.startswith(':'):
                    continue
                decoded_chunk = chunk.strip().lstrip('data: ').lstrip()

                try:
                    chunk_json = json.loads(decoded_chunk)
                # stream ended
                except json.JSONDecodeError as e:
                    yield create_final_llm_result_chunk(
                        index=chunk_index + 1,
                        message=AssistantPromptMessage(content=""),
                        finish_reason="Non-JSON encountered."
                    )
                    break
                if not chunk_json or len(chunk_json['choices']) == 0:
                    continue

                choice = chunk_json['choices'][0]
                finish_reason = chunk_json['choices'][0].get('finish_reason')
                chunk_index += 1

                if 'delta' in choice:
                    delta = choice['delta']
                    delta_content = delta.get('content')

                    assistant_message_tool_calls = None

                    if 'tool_calls' in delta and credentials.get('function_calling_type', 'no_call') == 'tool_call':
                        assistant_message_tool_calls = delta.get('tool_calls', None)
                    elif 'function_call' in delta and credentials.get('function_calling_type',
                                                                      'no_call') == 'function_call':
                        assistant_message_tool_calls = [{
                            'id': 'tool_call_id',
                            'type': 'function',
                            'function': delta.get('function_call', {})
                        }]

                    # assistant_message_function_call = delta.delta.function_call

                    # extract tool calls from response
                    if assistant_message_tool_calls:
                        tool_calls = self._extract_response_tool_calls(assistant_message_tool_calls)
                        increase_tool_call(tool_calls)

                    if delta_content is None or delta_content == '':
                        continue

                    # transform assistant message to prompt message
                    assistant_prompt_message = AssistantPromptMessage(
                        content=delta_content,
                    )

                    # reset tool calls
                    tool_calls = []
                    full_assistant_content += delta_content
                elif 'text' in choice:
                    choice_text = choice.get('text', '')
                    if choice_text == '':
                        continue

                    # transform assistant message to prompt message
                    assistant_prompt_message = AssistantPromptMessage(content=choice_text)
                    full_assistant_content += choice_text
                else:
                    continue

                yield LLMResultChunk(
                    model=model,
                    prompt_messages=prompt_messages,
                    delta=LLMResultChunkDelta(
                        index=chunk_index,
                        message=assistant_prompt_message,
                    )
                )

            chunk_index += 1

        if tools_calls:
            yield LLMResultChunk(
                model=model,
                prompt_messages=prompt_messages,
                delta=LLMResultChunkDelta(
                    index=chunk_index,
                    message=AssistantPromptMessage(
                        tool_calls=tools_calls,
                        content=""
                    ),
                )
            )

        yield create_final_llm_result_chunk(
            index=chunk_index,
            message=AssistantPromptMessage(content=""),
            finish_reason=finish_reason
        )

    async def _async_handle_generate_stream_response(self, model: str, credentials: dict,
                                                     endpoint_url: str, headers: dict, data: dict,
                                                     prompt_messages: list[PromptMessage]) -> AsyncGenerator:
        """
        Handle llm stream response

        :param model: model name
        :param credentials: model credentials
        :param response: streamed response
        :param prompt_messages: prompt messages
        :return: llm response chunk generator
        """
        full_assistant_content = ''
        chunk_index = 0

        def create_final_llm_result_chunk(index: int, message: AssistantPromptMessage, finish_reason: str) \
                -> LLMResultChunk:
            # calculate num tokens
            prompt_tokens = self._num_tokens_from_string(model, prompt_messages[0].content)
            completion_tokens = self._num_tokens_from_string(model, full_assistant_content)

            # transform usage
            usage = self._calc_response_usage(model, credentials, prompt_tokens, completion_tokens)

            return LLMResultChunk(
                model=model,
                prompt_messages=prompt_messages,
                delta=LLMResultChunkDelta(
                    index=index,
                    message=message,
                    finish_reason=finish_reason,
                    usage=usage
                )
            )

        # delimiter for stream response, need unicode_escape
        import codecs
        delimiter = credentials.get("stream_mode_delimiter", "\n\n")
        delimiter = codecs.decode(delimiter, "unicode_escape")

        tools_calls: list[AssistantPromptMessage.ToolCall] = []

        def increase_tool_call(new_tool_calls: list[AssistantPromptMessage.ToolCall]):
            def get_tool_call(tool_call_id: str):
                if not tool_call_id:
                    return tools_calls[-1]

                tool_call = next((tool_call for tool_call in tools_calls if tool_call.id == tool_call_id), None)
                if tool_call is None:
                    tool_call = AssistantPromptMessage.ToolCall(
                        id=tool_call_id,
                        type="function",
                        function=AssistantPromptMessage.ToolCall.ToolCallFunction(
                            name="",
                            arguments=""
                        )
                    )
                    tools_calls.append(tool_call)

                return tool_call

            for new_tool_call in new_tool_calls:
                # get tool call
                tool_call = get_tool_call(new_tool_call.function.name)
                # update tool call
                if new_tool_call.id:
                    tool_call.id = new_tool_call.id
                if new_tool_call.type:
                    tool_call.type = new_tool_call.type
                if new_tool_call.function.name:
                    tool_call.function.name = new_tool_call.function.name
                if new_tool_call.function.arguments:
                    tool_call.function.arguments += new_tool_call.function.arguments

        finish_reason = 'Unknown'
        async with httpx.AsyncClient(timeout=10.0) as client:
            async with client.stream("POST", endpoint_url, headers=headers, json=data) as response:
                if response.encoding is None or response.encoding == 'ISO-8859-1':
                    response.encoding = 'utf-8'

                if response.status_code != 200:
                    raise InvokeError(
                        f"API request failed with status code {response.status_code}: {response.text}")
                async for chunk in helper.httpx_stream_aiter_lines(response=response, delimiter=delimiter):
                    chunk = chunk.strip()
                    if chunk:
                        # ignore sse comments
                        if chunk.startswith(':'):
                            continue
                        decoded_chunk = chunk.strip().lstrip('data: ').lstrip()

                        try:
                            chunk_json = json.loads(decoded_chunk)
                        # stream ended
                        except json.JSONDecodeError as e:
                            yield create_final_llm_result_chunk(
                                index=chunk_index + 1,
                                message=AssistantPromptMessage(content=""),
                                finish_reason="Non-JSON encountered."
                            )
                            break
                        if not chunk_json or len(chunk_json['choices']) == 0:
                            continue

                        choice = chunk_json['choices'][0]
                        finish_reason = chunk_json['choices'][0].get('finish_reason')
                        chunk_index += 1

                        if 'delta' in choice:
                            delta = choice['delta']
                            delta_content = delta.get('content')

                            assistant_message_tool_calls = None

                            if 'tool_calls' in delta and credentials.get('function_calling_type',
                                                                         'no_call') == 'tool_call':
                                assistant_message_tool_calls = delta.get('tool_calls', None)
                            elif 'function_call' in delta and credentials.get('function_calling_type',
                                                                              'no_call') == 'function_call':
                                assistant_message_tool_calls = [{
                                    'id': 'tool_call_id',
                                    'type': 'function',
                                    'function': delta.get('function_call', {})
                                }]

                            # assistant_message_function_call = delta.delta.function_call

                            # extract tool calls from response
                            if assistant_message_tool_calls:
                                tool_calls = self._extract_response_tool_calls(assistant_message_tool_calls)
                                increase_tool_call(tool_calls)

                            if delta_content is None or delta_content == '':
                                continue

                            # transform assistant message to prompt message
                            assistant_prompt_message = AssistantPromptMessage(
                                content=delta_content,
                            )

                            # reset tool calls
                            tool_calls = []
                            full_assistant_content += delta_content
                        elif 'text' in choice:
                            choice_text = choice.get('text', '')
                            if choice_text == '':
                                continue

                            # transform assistant message to prompt message
                            assistant_prompt_message = AssistantPromptMessage(content=choice_text)
                            full_assistant_content += choice_text
                        else:
                            continue

                        yield LLMResultChunk(
                            model=model,
                            prompt_messages=prompt_messages,
                            delta=LLMResultChunkDelta(
                                index=chunk_index,
                                message=assistant_prompt_message,
                            )
                        )

                    chunk_index += 1

        if tools_calls:
            yield LLMResultChunk(
                model=model,
                prompt_messages=prompt_messages,
                delta=LLMResultChunkDelta(
                    index=chunk_index,
                    message=AssistantPromptMessage(
                        tool_calls=tools_calls,
                        content=""
                    ),
                )
            )

        yield create_final_llm_result_chunk(
            index=chunk_index,
            message=AssistantPromptMessage(content=""),
            finish_reason=finish_reason
        )

    def _handle_generate_response(self, model: str, credentials: dict, response: requests.Response,
                                  prompt_messages: list[PromptMessage]) -> LLMResult:
        response_json = response.json()

        completion_type = LLMMode.value_of(credentials['mode'])

        output = response_json['choices'][0]

        response_content = ''

        tool_calls = None

        function_calling_type = credentials.get("function_calling_type", 'no_call')
        if completion_type is LLMMode.CHAT:
            response_content = output.get('message', {})['content']
            if function_calling_type == 'tool_call':
                tool_calls = output.get('message', {}).get('tool_calls')
            elif function_calling_type == 'function_call':
                tool_calls = output.get('message', {}).get('function_call')
        elif completion_type is LLMMode.COMPLETION:
            response_content = output['text']

        assistant_message = AssistantPromptMessage(content=response_content, tools_calls=[])

        if tool_calls:
            # 需要将对应的工具/函数调用拼接到 AssistantPromptMessage 中
            if function_calling_type == 'tool_call':
                assistant_message.tool_calls = self._extract_response_tool_calls(tool_calls)
            elif function_calling_type == 'function_call':
                assistant_message.tool_calls = [self._extract_response_function_call(tool_calls)]

        usage = response_json.get('usage')
        if usage:
            prompt_tokens = usage["prompt_tokens"]
            completion_tokens = usage["completion_tokens"]
        else:
            # calculate num tokens
            prompt_tokens = self._num_tokens_from_string(model, prompt_messages[0].content)
            completion_tokens = self._num_tokens_from_string(model, assistant_message.content)

        # transform usage
        usage = self._calc_response_usage(model, credentials, prompt_tokens, completion_tokens)

        # transform response
        result = LLMResult(
            model=response_json["model"],
            prompt_messages=prompt_messages,
            message=assistant_message,
            usage=usage,
        )

        return result

    def _num_tokens_from_string(self, model: str, text: Union[str, list[PromptMessageContent]],
                                tools: Optional[list[PromptMessageTool]] = None) -> int:
        """
        功能：使用 GPT-2 分词器近似计算模型的令牌数量。
        参数：model 表示模型名称，text 表示提示文本，tools 表示工具列表。
        返回值：返回令牌的数量。
        """
        if isinstance(text, str):
            full_text = text
        else:
            full_text = ''
            for message_content in text:
                if message_content.type == PromptMessageContentType.TEXT:
                    message_content = cast(PromptMessageContent, message_content)
                    full_text += message_content.data

        num_tokens = self._get_num_tokens_by_gpt2(full_text)

        if tools:
            num_tokens += self._get_num_tokens_for_tools(tools)

        return num_tokens

    def _get_num_tokens_for_tools(self, tools: list[PromptMessageTool]) -> int:
        """
        功能：使用 tiktoken 包计算工具调用所需的令牌数量。
        参数：tools 表示用于工具调用的工具列表。
        返回值：返回令牌的数量。
        """

        num_tokens = 0
        for tool in tools:
            num_tokens += self._get_num_tokens_by_gpt2('type')
            num_tokens += self._get_num_tokens_by_gpt2('function')
            num_tokens += self._get_num_tokens_by_gpt2('function')

            # calculate num tokens for function object
            num_tokens += self._get_num_tokens_by_gpt2('name')
            num_tokens += self._get_num_tokens_by_gpt2(tool.name)
            num_tokens += self._get_num_tokens_by_gpt2('description')
            num_tokens += self._get_num_tokens_by_gpt2(tool.description)
            parameters = tool.parameters
            num_tokens += self._get_num_tokens_by_gpt2('parameters')
            if 'title' in parameters:
                num_tokens += self._get_num_tokens_by_gpt2('title')
                num_tokens += self._get_num_tokens_by_gpt2(parameters.get("title"))
            num_tokens += self._get_num_tokens_by_gpt2('type')
            num_tokens += self._get_num_tokens_by_gpt2(parameters.get("type"))
            if 'properties' in parameters:
                num_tokens += self._get_num_tokens_by_gpt2('properties')
                for key, value in parameters.get('properties').items():
                    num_tokens += self._get_num_tokens_by_gpt2(key)
                    for field_key, field_value in value.items():
                        num_tokens += self._get_num_tokens_by_gpt2(field_key)
                        if field_key == 'enum':
                            for enum_field in field_value:
                                num_tokens += 3
                                num_tokens += self._get_num_tokens_by_gpt2(enum_field)
                        else:
                            num_tokens += self._get_num_tokens_by_gpt2(field_key)
                            num_tokens += self._get_num_tokens_by_gpt2(str(field_value))
            if 'required' in parameters:
                num_tokens += self._get_num_tokens_by_gpt2('required')
                for required_field in parameters['required']:
                    num_tokens += 3
                    num_tokens += self._get_num_tokens_by_gpt2(required_field)

        return num_tokens

    def _extract_response_tool_calls(self, response_tool_calls: list[dict]) -> list[AssistantPromptMessage.ToolCall]:
        """
        功能：从响应中提取工具调用。
        参数：response_tool_calls 表示响应中的工具调用列表。
        返回值：返回一个工具调用对象的列表 list[AssistantPromptMessage.ToolCall] 。
        """
        tool_calls = []
        if response_tool_calls:
            for response_tool_call in response_tool_calls:
                function = AssistantPromptMessage.ToolCall.ToolCallFunction(
                    name=response_tool_call.get('function', {}).get('name', ''),
                    arguments=response_tool_call.get('function', {}).get('arguments', '')
                )

                tool_call = AssistantPromptMessage.ToolCall(
                    id=response_tool_call.get('id', ''),
                    type=response_tool_call.get('type', ''),
                    function=function
                )
                tool_calls.append(tool_call)
        return tool_calls

    def _extract_response_function_call(self, response_function_call) -> AssistantPromptMessage.ToolCall:
        """
        功能：从响应中提取函数调用。
        参数：response_function_call 表示响应中的函数调用。
        返回值：返回一个工具调用对象 AssistantPromptMessage.ToolCall。
        """
        tool_call = None
        if response_function_call:
            function = AssistantPromptMessage.ToolCall.ToolCallFunction(
                name=response_function_call.get('name', ''),
                arguments=response_function_call.get('arguments', '')
            )
            tool_call = AssistantPromptMessage.ToolCall(
                id=response_function_call.get('id', ''),
                type='function',
                function=function
            )

        return tool_call

    def _convert_prompt_message_to_dict(self, message: PromptMessage, credentials: Optional[dict] = None) -> dict:
        """
        将 PromptMessage 转换为 QiMing API 所支持的字典格式
        """

        # 处理用户 Prompt
        if isinstance(message, UserPromptMessage):
            message = cast(UserPromptMessage, message)
            if isinstance(message.content, str):
                message_dict = {"role": "user", "content": message.content}
            else:
                sub_messages = []
                for message_content in message.content:
                    # 如果当前类型为 TEXT
                    if message_content.type == PromptMessageContentType.TEXT:
                        message_content = cast(PromptMessageContent, message_content)
                        sub_message_dict = {
                            "type": "text",
                            "text": message_content.data
                        }
                        sub_messages.append(sub_message_dict)
                    elif message_content.type == PromptMessageContentType.IMAGE:
                        message_content = cast(ImagePromptMessageContent, message_content)
                        sub_message_dict = {
                            "type": "image_url",
                            "image_url": {
                                "url": message_content.data,
                                "detail": message_content.detail.value
                            }
                        }
                        sub_messages.append(sub_message_dict)
                message_dict = {"role": "user", "content": sub_messages}
        # 处理 AssistantPrompt
        elif isinstance(message, AssistantPromptMessage):
            message = cast(AssistantPromptMessage, message)
            message_dict = {"role": "assistant", "content": message.content}
            # 如果具有工具调用能力
            if message.tool_calls:
                function_call = message.tool_calls[0]
                message_dict["function_call"] = {
                    "name": function_call.function.name,
                    "args": function_call.function.arguments
                }
        # 处理 SystemPrompt
        elif isinstance(message, SystemPromptMessage):
            message = cast(SystemPromptMessage, message)
            message_dict = {"role": "system", "content": message.content}
        # 处理 ToolPrompt
        elif isinstance(message, ToolPromptMessage):
            message = cast(ToolPromptMessage, message)
            message_dict = {
                "role": "tool" if credentials and credentials.get("function_calling_type",
                                                                  "no_call") == 'tool_call' else "function",
                "content": message.content,
                "name": message.tool_call_id
            }
        else:
            raise ValueError(f"Got unknown type {message}")

        if message.name:
            message_dict["name"] = message.name
        return message_dict
