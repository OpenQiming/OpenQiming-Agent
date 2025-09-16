import logging

from fastapi import Depends, HTTPException
from fastapi import File, UploadFile
from fastapi.responses import JSONResponse
from starlette.responses import StreamingResponse

from agent_platform_basic.models.db_model import Account
from agent_platform_service.controllers.console import console_api
from agent_platform_service.fastapi_fields.req.console.api_info_req import ApiInfoDto, \
    ApiInfoPageReq, ApiInfoPageResp, ApiInfoReq, ApiExportReq
from agent_platform_service.fastapi_fields.resp.console.api_info_res import ApiInfoExportedResp, ApiInfoImportResp, \
    ApiInfoInsertResp, ApiInfoUpdateResp, ApiInfoDeleteResp
from agent_platform_service.services.api.api_info_service import ApiInfoService
from agent_platform_service.services.auth_service import login_user

logger = logging.getLogger(__name__)


@console_api.post("/api/info/import", response_model=ApiInfoImportResp)
async def api_info_import(file: UploadFile = File(...), current_user: Account = Depends(login_user),
                          api_service: ApiInfoService = Depends()):
    result = await api_service.api_info_import(current_user.username, file)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return JSONResponse(content=result, status_code=200)


@console_api.post("/api/info/export")
async def export_api_info(req: ApiExportReq, api_info_service: ApiInfoService = Depends()):

    api_id_list = req.api_id_list
    if api_id_list is None or len(api_id_list) == 0:
        raise HTTPException(status_code=400, detail="No data selected")
    if len(api_id_list) > 1000:
        raise HTTPException(status_code=400, detail="num of records should be less than 1000")
    output = await api_info_service.export_api_info(api_id_list=api_id_list)

    if not output:
        raise HTTPException(status_code=404, detail="No data found for the given parameters")
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=api_info_export.xlsx"}
    )
    # todo 权限控制


@console_api.post("/api/info/delete", response_model=ApiInfoDeleteResp)
async def delete_api_info(req: list[int], api_info_service: ApiInfoService = Depends(),
                          login_user: Account = Depends(login_user)):
    result = await api_info_service.delete_api_info(api_info_ids=req, login_user=login_user)
    if "error" in result:
        raise JSONResponse(content=result, status_code=200)
    return JSONResponse(content=result, status_code=200)


@console_api.post("/api/info/update", response_model=ApiInfoUpdateResp)
async def update_api_info(req: ApiInfoDto, api_info_service: ApiInfoService = Depends(),
                          login_user: Account = Depends(login_user)):
    result = await api_info_service.update_api_info(api=req, login_user=login_user)
    if "error" in result:
        raise JSONResponse(content=result, status_code=200)
    return JSONResponse(content=result, status_code=200)


@console_api.post("/api/info/query", response_model=ApiInfoPageResp)
async def query_api_info(req: ApiInfoPageReq, api_info_service: ApiInfoService = Depends(),
                         login_user: Account = Depends(login_user)):
    return await api_info_service.query_api_info(pageReq=req)


@console_api.post("/api/info/create", response_model=ApiInfoInsertResp)
async def create_api_info(req: ApiInfoDto, api_info_service: ApiInfoService = Depends(),
                          login_user: Account = Depends(login_user)):
    result = await api_info_service.create_api_info(req=req, login_user=login_user)
    if "error" in result:
        raise JSONResponse(content=result, status_code=200)
    return JSONResponse(content=result, status_code=200)
