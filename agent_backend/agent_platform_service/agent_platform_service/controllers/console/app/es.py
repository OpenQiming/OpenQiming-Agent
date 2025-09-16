from agent_platform_service.controllers.console import console_api
from fastapi import Query
from elasticsearch import Elasticsearch
from typing import Optional
import logging
from agent_platform_common.configs import agent_platform_config


@console_api.get("/es_query")
async def es_query(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    app_name: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),  # ISO 格式时间：2024-01-01 00:00:00
    end_time: Optional[str] = Query(None)
    ):
    logging.info(f"参数：page:{page}, page_size:{page_size}, app_name:{app_name}, start_time:{start_time}, end_time:{end_time}")
    from_ = (page - 1) * page_size

    # 构造 ES bool 查询
    must_clauses = []

    if app_name:
        must_clauses.append({
            "term": {
              "svcName": app_name
            }
        })

    if start_time or end_time:
        range_query = {}
        if start_time:
            range_query["gte"] = start_time
        if end_time:
            range_query["lte"] = end_time

        must_clauses.append({
            "range": {
                "createTime": range_query
            }
        })
    ip = agent_platform_config.HOST_IP
    query = {
        "bool": {
            "must": must_clauses,
            "filter": [
                {
                    "match_phrase": {
                        "deptId": "18945"
                    }
                },
                {
                    "match_phrase": {
                        "ip": ip
                    }
                }
            ]
        }
    }

    a = {
        "from": from_,
        "size": page_size,
        "query": query,
        "sort": [{"createTime": "desc"}]  # 默认按时间倒序
    }
    logging.info(f"query:{a}")

    # 执行搜索
    es_ip = agent_platform_config.ES_IP
    es_index = agent_platform_config.ES_INDEX
    es_user = agent_platform_config.ES_USER
    es_password = agent_platform_config.ES_PASSWORD

    es_ip = es_ip.split(",")
    es = Elasticsearch(
        hosts=es_ip,      # ES 地址，支持数组形式
        basic_auth=(es_user, es_password),   # 若未启用安全，可删掉 basic_auth
        request_timeout=30,  # 超时秒数，可选
        verify_certs=False,  # 如果是自签名证书
        ssl_show_warn=False,
        # headers={"Accept": "application/vnd.elasticsearch+json; compatible-with=8"},
        meta_header=False
    )
    # 禁用自动发送x-elastic-client-meta头)                    # 超时秒数，可选
    res = es.search(
    index = es_index,
    body = {
            "from": from_,
            "size": page_size,
            "query": query,
            "sort": [{"createTime": "desc"}]  # 默认按时间倒序
        }
    )

    total = res["hits"]["total"]["value"]
    results = [hit["_source"] for hit in res["hits"]["hits"]]


    result = []
    for hit in res["hits"]["hits"]:
        _source = hit["_source"]
        r = {
            "id": hit["_id"],
            "question": _source["question"],
            "answer": _source["answer"],
            "createTime": _source["createTime"],
            "hostIp": _source["ip"],
            "agentName": _source["svcName"],
        }
        result.append(r)


    return {
        "total": total,
        "code": 0,
        "data": results,
        "status": "successful"
    }
