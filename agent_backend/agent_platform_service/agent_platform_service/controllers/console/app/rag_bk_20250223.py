import httpx
from fastapi import Depends
from agent_platform_service.services.auth_service import login_user
from agent_platform_basic.models.db_model import AccountIntegrate, InvitationCode, Account
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.helper import async_ssrf_proxy
from agent_platform_service.controllers.console import console_api
from fastapi import FastAPI, File, UploadFile, HTTPException
import logging
from agent_platform_service.fastapi_fields.req.console.rag_req import UploadFileForRagReq
import os
import uuid

uuid_namespace = uuid.NAMESPACE_URL

# 查询场景编号字典接口
@console_api.get("/check-assistant-code")
async def check_assistant_code(name: str):
    logging.info(f"查询场景编号字典接口，name: {name}")
    print(f"查询场景编号字典接口，name: {name}")
    data = await get_assistant_list(name)
    print(data)
    # if code in data:
    #     return data[code] == name
    # else:
    #     return False
    # logging.info("查询成功", data)
    return data


@console_api.post("/kb_create")
# async def kb_create(kb_name, kb_desc, user: Account = Depends(login_user)):
async def kb_create(request: dict, user: Account = Depends(login_user)):
    print(request)
    kb_name = request.get("kb_name")
    kb_desc = request.get("kb_desc")
    tenant_id = Account.current_tenant_id
    user_name = Account.username

    try:

        headers = {
            'accept': 'application/json'
        }

        data = {"kb_name": kb_name,
                "kb_desc": kb_desc,
                "tenant_id": tenant_id,
                "user_name": user_name}

        RAG_KB_CREATE_URL = "https://172.27.221.54:8000/kb-create"


        async with httpx.AsyncClient() as client:
            response = await client.post(RAG_KB_CREATE_URL, headers=headers, data=data)

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Failed to upload file to the other API: {response.text}")

            return {"message": "File uploaded successfully", "state_code": 200}
    except Exception as e:
        logging.error(f"文件上传过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="知识库创建失败")



# 上传文件到rag接口
@console_api.post("/upload_file_for_rag")
async def upload_file_for_rag(file:UploadFile = File(...), user: Account = Depends(login_user)):
    logging.info("接收到用户发来的文件！")

    RAG_URL = "http://172.27.221.53:8000/upload/"

    # user_account_id = Account.id
    # Account.



    # 设置允许上传的文件类型
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    # 获取文件的扩展名
    file_extension = file.filename.split('.')[-1].lower()

    # 检查文件类型是否被允许
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不允许上传该文件类型。仅支持 PDF 和 DOCX 文件。")

    # 本地存储路径
    LOCAL_STORAGE_PATH = "uploads"
    if not os.path.exists(LOCAL_STORAGE_PATH):
        os.makedirs(LOCAL_STORAGE_PATH)

    try:
        file_content = await file.read()
        # logging.info(f"接收到的文件内容:\n{file_content.decode()}")
        # 1. 将文件保存到本地
        file_path = os.path.join(LOCAL_STORAGE_PATH, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        logging.info(f"文件已保存到本地: {file_path}")

        with open(file_path, 'rb') as file:
            # 准备文件数据
            files = {'file': file}
            # 定义请求头
            headers = {
                'accept': 'application/json'
            }
            # 发送同步 POST 请求
            async with httpx.AsyncClient() as client:
                response = await client.post(RAG_URL, headers=headers, files=files)

                if response.status_code != 200:
                    raise HTTPException(status_code=response.status_code, detail=f"Failed to upload file to the other API: {response.text}")
        # async with httpx.AsyncClient() as client:
        #     files = {"file": file_path}
        #     headers = {"accept": "application/json"}
        #     response = await client.post(url = RAG_URL,files=files,headers=headers)
        #     if response.status_code != 200:
        #         raise HTTPException(status_code=response.status_code, detail=f"Failed to upload file to the other API: {response.text}")
        return {"message": "File uploaded successfully", "state_code": 200}

    except Exception as e:
        logging.error(f"文件上传过程中发生错误: {e}")
        raise HTTPException(status_code=500, detail="文件上传失败")

@console_api.get("/get-region-list")
async def get_region_list():
    data = {
        "集团": "911010000000000000000000",
        "北京市": "111000000000000000000000",
        "天津市": "121000000000000000000000",
        "河北省": "131000000000000001216374",
        "山西省": "141011000000000000049839",
        "内蒙古自治区": "151000000000000268503725",
        "辽宁省": "211000000000000000000001",
        "吉林省": "221000100000000000000001",
        "黑龙江省": "231009100000000000000001",
        "上海市": "311115000000000000000000",
        "江苏省": "321122930000000000000014",
        "浙江省": "331711000000000021720883",
        "安徽省": "341033000000000002392001",
        "福建省": "351000000000000000000001",
        "江西省": "361011000000000036696304",
        "山东省": "371110000000000000000021",
        "河南省": "411000000000000001950388",
        "湖北省": "421100000000000000064915",
        "湖南省": "431102000000000000000001",
        "广东省": "441000000000000103054855",
        "广西壮族自治区": "451102000000000021333149",
        "海南省": "461000000000000000026357",
        "重庆市": "501102000000000000000000",
        "四川省": "511000000000000000000000",
        "贵州省": "521000000000000000000001",
        "云南省": "531000000000000000000477",
        "西藏自治区": "541000000000000261037094",
        "陕西省": "611000000000001824854982",
        "甘肃省": "621102000900800000004455",
        "青海省": "631100000000000067126468",
        "宁夏回族自治区": "641102000000000000000069",
        "新疆维吾尔自治区": "651102000000000021347615"
    }
    return data

async def get_assistant_list(job_type_name):
    headers = {
        "Content-Type": "application/json"
    }

    param = {
        "jobTypeName": job_type_name
    }

    response = await async_ssrf_proxy.post(agent_platform_config.RAG_ASSISTANT_LIST_URL, json=param, headers=headers)


    data_dict = response.json()

    result = dict()
    # data_dict = json.loads(response_json)
    print(data_dict["code"])
    if data_dict["code"] == 200:
        for row in data_dict["rows"]:
            result[row["jobTypeCode"]] = row["remark"]
    else:
        logging.info("查询失败")

    return result
