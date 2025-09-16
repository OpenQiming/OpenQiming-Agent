import logging
import os
from datetime import datetime
from http.client import HTTPException
from io import BytesIO

import pandas as pd
from fastapi import Depends
from fastapi import UploadFile
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform_basic.libs import DbUtils
from agent_platform_basic.models.db_model import Account
from agent_platform_basic.models.db_model.api_info import APIInfo
from agent_platform_service.fastapi_fields.req.console.api_info_req import ApiInfoDto, ApiInfoPageReq, ApiInfoReq
from agent_platform_service.services.account_service import TenantService
from agent_platform_service.utils.apps_common_utils import result_page

logger = logging.getLogger(__name__)


class ApiInfoService:

    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

    async def validate_file_extension(self, filename: str):
        allowed_extensions = ['.xlsx', '.xls']
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise ValueError(f"Unsupported file extension {file_extension}. Allowed extensions: {allowed_extensions}")

    async def read_excel_file(self, file):
        # 使用pandas读取Excel文件，确保使用BytesIO包装file.file
        content = await file.read()
        byte_stream = BytesIO(content)
        return pd.read_excel(byte_stream)

    async def validate_required_columns(self, df):
        required_columns = [
            "接口中文名", "接口英文名", "API_ID", "接口类型", "EOP协议", "EOP调用地址", "服务协议",
            "接口说明", "认证策略", "超时时长", "开放范围", "是否公网", "所属系统", "区域",
            "应用场景"
        ]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Excel文件缺少必要的列: {missing_columns}")

    async def check_duplicate_api_ids(self, df):
        duplicate_api_ids = df[df.duplicated(subset=['API_ID'], keep=False)]['API_ID'].unique().tolist()
        if duplicate_api_ids:
            return {"error": "Excel文件中有重复的API_ID", "duplicate_api_ids": duplicate_api_ids}
        return None

    async def get_existing_api_ids(self):
        query = select(APIInfo.api_id)
        result = await self.session.execute(query)
        existing_api_ids = [row[0] for row in result.all()]
        return existing_api_ids

    async def check_existing_api_ids(self, df, existing_api_ids):
        existing_in_db = df[df['API_ID'].isin(existing_api_ids)]['API_ID'].unique().tolist()
        if existing_in_db:
            return {"error": "数据库中已存在部分API_ID", "existing_api_ids": existing_in_db}
        return None

    async def import_data_to_database(self, df, username: str):
        records = df.to_dict(orient="records")
        for record in records:
            db_record = APIInfo(
                interface_name_zh=record["接口中文名"],
                interface_name_en=record["接口英文名"],
                api_id=record["API_ID"],
                interface_type=record["接口类型"],
                eop_protocol=record["EOP协议"],
                eop_call_address=record["EOP调用地址"],
                service_protocol=record["服务协议"],
                interface_description=record["接口说明"],
                auth_policy=record["认证策略"],
                timeout=record["超时时长"],
                open_scope=record["开放范围"],
                is_public=bool(record["是否公网"]),  # 假设Excel中的"是否公网"列是0或1
                system_belonged_to=record["所属系统"],
                region=record["区域"],
                application_scenario=record["应用场景"],
                headers=record.get("请求头"),
                request_script=record.get("请求脚本"),
                input_params=record.get("输入参数"),
                request_example=record.get("请求示例"),
                output_params=record.get("输出参数"),
                response_example=record.get("返回示例"),
                created_by=username,
                updated_by=username
            )
            self.session.add(db_record)
        await self.session.commit()

    async def api_info_import(self, username: str, file: UploadFile):
        try:
            # 校验文件后缀
            await self.validate_file_extension(file.filename)

            # 读取上传的Excel文件
            df = await self.read_excel_file(file)

            # 检查数据条数是否超过1000条
            if len(df) > 1000:
                raise HTTPException(status_code=400, detail="The number of records exceeds the limit of 1000.")

            # 检查列名是否匹配
            await self.validate_required_columns(df)

            # 检查Excel文件中的API_ID是否有重复
            duplicate_check = await self.check_duplicate_api_ids(df)
            if duplicate_check:
                return duplicate_check

            # 查询数据库中已存在的API_ID
            existing_api_ids = await self.get_existing_api_ids()

            # 检查Excel文件中的API_ID是否存在于数据库中
            existing_check = await self.check_existing_api_ids(df, existing_api_ids)
            if existing_check:
                return existing_check

            # 导入数据到数据库
            await self.import_data_to_database(df, username)

            return {"data": "Data imported successfully"}
        except Exception as e:
            logger.error(f"Error during file upload: {str(e)}")
            return {"error": str(e)}

    async def export_api_info(self, api_id_list: list[str]):
        logger.info(f"Received request: {api_id_list}")
        try:
            query = select(APIInfo).where(APIInfo.api_id.in_(api_id_list))

            logger.info(f"Received request: {query}")
            result = await self.session.execute(query)
            records = result.scalars().all()

            if not records:
                return None

            df = pd.DataFrame([{
                "接口中文名": record.interface_name_zh,
                "接口英文名": record.interface_name_en,
                "API_ID": record.api_id,
                "接口类型": record.interface_type,
                "EOP协议": record.eop_protocol,
                "EOP调用地址": record.eop_call_address,
                "服务协议": record.service_protocol,
                "接口说明": record.interface_description,
                "认证策略": record.auth_policy,
                "超时时长": record.timeout,
                "开放范围": record.open_scope,
                "是否公网": record.is_public,
                "所属系统": record.system_belonged_to,
                "区域": record.region,
                "应用场景": record.application_scenario,
                "请求头": record.headers,
                "请求脚本": record.request_script,
                "输入参数": record.input_params,
                "请求示例": record.request_example,
                "输出参数": record.output_params,
                "返回示例": record.response_example
            } for record in records])
            logger.info(f"Dataframe created with {len(df)} records.")
            # 生成Excel文件
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)

            return output
        except Exception as e:
            logger.error(f"Error during export: {str(e)}")
            return None

    async def delete_api_info(self, api_info_ids: list[str], login_user: Account):
        await self.session.execute(delete(APIInfo).where(APIInfo.id.in_(api_info_ids)))
        await self.session.commit()
        return {"data": "successfully"}

    async def update_api_info(self, api: ApiInfoDto, login_user: Account):
        old_api = await self.session.execute(select(APIInfo).filter(APIInfo.id == api.id))
        old_api: APIInfo = old_api.scalar_one_or_none()
        if not old_api:
            return {"data": "API not found", "status": "error", "code": 500}
        old_api_id = await self.session.execute(select(APIInfo).filter(APIInfo.api_id == api.api_id))
        old_api_id = old_api_id.scalar_one_or_none()
        if old_api_id:
            if old_api_id.id != api.id:
                return {"data": "API_ID already exists", "status": "error", "code": 500}

        old_api.api_id = api.api_id
        old_api.interface_name_zh = api.interface_name_zh
        old_api.interface_name_en = api.interface_name_en
        old_api.interface_type = api.interface_type
        old_api.eop_protocol = api.eop_protocol
        old_api.eop_call_address = api.eop_call_address
        old_api.service_protocol = api.service_protocol
        old_api.interface_description = api.interface_description
        old_api.auth_policy = api.auth_policy
        old_api.timeout = api.timeout
        old_api.open_scope = api.open_scope
        old_api.is_public = api.is_public
        old_api.system_belonged_to = api.system_belonged_to
        old_api.region = api.region
        old_api.application_scenario = api.application_scenario
        old_api.headers = api.headers
        old_api.request_script = api.request_script
        old_api.input_params = api.input_params
        old_api.request_example = api.request_example
        old_api.output_params = api.output_params
        old_api.response_example = api.response_example
        old_api.updated_by = login_user.id
        old_api.updated_at = datetime.now().replace(tzinfo=None)

        await self.session.merge(old_api)
        await self.session.commit()
        return {"data": "successfully"}

    async def query_api_info(self, pageReq: ApiInfoPageReq):
        filters = []
        if pageReq.interface_name_zh:
            filters.append(APIInfo.interface_name_zh.like(f"%{pageReq.interface_name_zh}%"))
        if pageReq.api_id:
            filters.append(APIInfo.api_id.like(f"%{pageReq.api_id}%"))
        if pageReq.interface_type:
            filters.append(APIInfo.interface_type == pageReq.interface_type)
        if pageReq.region:
            filters.append(APIInfo.region == pageReq.region)
        if pageReq.application_scenario:
            filters.append(APIInfo.application_scenario == pageReq.application_scenario)

        datas = await paginate(self.session, select(APIInfo).where(*filters).order_by(APIInfo.created_at.desc()),
                               Params(page=pageReq.page, size=pageReq.limit))
        # api_info_id_list = [data.id for data in datas.items]

        return result_page(datas.items, datas.total, pageReq.page, pageReq.limit)

    async def create_api_info(self, req: ApiInfoDto, login_user: Account):
        if req.id:
            return {"data": "id is not allowed", "status": "error", "code": 500}
        if not req.api_id:
            return {"data": "api_id is required", "status": "error", "code": 500}
        api_id_info = await self.session.execute(select(APIInfo).filter(APIInfo.api_id == req.api_id))
        if api_id_info.scalar_one_or_none():
            return {"data": "api_id already exists", "status": "error", "code": 500}
        api = APIInfo(**req.dict())
        api.created_by = login_user.id
        self.session.add(api)
        await self.session.commit()
        return {"data": "successfully"}
