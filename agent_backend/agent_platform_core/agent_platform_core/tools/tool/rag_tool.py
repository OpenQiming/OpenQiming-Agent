import json
from copy import deepcopy

import httpx

from agent_platform_core.tools.tool.tool import Tool
from agent_platform_core.helper import async_ssrf_proxy
from agent_platform_core.tools.entities.tool_entities import ToolInvokeMessage, ToolParameter, ToolProviderType
from agent_platform_common.configs import agent_platform_config
from typing import Any, Union, Optional
import logging
from enum import Enum

class RAGSceneType(Enum):
    # RAG 场景类型
    knowledge_assistant_maintenance = 2  # 综维知识助手
    knowledge_assistant_network = 3  # 无线网优知识助手
    knowledge_assistant_installation = 7  # 装维知识助手
    knowledge_assistant_rule = 8  # 规章制度助手
    knowledge_assistant_pass = 9  # IT运维知识助手
    disposal_assistant_wireless_fault = 11  # 无线故障处置助手
    knowledge_tongyi = 13  # 统一/通用知识助手

class RagTool(Tool):
    
    """
    Rag tool.
    """
    query: Optional[str] = ""
    kb_id: Optional[str] = ""

    def __init__(self, query: str, kb_id: str, **data: Any):
        super().__init__(**data)
        self.query = query
        self.kb_id = kb_id
    
    def tool_provider_type(self) -> ToolProviderType:
        """
        get the tool provider type

        :return: the tool provider type
        """
        return ToolProviderType.RAG

    def _invoke(
            self, user_id: str, tool_parameters: dict[str, Any]
    ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        pass

    async def _async_invoke(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        BASE_KNOWLEDGE_API_ENDPOINT = agent_platform_config.BASE_KNOWLEDGE_API_ENDPOINT
        RAG_URL = BASE_KNOWLEDGE_API_ENDPOINT + "/know_query"

        print("user_id:::", user_id, tool_parameters)
        print("model_config:::", self.model_config)
        print("tenant_id:::", self.runtime.tenant_id)
        print("self.runtime.runtime_parameters::::", self.runtime.runtime_parameters)
        print("query:::2", self.runtime.runtime_parameters.get("query", ""))
        print("self.kb_id:::", self.kb_id)
        print("self.query:::", self.query)



        rag_headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        # 用户id
        knowledge_pload = {
            "tenant_id": self.runtime.tenant_id,
            "kb_id": self.kb_id,
            "query": self.query,
            "top_k": 2,  # 默认使用
            "area": "app"
        }

        try:
            logging.info("rag-http-request => url:{} knowledge_pload: {}"
                         .format(RAG_URL, knowledge_pload))

            async with httpx.AsyncClient() as client:
                response = await client.post(RAG_URL, headers=rag_headers, json=knowledge_pload,timeout=60)
                response_json = response.json()
            logging.info("response => {}".format(response_json))

        except Exception as e:
            logging.exception(e)
            raise ValueError(f"RAG REQUEST ERROR ,PLEASE TRY AGAIN")

        outputs = response_json['answers']

        result = []

        for o in outputs:
            result.append(self.create_text_message(json.dumps(o, ensure_ascii=False)))
            result.append(self.create_json_message(o))

        return result


    # 丢弃
    async def _async_invoke_b(self, user_id: str, tool_parameters: dict[str, Any]) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        RAG_INTERFACE_ENDPOINT = agent_platform_config.RAG_INTERFACE_ENDPOINT
        RAG_AGENT_SERVICE = agent_platform_config.RAG_AGENT_SERVICE

        RAG_URL = f'{RAG_INTERFACE_ENDPOINT}/{RAG_AGENT_SERVICE}/rest/bm/query/kg/trag'
        RAG_PROVS_URL = f'{RAG_INTERFACE_ENDPOINT}/{RAG_AGENT_SERVICE}/rest/bm/query/kg/new/trag'
        RAG_TAG_URL = f'{RAG_INTERFACE_ENDPOINT}/{RAG_AGENT_SERVICE}/rest/wsc/getBigModelLabels'
        """
        invoke the rag
        """

        query = tool_parameters.get("query")
        user_select = tool_parameters.get("scene")
        params = tool_parameters.get("params")

        if any(user_select == str(member.value) for member in RAGSceneType):
            big_model_label = RAGSceneType(int(user_select)).name  # 获取场景标签
        else:
            big_model_label = user_select

        province_code = tool_parameters.get("prov")
        # job_type_name = tool_parameters.get("job_type_name")

        rag_tag_headers = {
            "Content-Type": "application/json",
            "X-APP-ID": agent_platform_config.ASSISTANT_RAG_TAG_X_APP_ID,
            "X-APP-KEY": agent_platform_config.ASSISTANT_RAG_TAG_X_APP_KEY
        }

        tag_pload = {
            "bigModelLabel": big_model_label,
            "provinceCode": province_code
        }

        if user_select == str(RAGSceneType.knowledge_assistant_pass.value) or user_select == str(RAGSceneType.knowledge_tongyi.value):
            tag_pload['bigModelLabel'] += "_" + params

        try:
            logging.info("rag-tag-http-request => url:{} headers:{}, tag_pload: {}"
                         .format(self.RAG_TAG_URL, rag_tag_headers, tag_pload))
            response = await getattr(async_ssrf_proxy, "post")(
                self.RAG_TAG_URL,
                json=tag_pload,
                headers=rag_tag_headers,
            )
        except Exception as e:
            logging.exception(e)
            raise ValueError(f"Get RAG TAG ERROR ,PLEASE TRY AGAIN")

        response_json = response.json()
        logging.info(response_json)
        rag_tag = response_json['data']

        rag_headers = {
            "Content-Type": "application/json",
            "X-APP-ID": agent_platform_config.ASSISTANT_RAG_X_APP_ID,
            "X-APP-KEY": agent_platform_config.ASSISTANT_RAG_X_APP_KEY
        }

        knowledge_pload = {
            "query": query,
            "tag": rag_tag,
            "top_k": 3,
            "score_threshold": 0.5
        }

        try:
            logging.info("rag-http-request => url:{} headers:{}, knowledge_pload: {}"
                         .format(self.RAG_PROVS_URL, rag_headers, knowledge_pload))
            response = await getattr(async_ssrf_proxy, "post")(
                self.RAG_PROVS_URL,
                json=knowledge_pload,
                headers=rag_headers,
            )
        except Exception as e:
            logging.exception(e)
            raise ValueError(f"RAG REQUEST ERROR ,PLEASE TRY AGAIN")

        response_json = response.json()
        logging.info("response => {}".format(response_json))

        outputs={
                'output': response_json['data']['context'],
        }

        # outputs= '''
        #     以下是关于日本动画《鬼灭之刃》的详细信息整理：
        #
        #     核心设定
        #     ‌故事背景‌
        #     日本大正时期，卖炭少年灶门炭治郎因家人被恶鬼杀害，唯一存活的妹妹祢豆子也变成鬼。为寻找让妹妹恢复人类的方法，炭治郎加入专门猎杀恶鬼的组织「鬼杀队」15。
        #     ‌核心冲突‌
        #     人与鬼的对抗，炭治郎与伙伴们（善逸、伊之助等）共同对抗鬼之始祖鬼舞辻无惨38。
        #     动画系列结构
        #     ‌篇章名称‌	‌播出时间‌	‌集数/形式‌	‌备注‌
        #     灶门炭治郎 立志篇	2019年4月6日	TV动画26集	首季剧情，炭治郎加入鬼杀队6
        #     无限列车篇	2020年10月16日	剧场版动画	承接立志篇，炎柱牺牲主线6
        #     游郭篇	2021年12月5日	TV动画11集	音柱与上弦之陆对战6
        #     刀匠村篇	2023年4月9日	TV动画11集	霞柱与恋柱的锻刀村之战6
        #     柱训练篇	2024年5月12日	TV动画8集	鬼杀队全员特训备战6
        #     ‌无限城篇‌	‌2025年7月18日‌	‌剧场版动画（待映）‌	最终决战篇46
        #     主要角色与声优
        #     ‌灶门炭治郎‌（CV：花江夏树）
        #     主角，以水之呼吸与日轮刀战斗，嗅觉敏锐58。
        #     ‌灶门祢豆子‌（CV：鬼头明里）
        #     炭治郎之妹，虽化鬼仍保留人性，可通过睡眠恢复体力8。
        #     ‌我妻善逸‌（CV：下野纮）
        #     雷之呼吸传人，胆小但睡梦中战斗力爆发58。
        #     观看渠道
        #     ‌正版平台‌
        #     中国大陆可在B站观看高清全集（含未删减版），评分9.7/1078。
        #     ‌剧场版追踪‌
        #     《无限城篇》将于2025年7月18日在日本首映46。
        #     该系列改编自吾峠呼世晴的同名漫画，由ufotable制作，全球播放量超10亿，被誉“现象级热血番”
        # '''

        # assemble invoke message
        return self.create_text_message(outputs)

    def fork_tool_runtime(self, runtime: dict[str, Any]) -> 'RagTool':
        """
        fork a new tool with meta data

        :param meta: the meta data of a tool call processing, tenant_id is required
        :return: the new tool
        """
        return self.__class__(
            identity=deepcopy(self.identity),
            parameters=deepcopy(self.parameters),
            description=deepcopy(self.description),
            runtime=Tool.Runtime(**runtime),
            query=self.query,
            kb_id=self.kb_id
        )

 