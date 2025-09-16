import json
import logging
import random
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import aliased
from fastapi import Depends, HTTPException
from openai import NotFoundError
from sqlalchemy import func, delete
from sqlalchemy import update
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.elements import BinaryExpression, and_
from agent_platform_basic.models.enum_model.tenant import TenantAccountRole
from agent_platform_basic.exceptions.controllers.console.application_audti import ApplicationAlreadyCreatedError
from agent_platform_basic.libs import DbUtils
from agent_platform_basic.models.db_model import Tenant, Account, TenantAccountJoin
from agent_platform_basic.models.db_model.application_audit import ApplicationAudit
from agent_platform_basic.models.db_model.application_audit_share import ApplicationAuditShare
from agent_platform_basic.models.enum_model.application_audit import ApplicationType, AuditStatus
from agent_platform_core.models.db_model.model import App
from agent_platform_core.models.db_model.model.big_model import Bigmodel
from agent_platform_core.models.db_model.tools import ApiToolProvider
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.fastapi_fields.req.console.application_audit_req import ApplicationAuditUpdateReq, \
    ApplicationAuditCreateReq, ApplicationAuditPageReq
from agent_platform_service.fastapi_fields.resp.console.application_audit_resp import ApplicationAuditPageResp, \
    ApplicationAuditItem
from agent_platform_service.fastapi_fields.resp.console.user_permissions_resp import Reviewer
from agent_platform_service.services.account_service import TenantService
from agent_platform_service.services.auth.user_permissions_service import UserPermissionsService
from agent_platform_service.services.auth_service import login_user

logger = logging.getLogger(__name__)


class ApplicationAuditService:

    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session),
                 session_share: AsyncSession = Depends(DbUtils.get_db_async_share_session),
                 user_permissions_service: UserPermissionsService = Depends(UserPermissionsService)):
        self.session = session
        self.session_share = session_share
        self.user_permissions_service = user_permissions_service

    async def validate_request_body(self, req: ApplicationAuditCreateReq) -> object:
        # 检查 application_type 是否为有效枚举值
        if req.application_type not in ApplicationType.__members__.values():
            raise ValueError("application_type must be one of the valid values.")
        # 检查必填字段是否为空或仅包含空白字符
        if not req.application_type.strip():
            raise ValueError("application_type must not be empty or only whitespace.")

        if not req.applicant_id.strip():
            raise ValueError("applicant_id must not be empty or only whitespace.")

        if not req.applicant.strip():
            raise ValueError("applicant must not be empty or only whitespace.")

        if not req.reason.strip():
            raise ValueError("reason must not be empty or only whitespace.")

        if not req.app_id.strip():
            raise ValueError("app_id must not be empty or only whitespace.")

        # 检查可选字段是否为空或仅包含空白字符
        if req.space_id is not None and not req.space_id.strip():
            raise ValueError("space_id must not be empty or only whitespace if provided.")

    async def validate_update_request_body(self, req: ApplicationAuditUpdateReq) -> object:

        if not req.process_id.strip():
            raise ValueError("applicant_id must not be empty or only whitespace.")

        if req.status == AuditStatus.DENIED.value:
            if req.denial_reason is not None and not req.denial_reason.strip():
                raise ValueError("denial_reason must not be empty or only whitespace if provided.")

    """
     个人空间发布流程创建接口
    """

    async def application_process_self_create(self, request_body: ApplicationAuditCreateReq):

        result_tenants = await self.session.execute(
            select(Tenant).where(Tenant.id == request_body.space_id))
        tenant = result_tenants.scalars().first()

        # 创建 ApplicationAudit 对象
        new_audit = ApplicationAudit(
            application_type=request_body.application_type,
            applicant_id=request_body.employee_number,
            applicant=request_body.username,
            reason=request_body.reason,
            app_id=request_body.app_id,
            app_type=request_body.app_type,
            space_id=request_body.space_id,
            space_name=tenant.name,
            status=request_body.status,
            reviewer_id=request_body.reviewer_id,
            reviewer=request_body.reviewer,
            reviewed_at=datetime.now(),
        )
        # 添加到数据库
        self.session.add(new_audit)
        try:
            # 提交事务
            await self.session.commit()
            return {
                "result": "success",
                "process_id": new_audit.id
            }
        except IntegrityError as e:
            # 回滚事务
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

    """
      todo 流程审核人员列表 后续可以放到配置文件，或者数据库
    """
    reviewers = [
        # Reviewer(id="71091756@CQ", name="李翔"),
        # Reviewer(id="W8518993@CQ", name="黄观生"),
        # Reviewer(id="W8526295@CQ", name="曹峻豪"),
        # Reviewer(id="71156075@CQ", name="何岩峰"),
        # Reviewer(id="71174470@CQ", name="许家豪"),
        # Reviewer(id="71199950@CQ", name="雷瑞清"),
        # Reviewer(id="71182783@CQ", name="周家西"),
        # Reviewer(id="71206368@CQ", name="蔡雨廷"),
        # Reviewer(id="71195820@CQ", name="胡科"),
        # Reviewer(id="71112861@XJ", name="何世华"),
        # Reviewer(id="71162956@GD", name="董立言"),
        # Reviewer(id="71123204@HQ", name="许豪"),
        # Reviewer(id="71097080@HQ", name="薛裕颖"),
        # Reviewer(id="71136417@HQ", name="王羽培"),
        # Reviewer(id="71094606@HQ", name="刘巧俏"),
        # Reviewer(id="71145770@sh", name="于舒阳"),
        # Reviewer(id="71181613@sh", name="杨媛翔"),
        # Reviewer(id="71181621@sh", name="翟羽佳"),
        # Reviewer(id="71002109", name="刘凯"),
        Reviewer(id="W9567754@FJ", name="13051069274"),     # 增加邱力帅为超级管理员
        Reviewer(id="71097080@HQ", name="薛裕颖"),
        # Reviewer(id="71117607@JX", name="吴文韬")     # 江西省侧超级管理员
        # Reviewer(id="71010625", name="陈坚"),
        # Reviewer(id="71111866@HQ", name="李冬冬")
    ]

    def get_random_reviewer(self) -> Optional[Reviewer]:
        return self.reviewers[-1]

    async def check_application_exists(self, application_type: str, applicant_id: str, app_id: str, app_type: str):
        query_conditions = [
            ApplicationAudit.application_type == application_type,
            ApplicationAudit.applicant_id == applicant_id,
            ApplicationAudit.app_id == app_id,
            ApplicationAudit.app_type == app_type,
            ApplicationAudit.status == AuditStatus.PENDING.value
        ]
        logger.info("查询是否存在已经创建的========================================================================")
        for expr in query_conditions:
            logger.info(str(expr))
        logger.info("========================================================================")

        result = await self.session.execute(select(ApplicationAudit).filter(and_(*query_conditions)))
        existing_record = result.scalars().first()
        if existing_record:
            logger.info("存在已经创建的流程========================================================================")
            logger.info(str(existing_record))
            logger.info("========================================================================")
            raise ApplicationAlreadyCreatedError()


    async def check_space_exist_model(self,space_id:str,model_id:str):
        print("入参为",space_id,model_id,"================================","\n")
        result = await self.session.execute(
            select(ApplicationAudit).where(
                ApplicationAudit.tool_param.like(f"%{model_id}%"),
                ApplicationAudit.space_id == space_id
            )
        )
        f = result.scalars().first()
        print("查询判重结果===============================================================================")
        print(f)

        if f:
            return True
        else:
            return False
    """
     流程创建接口
    """
    async def application_process_create(self, request_body: ApplicationAuditCreateReq):
        if request_body.app_type != AppMode.BIGMODEL.value:
            await self.check_application_exists(request_body.application_type, request_body.employee_number,
                                            request_body.app_id, request_body.app_type)

        logger.info("开始创建应用审核流程 ============================================== ")
        result_tenants = await self.session.execute(
            select(Tenant).where(Tenant.id == request_body.space_id))
        if request_body.application_type == ApplicationType.PUBLIC.value:
            tenant = Tenant(id=request_body.space_id, name='模型广场')
        else:
            tenant = result_tenants.scalars().first()
        logger.info("查询到的项目空间 ============================================== ")
        logger.info(tenant)
        reviewer_employee_number = ""
        if request_body.application_type and request_body.application_type == ApplicationType.PROJECT.value:
            logger.info("发布到项目空间 ============================================== ")
            join_query = await self.session.execute(
                select(TenantAccountJoin).filter(TenantAccountJoin.tenant_id == request_body.space_id,
                                                 TenantAccountJoin.role == 'owner'))
            join = join_query.scalar_one_or_none()
            account_query = await self.session.execute(select(Account).filter(Account.id == join.account_id))
            reviewer_obj = account_query.scalar_one_or_none()
            reviewer_employee_number = reviewer_obj.employee_number
        elif request_body.application_type and request_body.application_type == ApplicationType.SHARE.value:
            logger.info("发布到共享广场 ============================================== ")
            reviewer_obj = self.get_random_reviewer()
            reviewer_employee_number = reviewer_obj.id
        else:
            logger.info("发布到广场 ============================================== ")
            reviewer_obj = self.get_random_reviewer()
            reviewer_employee_number = reviewer_obj.id

        if request_body.application_type and request_body.application_type == ApplicationType.SHARE.value:
            # 如果是发布到共享广场
            new_audit_share = ApplicationAuditShare(
                application_type=request_body.application_type,
                applicant_id=request_body.employee_number,
                applicant=request_body.applicant,
                reason=request_body.reason,
                app_id=request_body.app_id,
                app_type=request_body.app_type,
                space_id=request_body.space_id,
                space_name=tenant.name,
                reviewer_id=reviewer_employee_number,
                reviewer=reviewer_obj.name,
                status=AuditStatus.PENDING.value,
                change_description=request_body.change_description,
                need_publish_tool=request_body.need_publish_tool,
                tool_param=request_body.tool_param
            )
            # 添加到共享数据库
            self.session.add(new_audit_share)
            try:
                # 提交事务
                await self.session.commit()
                return {
                    "result": "success",
                    "process_id": str(new_audit_share.id)
                }
            except IntegrityError as e:
                # 回滚事务
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
        else:
            print("request_body:::", request_body.applicant)
            # 创建 ApplicationAudit 对象
            new_audit = ApplicationAudit(
                application_type=request_body.application_type,
                applicant_id=request_body.employee_number,
                applicant=request_body.applicant,
                reason=request_body.reason,
                app_id=request_body.app_id,
                app_type=request_body.app_type,
                space_id=request_body.space_id,
                space_name=tenant.name,
                reviewer_id=reviewer_employee_number,
                reviewer=reviewer_obj.name,
                status=AuditStatus.PENDING.value,
                change_description=request_body.change_description,
                need_publish_tool=request_body.need_publish_tool,
                tool_param=request_body.tool_param
            )
            if (
                    new_audit.app_type == AppMode.BIGMODEL.value and new_audit.application_type == ApplicationType.PROJECT.value):
                d = json.loads(request_body.tool_param)
                exist = await self.check_space_exist_model(request_body.space_id, d.get("bussiness_id"))
                if exist:
                    raise HTTPException(status_code=500, detail=f"大模型再在此项目空间已经发布过")
            logger.info("打印创建的流程对象 ==============================================")
            logger.info('application_type=%s' % (
                request_body.application_type if request_body.application_type is not None else ""))
            logger.info(
                'applicant_id=%s' % (request_body.employee_number if request_body.employee_number is not None else ""))
            logger.info('applicant=%s' % (request_body.username if request_body.username is not None else ""))
            logger.info('reason=%s' % (request_body.reason if request_body.reason is not None else ""))
            logger.info('app_id=%s' % (request_body.app_id if request_body.app_id is not None else ""))
            logger.info('app_type=%s' % (request_body.app_type if request_body.app_type is not None else ""))
            logger.info('space_id=%s' % (request_body.space_id if request_body.space_id is not None else ""))
            logger.info('space_name=%s' % (tenant.name if tenant and tenant.name is not None else ""))
            logger.info('reviewer_id=%s' % (reviewer_employee_number if reviewer_employee_number is not None else ""))
            logger.info('reviewer=%s' % (reviewer_obj.name if reviewer_obj and reviewer_obj.name is not None else ""))
            logger.info('status=%s' % (AuditStatus.PENDING.value if AuditStatus.PENDING.value is not None else ""))
            logger.info('change_description=%s' % (
                request_body.change_description if request_body.change_description is not None else ""))
            logger.info('need_publish_tool=%s' % (
                request_body.need_publish_tool if request_body.need_publish_tool is not None else ""))
            logger.info('tool_param=%s' % (request_body.tool_param if request_body.tool_param is not None else ""))
            logger.info("打印创建的流程对象结束 ==============================================")
            # 添加到数据库
            self.session.add(new_audit)
            try:
                # 提交事务
                await self.session.commit()
                return {
                    "result": "success",
                    "process_id": str(new_audit.id)
                }
            except IntegrityError as e:
                # 回滚事务
                await self.session.rollback()
                raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

    async def get_application_audit_by_id(self, process_id: str) -> ApplicationAudit:
        result = await self.session.execute(
            select(ApplicationAudit).where(ApplicationAudit.id == uuid.UUID(process_id))
        )
        dbApplicationAudit = result.scalars().first()

        if dbApplicationAudit is None:
            raise NotFoundError(f"No application audit found with ID {process_id}")
        return dbApplicationAudit

    async def check_reviewer_permission(self, reviewer_id: str) -> bool:
        for reviewer in self.reviewers:
            if reviewer.id == reviewer_id:
                return True
        raise HTTPException(status_code=403, detail=reviewer_id + "没有删除权限")

    async def application_process_delete(self, delete_body: ApplicationAuditUpdateReq, employee_number: str):
        #
        # # 检查用户是否有删除权限
        # await self.check_reviewer_permission(employee_number)

        # 先查询数据库以确认审核人的ID是否与提供的employee_number匹配
        query_result = await self.session.execute(
            select(ApplicationAudit)
                .where(ApplicationAudit.id == uuid.UUID(delete_body.process_id))
        )

        audit_record = query_result.scalar_one_or_none()

        if audit_record is None:
            raise HTTPException(status_code=404, detail="No such audit record found.")

        if audit_record.reviewer_id != employee_number:
            raise HTTPException(status_code=403, detail="不允许删除此记录，因为您不是审核人。")

        try:
            # 构建删除语句
            result = await self.session.execute(
                delete(ApplicationAudit)
                    .where(ApplicationAudit.id == uuid.UUID(delete_body.process_id))
                    .where(ApplicationAudit.reviewer_id == employee_number)
                    .execution_options(synchronize_session="fetch")
            )

            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="No such audit record found.")

            # 提交事务
            await self.session.commit()
            return {
                "result": "success",
                "process_id": delete_body.process_id
            }
        except IntegrityError as e:
            # 回滚事务
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

    async def application_process_update(self, update_body: ApplicationAuditUpdateReq):
        logger.info("修改审批流程状态=============================")
        # 构建更新语句
        try:
            # 执行更新语句
            result = await self.session.execute(update(ApplicationAudit)
                                                .where(
                ApplicationAudit.id == ApplicationAudit.id == uuid.UUID(update_body.process_id))
                                                .values(
                status=update_body.status,
                denial_reason=update_body.denial_reason,
                reviewed_at=datetime.now()
            ).execution_options(synchronize_session="fetch"))
            if result.rowcount == 0:
                raise HTTPException(status_code=404, detail="No such audit record found.")

            # 提交事务
            await self.session.commit()
            return {
                "result": "success",
                "process_id": update_body.process_id
            }
        except IntegrityError as e:
            # 回滚事务
            await self.session.rollback()
            raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

    """
     流程审核接口
    """

    async def application_process_page_list(self, req: ApplicationAuditPageReq,
                                            current_user: Account = Depends(login_user)):
        logger.info(f'req=====>:{req}')
        logger.info(f'current_user=====>:{current_user.id}:{current_user.employee_number}')
        super_read_auth = await self.user_permissions_service.check_user_is_super_admin_read_auth(
            current_user.employee_number)
        super_edit_auth = await self.user_permissions_service.check_user_is_super_admin_edit_auth(
            current_user.employee_number)

        filters: List[BinaryExpression] = []
        # if not super_read_auth and not super_edit_auth:
        #     filters.append(ApplicationAudit.applicant_id == current_user.employee_number)
        #     filters.append(ApplicationAudit.application_type != ApplicationType.NORMAL.value)
        #     filters.append(ApplicationAudit.application_type != ApplicationType.PROJECT.value)

        # if current_user.is_tenant_admin_or_owner(current_user.employee_number):
        #     filters.append(ApplicationAudit.application_type == ApplicationType.PROJECT.value)
        # 完全不理解审核列表要看到审核人不是自己的逻辑    --hesh
        # if req.need_check:
        #     filters.append(ApplicationAudit.reviewer_id == current_user.employee_number)
        # else:
        #     filters.append(ApplicationAudit.reviewer_id != current_user.employee_number)

        # filters.append(ApplicationAudit.reviewer_id == current_user.employee_number)
        # if req.status:
        #     filters.append(ApplicationAudit.status == req.status)
        filters.append(ApplicationAudit.status == 'pending')
        if req.space_id: #tenant_id
            filters.append(ApplicationAudit.space_id == req.space_id)
            is_admin_or_owner = current_user.is_admin_or_owner

            #获取创建者
            query = (
                select(TenantAccountJoin)
                .where(and_(TenantAccountJoin.role==TenantAccountRole.OWNER.value,
                            TenantAccountJoin.tenant_id==req.space_id))
            )
            # query = (
            #     select(TenantAccountJoin)
            #     .where(and_(TenantAccountJoin.role==TenantAccountRole.OWNER.value,
            #                 TenantAccountJoin.tenant_id==req.space_id,
            #                 TenantAccountJoin.account_id==current_user.id))
            # )
            #判断登陆人 是否是这个空间的管理者 如果是 管理者就 审核  不是管理者 只能查看自己申请的发布都有哪些
            tenant_account_join = await self.session.execute(query)
            is_owner = tenant_account_join.scalars().first()

            # 如果是创建者 或者admin
            if is_admin_or_owner:
                owner_info = await self.session.execute(select(Account).where(Account.id==is_owner.account_id))
                owner_info = owner_info.scalars().first()
                #获取创建者的所有审批
                filters.append(ApplicationAudit.reviewer_id == owner_info.employee_number)
            else:
                filters.append(ApplicationAudit.applicant_id == current_user.employee_number)
        if req.space_name:
            filters.append(ApplicationAudit.space_name == req.space_name)
        if req.applicant_id:
            filters.append(ApplicationAudit.applicant_id == req.applicant_id)
        if req.applicant:
            filters.append(ApplicationAudit.applicant == req.applicant)
        if req.reason:
            filters.append(ApplicationAudit.reason == req.reason)
        if req.app_id:
            filters.append(ApplicationAudit.app_id == req.app_id)

        # 这块逻辑感觉是错的  因为我看不懂  --hesh
        if req.app_type:
            app_type_list = req.app_type if req.app_type is not None else []
            filters.append(ApplicationAudit.app_type.in_(app_type_list))

        if req.application_type:
            application_type_list = req.application_type if req.application_type is not None else []
            filters.append(ApplicationAudit.application_type.in_(application_type_list))

        if req.denial_reason:
            filters.append(ApplicationAudit.denial_reason == req.denial_reason)
        # if req.reviewer_id:
        #     filters.append(ApplicationAudit.reviewer_id == req.reviewer_id)
        # if req.reviewer:
        #     filters.append(ApplicationAudit.reviewer == req.reviewer)

        query = (select(ApplicationAudit))
        if filters:
            query = query.where(and_(*filters))

        total = await self.session.scalar(select(func.count()).select_from(ApplicationAudit).where(and_(*filters)))
        paginated_query = (
            query
                .offset((req.page - 1) * req.limit)
                .limit(req.limit)
        )
        logger.info(f'paginated_query:{paginated_query}')
        results: Result = await self.session.execute(paginated_query)
        orm_results = results.scalars().all()
        print(orm_results)
        app_ids = []
        tool_api_provider_ids = []
        for item in orm_results:
            if item.app_type == AppMode.TOOL.value:
                tool_api_provider_ids.append(item.app_id)
            else:
                app_ids.append(item.app_id)
        apps_dict = {}
        tools_dict = {}
        if app_ids:
            # app_ids_uuid = await self.convert_to_uuid_list(app_ids)
            app_query = select(App).where(App.id.in_(app_ids))
            apps_result = await self.session.execute(app_query)
            for app in apps_result.scalars().all():
                account_query = await self.session.execute(
                    select(Account).filter(Account.id == app.account_id))
                account_item = account_query.scalar_one_or_none()
                app_creator = account_item.username

                apps_dict[app.id] = {
                    "app_name": app.name,
                    "app_attr": app.mode,
                    "app_desc": app.description,
                    "app_creator": app_creator
                }

            # 查询 app对应的 tenant 租户owner
            sql = '''
                select ap.id app_id, a.id owner_id, a.name owner_name from apps ap left join tenant_account_join  t on ap.tenant_id=t.tenant_id left join accounts a on a.id=t.account_id
                where  t.role='owner' and ap.id in ()
            '''
            t = aliased(TenantAccountJoin)
            a = aliased(Account)

            query = (
                select(App.id.label("app_id"), a.id.label("owner_id"), a.name.label("owner_name"))
                .join(t, App.tenant_id == t.tenant_id)
                .join(a, t.account_id == a.id)
                .where(t.role == TenantAccountRole.OWNER.value, App.id.in_(app_ids))
            )
            app_account_result = await self.session.execute(query)

            # 转成字典（如果你需要）
            rows = app_account_result.mappings().all()
            app_id_owner = {r.get("app_id"): {"owner_id": r.get("owner_id", ""), "owner_name": r.get("owner_name", "")} for r in rows}

        # 查询 ApiToolProvider 表
        if tool_api_provider_ids:
            # tool_app_ids_uuid = await self.convert_to_uuid_list(tool_app_ids)
            tool_query = select(ApiToolProvider).where(ApiToolProvider.id.in_(tool_api_provider_ids))
            tools_result = await self.session.execute(tool_query)
            for tool in tools_result.scalars().all():
                account_query = await self.session.execute(
                    select(Account).filter(Account.id == tool.user_id))
                account_item = account_query.scalar_one_or_none()
                app_creator = account_item.username
                tools_dict[tool.id] = {
                    "app_name": tool.name,
                    "app_attr": "tool",  # ToolApp 表中没有直接对应的字段
                    "app_desc": tool.description,
                    "app_creator": app_creator  # ToolApp 表中没有直接对应的字段
                }

            # 查询 app对应的 tenant 租户owner
            sql = '''
                select ap.id app_id, a.id owner_id, a.name owner_name from apps ap left join tenant_account_join  t on ap.tenant_id=t.tenant_id left join accounts a on a.id=t.account_id
                where  t.role='owner' and ap.id in ()
            '''
            t = aliased(TenantAccountJoin)
            a = aliased(Account)

            query = (
                select(App.id.label("app_id"), a.id.label("owner_id"), a.name.label("owner_name"))
                .join(t, App.tenant_id == t.tenant_id)
                .join(a, t.account_id == a.id)
                .where(t.role == TenantAccountRole.OWNER.value, App.id.in_(app_ids))
            )
            app_account_result = await self.session.execute(query)

            # 转成字典（如果你需要）
            rows = app_account_result.mappings().all()
            app_id_owner = {r.get("app_id"): {"owner_id": r.get("owner_id", ""), "owner_name": r.get("owner_name", "")} for r in rows}
        else:
            tools_dict = {}

        logger.info(f'apps_dict:{apps_dict}')
        logger.info(f'tools_dict:{tools_dict}')
        logger.info(f'app_ids:{app_ids}')
        logger.info(f'tool_app_ids:{tool_api_provider_ids}')
        items = [
            ApplicationAuditItem.model_validate({
                **item.__dict__,
                "id": str(item.id),
                "app_name": tools_dict.get(item.app_id, {}).get("app_name",
                                                                "") if item.app_type == AppMode.TOOL.value else apps_dict.get(
                    item.app_id, {}).get("app_name", ""),
                "app_attr": tools_dict.get(item.app_id, {}).get("app_attr",
                                                                "") if item.app_type == AppMode.TOOL.value else apps_dict.get(
                    item.app_id, {}).get("app_attr", ""),
                "app_desc": tools_dict.get(item.app_id, {}).get("app_desc",
                                                                "") if item.app_type == AppMode.TOOL.value else apps_dict.get(
                    item.app_id, {}).get("app_desc", ""),
                "app_creator": tools_dict.get(item.app_id, {}).get("app_creator",
                                                                   "") if item.app_type == AppMode.TOOL.value else apps_dict.get(
                    item.app_id, {}).get("app_creator", ""),
                "owner_name": app_id_owner.get(item.app_id, {}).get("owner_name",),
                "owner_id": app_id_owner.get(item.app_id, {}).get("owner_id", )
            })
            for item in orm_results
        ]
        big_model_dict = {}
        logger.info("审批数据信息===========================================================")
        for t in orm_results:
            logger.info(type(t.id))
            logger.info(str(t.id))
            logger.info(t.tool_param)
            logger.info("审批数据信息===========================================================")
            if t.tool_param:
                big_model_dict[str(t.id)] = t.tool_param
        logger.info(big_model_dict)
        logger.info("结束数据id===========================================================")
        for t in items:
            if t.app_type == AppMode.BIGMODEL.value:
                logger.info(t.id)
                logger.info(big_model_dict.get(t.id, {}))
                logger.info(type(big_model_dict.get(t.id, {})))
                dict_param = json.loads(big_model_dict.get(t.id, {}))
                print(type(dict_param))
                t.app_name = str(dict_param.get("name", ""))
                t.app_desc = str(dict_param.get("description",""))
        # 构建分页响应对象
        response = ApplicationAuditPageResp(
            page=req.page,
            limit=req.limit,
            total=int(total) if total else 0,
            has_more=bool(items and len(items) == req.limit),
            data=items
        )

        return response

    async def convert_to_uuid_list(self, ids):
        uuid_list = []
        for id in ids:
            try:
                uuid_obj = uuid.UUID(id)
                uuid_list.append(uuid_obj)
            except ValueError:
                raise ValueError(f"Invalid UUID '{id}'")
        return uuid_list

    async def is_auditing_async(self, app_id: str):
        audit = await self.session.execute(select(ApplicationAudit).where(ApplicationAudit.app_id == app_id),
                                           ApplicationAudit.status == AuditStatus.PENDING.value)
        audit = audit.scalars().all()
        if len(audit) > 0:
            return True
        return False

    async def check_has_app_id_auth(self, employee_number, process_id):
        result = await self.session.execute(
            select(ApplicationAudit)
                .where(ApplicationAudit.id == uuid.UUID(process_id))
                .where(ApplicationAudit.reviewer_id == employee_number)
        )
        dbApplicationAudit = result.scalars().first()

        if dbApplicationAudit is None:
            raise NotFoundError(f"No application audit auth")
        return dbApplicationAudit


    """
     全流程审核接口
    """
    async def application_process_all_page_list(self, req: ApplicationAuditPageReq,
                                            current_user: Account = Depends(login_user)):
        logger.info(f'req=====>:{req}')
        logger.info(f'current_user=====>:{current_user.id}:{current_user.employee_number}')
        super_read_auth = await self.user_permissions_service.check_user_is_super_admin_read_auth(
            current_user.employee_number)
        super_edit_auth = await self.user_permissions_service.check_user_is_super_admin_edit_auth(
            current_user.employee_number)

        filters: List[BinaryExpression] = []

        filters.append(ApplicationAudit.reviewer_id == current_user.employee_number)

        # filters.append(ApplicationAudit.status == 'pending')
        if req.space_id:
            filters.append(ApplicationAudit.space_id == req.space_id)
        if req.space_name:
            filters.append(ApplicationAudit.space_name == req.space_name)
        if req.applicant_id:
            filters.append(ApplicationAudit.applicant_id == req.applicant_id)
        if req.applicant:
            filters.append(ApplicationAudit.applicant == req.applicant)
        if req.reason:
            filters.append(ApplicationAudit.reason == req.reason)
        if req.app_id:
            filters.append(ApplicationAudit.app_id == req.app_id)

        # 这块逻辑感觉是错的  因为我看不懂  --hesh
        if req.app_type:
            app_type_list = req.app_type if req.app_type is not None else []
            filters.append(ApplicationAudit.app_type.in_(app_type_list))

        if req.application_type:
            application_type_list = req.application_type if req.application_type is not None else []
            filters.append(ApplicationAudit.application_type.in_(application_type_list))

        if req.denial_reason:
            filters.append(ApplicationAudit.denial_reason == req.denial_reason)

        query = (select(ApplicationAudit))
        if filters:
            query = query.where(and_(*filters))

        total = await self.session.scalar(select(func.count()).select_from(ApplicationAudit).where(and_(*filters)))
        paginated_query = (
            query
                .offset((req.page - 1) * req.limit)
                .limit(req.limit)
        )
        logger.info(f'paginated_query:{paginated_query}')
        results: Result = await self.session.execute(paginated_query)
        orm_results = results.scalars().all()
        app_ids = []
        tool_api_provider_ids = []
        for item in orm_results:
            if item.app_type == AppMode.TOOL.value:
                tool_api_provider_ids.append(item.app_id)
            else:
                app_ids.append(item.app_id)
        apps_dict = {}
        tools_dict = {}
        if app_ids:
            # app_ids_uuid = await self.convert_to_uuid_list(app_ids)
            app_query = select(App).where(App.id.in_(app_ids))
            apps_result = await self.session.execute(app_query)
            for app in apps_result.scalars().all():
                account_query = await self.session.execute(
                    select(Account).filter(Account.id == app.account_id))
                account_item = account_query.scalar_one_or_none()
                app_creator = account_item.username

                apps_dict[app.id] = {
                    "app_name": app.name,
                    "app_attr": app.mode,
                    "app_desc": app.description,
                    "app_creator": app_creator
                }
        else:
            apps_dict = {}

        # 查询 ApiToolProvider 表
        if tool_api_provider_ids:
            # tool_app_ids_uuid = await self.convert_to_uuid_list(tool_app_ids)
            tool_query = select(ApiToolProvider).where(ApiToolProvider.id.in_(tool_api_provider_ids))
            tools_result = await self.session.execute(tool_query)
            for tool in tools_result.scalars().all():
                account_query = await self.session.execute(
                    select(Account).filter(Account.id == tool.user_id))
                account_item = account_query.scalar_one_or_none()
                app_creator = account_item.username
                tools_dict[tool.id] = {
                    "app_name": tool.name,
                    "app_attr": "tool",  # ToolApp 表中没有直接对应的字段
                    "app_desc": tool.description,
                    "app_creator": app_creator  # ToolApp 表中没有直接对应的字段
                }
        else:
            tools_dict = {}

        logger.info(f'apps_dict:{apps_dict}')
        logger.info(f'tools_dict:{tools_dict}')
        logger.info(f'app_ids:{app_ids}')
        logger.info(f'tool_app_ids:{tool_api_provider_ids}')
        items = [
            ApplicationAuditItem.model_validate({
                **item.__dict__,
                "id": str(item.id),
                "app_name": tools_dict.get(item.app_id, {}).get("app_name",
                                                                "") if item.app_type == AppMode.TOOL.value else apps_dict.get(
                    item.app_id, {}).get("app_name", ""),
                "app_attr": tools_dict.get(item.app_id, {}).get("app_attr",
                                                                "") if item.app_type == AppMode.TOOL.value else apps_dict.get(
                    item.app_id, {}).get("app_attr", ""),
                "app_desc": tools_dict.get(item.app_id, {}).get("app_desc",
                                                                "") if item.app_type == AppMode.TOOL.value else apps_dict.get(
                    item.app_id, {}).get("app_desc", ""),
                "app_creator": tools_dict.get(item.app_id, {}).get("app_creator",
                                                                   "") if item.app_type == AppMode.TOOL.value else apps_dict.get(
                    item.app_id, {}).get("app_creator", "")
            })
            for item in orm_results
        ]
        big_model_dict = {}
        logger.info("审批数据信息===========================================================")
        for t in orm_results:
            logger.info(type(t.id))
            logger.info(str(t.id))
            logger.info(t.tool_param)
            logger.info("审批数据信息===========================================================")
            if t.tool_param:
                big_model_dict[str(t.id)] = t.tool_param
        logger.info(big_model_dict)
        logger.info("结束数据id===========================================================")
        for t in items:
            if t.app_type == AppMode.BIGMODEL.value:
                logger.info(t.id)
                logger.info(big_model_dict.get(t.id, {}))
                logger.info(type(big_model_dict.get(t.id, {})))
                dict_param = json.loads(big_model_dict.get(t.id, {}))
                print(type(dict_param))
                t.app_name = str(dict_param.get("name", ""))
                t.app_desc = str(dict_param.get("description",""))
        # 构建分页响应对象
        response = ApplicationAuditPageResp(
            page=req.page,
            limit=req.limit,
            total=int(total) if total else 0,
            has_more=bool(items and len(items) == req.limit),
            data=items
        )

        return response