from agent_platform_service.controllers.interface import interface_api
from agent_platform_service.services import model_register_service
from agent_platform_service.services.auth_service import login_user
from agent_platform_service.fastapi_fields.req.interface_api.model_register_req import AddApiReq, UpdateKeyReq
from agent_platform_service.fastapi_fields.resp.interface_api.model_register_resp import ModelRegisterResp

from fastapi import Depends, status, Request

from agent_platform_service.services.model_register_service import ModelRegisterService


@interface_api.post("/add-api", response_model=ModelRegisterResp, status_code=status.HTTP_201_CREATED)
async def addApi_post(request_body: AddApiReq,
                      model_register_service: ModelRegisterService = Depends(ModelRegisterService),
                      current_user=Depends(login_user)):
    args = request_body.model_dump()
    return await model_register_service.add_api(json=args)


@interface_api.get("/delete-api", status_code=status.HTTP_200_OK)
async def deleteApi_get(api_id: str, model_register_service: ModelRegisterService = Depends(ModelRegisterService)):
    return await model_register_service.delete_api(api_id)


@interface_api.get("/api-info", status_code=status.HTTP_200_OK)
async def apiInfo_get(page_index: str, page_size: str, create_by: str,
                      model_register_service: ModelRegisterService = Depends(ModelRegisterService),current_user=Depends(login_user)):
    return await model_register_service.api_info(page_index, page_size, create_by)

@interface_api.post("/update_key", status_code=status.HTTP_200_OK)
async def update_key_post(request_body: UpdateKeyReq,
                          model_register_service: ModelRegisterService = Depends(ModelRegisterService)):
    args = request_body.model_dump()
    return await model_register_service.update_key(json=args)

@interface_api.get("/inter_call_info", status_code=status.HTTP_200_OK)
async def inter_call_info_get(request: Request, model_register_service: ModelRegisterService = Depends(ModelRegisterService)):
    qp = request.query_params
    return await model_register_service.inter_call_info(qp)