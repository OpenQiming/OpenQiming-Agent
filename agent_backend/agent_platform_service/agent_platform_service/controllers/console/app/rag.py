# @Author: Yutong Wang
from typing import List

import httpx
from fastapi import Depends, Form
import json

from agent_platform_service.services.auth_service import login_user
from agent_platform_basic.models.db_model import AccountIntegrate, InvitationCode, Account
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.helper import async_ssrf_proxy
from agent_platform_service.controllers.console import console_api
from fastapi import FastAPI, File, UploadFile, HTTPException
import logging
# from agent_platform_service.fastapi_fields.req.console.rag_req import UploadFileForRagReq
import os
import uuid

uuid_namespace = uuid.NAMESPACE_URL

# # 查询场景编号字典接口
# @console_api.get("/check-assistant-code")
# async def check_assistant_code(name: str):
#     logging.info(f"查询场景编号字典接口，name: {name}")
#     print(f"查询场景编号字典接口，name: {name}")
#     data = await get_assistant_list(name)
#     print(data)
#     # if code in data:
#     #     return data[code] == name
#     # else:
#     #     return False
#     # logging.info("查询成功", data)
#     return data

# 1.创建知识库
@console_api.post("/kb_create")
async def kb_create(request: dict, account: Account = Depends(login_user)):
    try:
        kb_name = request.get("kb_name","")
        kb_desc = request.get("kb_desc", "")
        kb_icon = request.get("kb_icon", "")
        tenant_id = request.get("tenant_id", "")
        logging.info("tenant_id of kb_create: %s", tenant_id)
        tenant_id = tenant_id or account.current_tenant_id
        user_name = account.name
        if not(kb_name or kb_icon):
            raise HTTPException(status_code=400, detail="缺少必传参数")

        headers = {
            'accept': 'application/json'
        }

        data = {
            "kb_name": kb_name,
            "kb_desc": kb_desc,
            "kb_icon": kb_icon,
            "tenant_id": tenant_id,
            "user_name": user_name
         }

        RAG_KB_CREATE_URL = agent_platform_config.BASE_KNOWLEDGE_API_ENDPOINT + "/kb_create"
        # return {
        #   "kb_name": "123",
        #   "kb_id": "123",
        #   "status": "true"
        # }
        async with httpx.AsyncClient() as client:
            response = await client.post(RAG_KB_CREATE_URL, headers=headers, json=data)
            print(response.content)
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Failed to upload file to the other API: {response.text}")

            return response.json()
    except Exception as e:
        logging.error(f"知识库创建过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="知识库创建失败")


# 2.用户名下知识库查询
@console_api.post("/kb_list")
async def kb_list(request: dict, account: Account = Depends(login_user)):
    try:
        tenant_id = request.get("tenant_id", "")
        logging.info("tenant_id of kb_list: %s", tenant_id)
        tenant_id = tenant_id or account.current_tenant_id

        headers = {
            'accept': 'application/json'
        }

        data = {
            "tenant_id": tenant_id
        }

        RAG_KB_LIST_URL = agent_platform_config.BASE_KNOWLEDGE_API_ENDPOINT + "/kb_list"
        # RAG_KB_LIST_URL = "http://172.27.221.54:8002/kb_list"

    #     return {"kb_list": [  {
    #   "kb_name": "123",
    #   "kb_id": "123",
    #   "creator": "qqq",
    #   "kb_desc": "asdassafd",
    #   "creation_time": "2025-02-20 10:00:00",
    #   "update_time": "2025-02-21 15:30:00"
    # }], "status": "successful"}
        async with httpx.AsyncClient() as client:
            response = await client.post(RAG_KB_LIST_URL, headers=headers, json=data)

            if response.status_code != 200:
                print(f"知识库列表查询失败: {response.text}")
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Failed to list kb to the other API: {response.text}")

            return response.json()
    except HTTPException as e:
        print(f"知识库列表查询过程中发生错误: {e.with_traceback()}")
        raise e
    except Exception as e:
        logging.error(f"知识库列表查询过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="知识库列表查询")


# 3.用户名下知识库文件查询
@console_api.post("/kb_file_list")
async def kb_file_list(request: dict, account: Account = Depends(login_user)):
    try:
        # kb_id = request.get("kb_id", "")
        headers = {
            'accept': 'application/json'
        }

        data = {
            "kb_id": request.get("kb_id","")
        }

        RAG_KB_LIST_FILES_URL = agent_platform_config.BASE_KNOWLEDGE_API_ENDPOINT + "/kb_file_list"

        # return {"kb_file_list": ["文档1.doc", "文档2.pdf"], "status":"successful"}

        async with httpx.AsyncClient() as client:
            response = await client.post(RAG_KB_LIST_FILES_URL, headers=headers, json=data)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Failed to list kb to the other API: {response.text}")

            return response.json()
    except Exception as e:
        logging.error(f"知识库内文件列表查询过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="知识库内文件列表查询")


# 4.上传文件到rag接口
@console_api.post("/upload_file")
async def upload_file(
        files: List[UploadFile] = File(...),
        kb_id: str = Form(...),
        split_char: str = Form(None),
        max_length: int = Form(None),
        overlap_rate: float = Form(None),
        tenant_id: str = Form(None),
        custom_split_char: str = Form(None),
        account: Account = Depends(login_user)
):
    logging.info("接收到用户发来的文件！")
    logging.info("tenant_id of upload_file: %s, %s", tenant_id, custom_split_char)
    tenant_id = tenant_id or account.current_tenant_id

    RAG_URL = agent_platform_config.BASE_KNOWLEDGE_API_ENDPOINT + "/upload_file"

    # 构造符合 kb.py 接口要求的请求参数
    data = {
        "kb_id": kb_id,
        "tenant_id": tenant_id,
        **({"split_char": split_char} if split_char is not None else {}),
        **({"max_length": max_length} if max_length is not None else {}),
        **({"overlap_rate": overlap_rate} if overlap_rate is not None else {}),
        **({"custom_split_char": custom_split_char} if custom_split_char is not None else {})
    }

    # 本地存储路径
    LOCAL_STORAGE_PATH = "uploads"
    if not os.path.exists(LOCAL_STORAGE_PATH):
        os.makedirs(LOCAL_STORAGE_PATH)

    # 构建多文件请求
    files_data = []
    for file in files:
        file_content = await file.read()
        files_data.append(("files", (file.filename, file_content, file.content_type)))

    headers = {'accept': 'application/json'}

    try:
        async with httpx.AsyncClient() as client:
            # 发送包含文件和表单数据的请求
            response = await client.post(
                RAG_URL,
                headers=headers,
                data=data,
                files=files_data,
                timeout=60
            )
            logging.info("response: %s", response.text)

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to upload file to the other API: {response.text}"
                )

            return {"message": "successfully", "state_code": 200, "rag_response": response.json()}

    except Exception as e:
        logging.error(f"文件上传过程中发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail="文件上传失败")

# 5.删除文档
@console_api.post("/delete_document")
async def delete_document(request: dict, account: Account = Depends(login_user)):
    try:
        kb_id = request.get("kb_id")
        file_name = request.get("file_name","")
        tenant_id = request.get("tenant_id", "")
        logging.info("tenant_id of delete_document: %s", tenant_id)

        tenant_id = tenant_id or account.current_tenant_id

        data = {
            "tenant_id": tenant_id,
            "kb_id": kb_id,
            "file_name": file_name
        }

        headers = {
            'accept': 'application/json'
        }

        RAG_KB_DOC_DELETE_URL = agent_platform_config.BASE_KNOWLEDGE_API_ENDPOINT + "/delete_document"
        async with httpx.AsyncClient() as client:
            response = await client.post(RAG_KB_DOC_DELETE_URL, headers=headers, json=data, timeout=60)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Failed to delete doc to the other API: {response.text}")

            return response.json()
    except Exception as e:
        logging.error(f"知识库内文件删除过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="知识库内文件删除失败")

@console_api.post("/update_kb")
async def update_kb(request: dict, account: Account = Depends(login_user)):
    try:
        kb_id = request.get("kb_id","")
        kb_name = request.get("kb_name", "")
        kb_desc = request.get("kb_desc", "")
        tenant_id = request.get("tenant_id", "")
        logging.info("tenant_id of update_kb: %s", tenant_id)
        tenant_id = tenant_id or account.current_tenant_id

        data = {
            "tenant_id": tenant_id,
            "kb_id": kb_id,
            "kb_name": kb_name,
            "kb_desc": kb_desc,
        }
        print(data)
        headers = {
            'accept': 'application/json'
        }

        RAG_KB_UPDATE_URL = agent_platform_config.BASE_KNOWLEDGE_API_ENDPOINT + "/update_kb"

        async with httpx.AsyncClient() as client:
            response = await client.post(RAG_KB_UPDATE_URL, headers=headers, json=data)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Failed to delete doc to the other API: {response.text}")

            return response.json()
    except Exception as e:
        logging.error(f"知识库删除过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="知识库修改失败")


# 6.删除库
@console_api.post("/delete_kb")
async def delete_kb(request: dict, account: Account = Depends(login_user)):
    try:
        kb_id = request.get("kb_id","")
        tenant_id = request.get("tenant_id", "")
        logging.info("tenant_id of delete_kb: %s", tenant_id)
        tenant_id = tenant_id or account.current_tenant_id
        data = {
            "tenant_id": tenant_id,
            "kb_id": kb_id
        }
        print(data)
        headers = {
            'accept': 'application/json'
        }

        RAG_KB_DELETE_URL = agent_platform_config.BASE_KNOWLEDGE_API_ENDPOINT + "/delete_kb"

        async with httpx.AsyncClient() as client:
            response = await client.post(RAG_KB_DELETE_URL, headers=headers, json=data)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Failed to delete doc to the other API: {response.text}")

            return response.json()
    except Exception as e:
        logging.error(f"知识库删除过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="知识库删除查询")


# 7.历史命中
@console_api.post("/history_mint")
async def history_mint(request: dict, account: Account = Depends(login_user)):
    try:
        kb_id = request.get("kb_id","")
        data = {
            "kb_id": kb_id
        }
        print(data)
        headers = {
            'accept': 'application/json'
        }

        RAG_KB_MINT_URL = agent_platform_config.BASE_KNOWLEDGE_API_ENDPOINT + "/history_mint"

        async with httpx.AsyncClient() as client:
            response = await client.post(RAG_KB_MINT_URL, headers=headers, json=data)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Failed to get history mint : {response.text}")

            return response.json()
    except Exception as e:
        logging.error(f"历史命中查询过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="历史命中查询")

# 8. 直接检索
@console_api.post("/know_query")
async def search_query(request: dict, account: Account = Depends(login_user)):
    try:
        kb_id = request.get("kb_id","")
        query = request.get("query", "")
        top_k = request.get("top_k", 2)
        area = request.get("area", "kb")
        tenant_id = request.get("tenant_id", "")
        logging.info("tenant_id of know_query: %s", tenant_id)
        score_threshold = request.get("score_threshold", 0.0)
        # 在知识库的命中测试页面请求则为"kb"，在工作流、智能体等应用页面请求则为"app"
        tenant_id = tenant_id or account.current_tenant_id

        data = {
            "tenant_id": tenant_id,
            "kb_id": kb_id,
            "query": query,
            "top_k": top_k,
            "area": area,
            "score_threshold": score_threshold
        }
        headers = {
            'accept': 'application/json'
        }
        print(data)
        RAG_KB_SEARCH_URL = agent_platform_config.BASE_KNOWLEDGE_API_ENDPOINT + "/know_query"

        async with httpx.AsyncClient() as client:
            response = await client.post(RAG_KB_SEARCH_URL, headers=headers, json=data, timeout=60)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Failed to search knowledge in RAG: {response.text}")

            return response.json()
    except Exception as e:
        logging.error(f"RAG检索过程出现错误: {e}")
        raise HTTPException(status_code=500, detail="RAG检索")