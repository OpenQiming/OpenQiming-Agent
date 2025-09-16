import json
import logging
import re
from collections.abc import Generator
from typing import Union

from agent_platform_core.agent.entities import AgentScratchpadUnit, AgentScratchpadUnitllama
from agent_platform_core.model_runtime.entities.llm_entities import LLMResultChunk
logger = logging.getLogger(__name__)

class LlamaAgentOutputParser:
    @classmethod
    def handle_react_stream_output(cls, llm_response: Generator[LLMResultChunk, None, None], usage_dict: dict) -> \
            Generator[Union[str, AgentScratchpadUnit.Action], None, None]:

        def parse_llama_func_response(response: str):
            # 定义正则表达式，匹配函数名和参数
            function_regex = r"<function=([\w\s]+)>(.*?)</function>"  # TODO rm '\s' after modifing prompt
            match = re.search(function_regex, response)
            if match:
                # 提取函数名和参数字符串
                function_name, args_string = match.groups()
                try:
                    # TODO temporary solution here:
                    args = json.loads(args_string) if args_string != '' else json.loads('{}')
                    # TODO PROBLEM to be solved， json decoding error with {{ }}
                    return AgentScratchpadUnitllama.Action(
                        action_name=function_name,
                        action_input=args,
                        function_res=response,
                    )
                except json.JSONDecodeError as error:
                    logging.error(error)
                    return AgentScratchpadUnitllama.Action(
                        action_name=function_name,
                        action_input=args_string,
                        function_res=response,
                    )
            return None

        def extra_json_from_code_block(code_block) -> Generator[Union[dict, str], None, None]:
            # 从代码块中提取 JSON 的内部方法
            # 匹配所有用 ``` 包围的代码块
            code_blocks = re.findall(r'```(.*?)```', code_block, re.DOTALL)
            if not code_blocks:
                return
            for block in code_blocks:
                json_text = re.sub(r'^[a-zA-Z]+\n', '', block.strip(), flags=re.MULTILINE)
                yield json_text

        def words_comparison(delta, words_str, words_cache_dic, d):
            # 比较响应中的文本和指定词汇是否匹配成功
            if delta[:d].lower() == words_str[
                                    len(words_cache_dic[words_str]):len(words_cache_dic[words_str]) + len(delta)]:
                # 如果匹配，将匹配的部分添加到缓存
                words_cache_dic[words_str] += delta[:d]
                return True
            else:
                return False

        def first_char_case(delta, cached_dic):
            # 处理响应中第一个字符的内部方法
            if not cached_dic:  # 如果缓存字典为空
                if delta[0] in ['\n', ' ']:  # 如果 delta 以换行符或空格开头
                    return delta[1:] or delta  # 跳过第一个字符返回
                return delta  # 返回 delta
            else:
                return delta  # 如果缓存字典不为空，直接返回 delta

        def hide_words(words_cache_dic: dict, delta):
            # 递归隐藏特定词汇的内部方法
            for words_str in words_cache_dic.keys():  # 遍历缓存字典中的每个词汇
                # base case
                if delta == '':
                    # print('case0')
                    return ''
                # delta = first_char_case(delta, words_cache_dic[words_str])
                d = len(words_str) - len(words_cache_dic[words_str])  # 计算剩余的匹配长度
                # check if there is ‘ ’ before：  #TODO use search first?
                if words_comparison(delta, words_str, words_cache_dic, d):  # 如果 delta 与词汇匹配
                    if words_cache_dic[words_str].lower() == words_str:  # 如果词汇完全匹配
                        words_cache_dic[words_str] = ''  # 清空缓存中的词汇
                    return hide_words({words_str: words_cache_dic[words_str]}, delta[d:])  # 递归处理剩余的 delta
                # print('case2')
                if words_cache_dic[words_str]:  # 如果缓存中有词汇
                    delta = words_cache_dic[words_str] + delta  # 将缓存词汇拼接到 delta
                    words_cache_dic[words_str] = ''  # 清空缓存
            return delta

        def llama_func_pass(llama_func_left_str, llama_func_right_str, llama_func_dic, delta):
            # base case
            # 检查函数调用起止符并解析
            if delta == '':
                return ''
            delta = first_char_case(delta, llama_func_dic['working'])
            # 如果不在函数内部
            if not llama_func_dic['in_func']:
                # waiting for left first
                # 计算剩余的匹配长度
                d = len(llama_func_left_str) - len(llama_func_dic[llama_func_left_str])
                # # 如果匹配到函数左边界
                if words_comparison(delta, llama_func_left_str, llama_func_dic, d):
                    # 设置工作标志为 True
                    llama_func_dic['working'] = True
                    if llama_func_dic[llama_func_left_str].lower() == llama_func_left_str:
                        # print('case1')
                        llama_func_dic['in_func'] = True
                        llama_func_dic['complete'] = False
                    return llama_func_pass(llama_func_left_str, llama_func_right_str, llama_func_dic, delta[d:])


            else:
                # in_func begin
                # 如果已经在函数内部
                llama_func_dic['inside_func'] += delta  # 将 delta 添加到函数内部内容中
                if llama_func_right_str in llama_func_dic['inside_func']:  # 如果找到函数右边界
                    llama_func_dic['function'] = llama_func_left_str + llama_func_dic['inside_func']
                    llama_func_dic['complete'] = True
                    llama_func_dic[llama_func_left_str] = ''
                    llama_func_dic[llama_func_right_str] = ''
                    llama_func_dic['inside_func'] = ''
                    llama_func_dic['working'] = False
                    llama_func_dic['in_func'] = False
                    # llama_func_right_str
                    d = delta.find('>')+1
                    return llama_func_pass(llama_func_left_str, llama_func_right_str, llama_func_dic, delta[d:])
            # elif not llama_func_dic['complete']:
            #     # pass everything into func:
            #     d = len(llama_func_right_str) - len(llama_func_dic[llama_func_right_str])
            #     if words_comparison(delta, llama_func_right_str, llama_func_dic, d):
            #         # if right begin:
            #         if llama_func_dic[llama_func_right_str].lower() == llama_func_right_str:
            #             llama_func_dic['function'] = llama_func_left_str + llama_func_dic[
            #                 llama_inside_func_str] + llama_func_right_str
            #             llama_func_dic['complete'] = True
            #             llama_func_dic[llama_func_left_str] = ''
            #             llama_func_dic[llama_func_right_str] = ''
            #             llama_func_dic[llama_inside_func_str] = ''
            #             llama_func_dic['working'] = False
            #             llama_func_dic['in_func'] = False
            #         return llama_func_pass(llama_func_left_str, llama_func_right_str, llama_func_dic, delta[d:])
            #     else:
            #         if not llama_func_dic[llama_func_right_str]:
            #             llama_func_dic[llama_inside_func_str] += delta
            #         else:
            #             llama_func_dic['complete'] = False
            #             llama_func_dic['working'] = False
            #             llama_func_dic[llama_func_left_str] = ''
            #             llama_func_dic[llama_func_right_str] = ''
            #             llama_func_dic[llama_inside_func_str] = ''
            #             llama_func_dic['in_func'] = False

        def llama_code_pass(llama_code_indicator_str, llama_code_dic, delta):
            # base case
            if delta == '':
                return ''
            delta = first_char_case(delta, llama_code_dic['working'])
            d = len(llama_code_indicator_str) - len(llama_code_dic[llama_code_indicator_str])
            if words_comparison(delta, llama_code_indicator_str, llama_code_dic, d):
                # indicator matched
                llama_code_dic['working'] = True
                if llama_code_dic[llama_code_indicator_str].lower() == llama_code_indicator_str:
                    # print('case1')
                    llama_code_dic['full_code'] += llama_code_indicator_str
                    llama_code_dic[llama_code_indicator_str] = ''
                    llama_code_dic['in_code'] += 1
                return llama_code_pass(llama_code_indicator_str, llama_code_dic, delta[d:])

            if llama_code_dic['in_code'] == 1:
                llama_code_dic['full_code'] += delta
            elif llama_code_dic['in_code'] == 2:
                # llama_code_dic['full_code'] += llama_code_indicator_str
                llama_code_dic['complete'] = True
                llama_code_dic['in_code'] = 0
            else:
                llama_code_dic['working'] = False
                delta = llama_code_dic[llama_code_indicator_str] + delta if llama_code_dic[
                    llama_code_indicator_str] else delta
                # TODO catch error if llm's respondes are ridiculous... ( especially for in_code situation here)
                llama_code_dic[llama_code_indicator_str] = ''
                # return delta

                # return llama_code_pass(llama_code_indicator_str, llama_code_dic, delta[d:])  #TODO check here
        # check llama function call
        llama_func_left_str = "<function="  # followed by >
        llama_func_right_str = "</function>"
        llama_inside_func_str = 'inside_func'
        llama_func_dic = {llama_func_left_str: '', llama_func_right_str: '', llama_inside_func_str: '',
                          'in_func': False, 'function': '', 'working': False, 'complete': False}
        # check llama code-python
        llama_code_indicator_str = "```"
        # llama_code_type_str = "python"
        llama_inside_code_str = 'inside_code'
        llama_code_dic = {llama_code_indicator_str: '', llama_inside_code_str: '', 'in_code': 0, 'full_code': '',
                          'complete': False, 'working': False}

        action_str = 'action:'
        thought_str = 'thought:'
        hide_words_cache_dic = {action_str: '', thought_str: ''}

        for response in llm_response:
            if response.delta.usage:
                usage_dict['usage'] = response.delta.usage
            response = response.delta.message.content
            logger.debug(response)
            if not isinstance(response, str):
                continue

            _ = llama_func_pass(llama_func_left_str, llama_func_right_str, llama_func_dic, response)
            _ = llama_code_pass(llama_code_indicator_str, llama_code_dic, response)
            if llama_func_dic['complete']:
                if not parse_llama_func_response(llama_func_dic['function']):
                    pass

                yield parse_llama_func_response(llama_func_dic['function'])
                llama_func_dic['function'] = ''
                llama_func_dic['complete'] = False
                continue
                # print("function gotcha: ", llama_func_dic['function'])
            elif llama_code_dic['complete']:
                yield extra_json_from_code_block(llama_code_dic['full_code'])
                llama_code_dic['full_code'] = ''
                llama_code_dic['complete'] = False
                continue
                # print("code gotcha: ", llama_code_dic['full_code'])
            if not llama_func_dic['working'] and not llama_func_dic['working']:
                delta = hide_words(hide_words_cache_dic, response)
                if delta:
                    yield delta
                    continue
                    # print(delta)
