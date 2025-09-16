import json
import logging
from datetime import datetime
from typing import Optional, List

from fastapi import Depends, HTTPException
from rich import status
from sqlalchemy import delete, insert
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform_basic.exceptions.services.user_permissions import UserPermissionError
from agent_platform_basic.extensions.ext_redis import async_redis_client
from agent_platform_basic.libs import DbUtils
from agent_platform_basic.models.db_model import Account
from agent_platform_basic.models.db_model.global_user_permissions import GlobalUserPermissions
from agent_platform_basic.models.db_model.user_permissions import UserPermissions
from agent_platform_service.fastapi_fields.req.console.user_permissions_req import UserPermissionReq
from agent_platform_service.fastapi_fields.resp.console.user_permissions_resp import UserPermission, \
    UserPermissionsResp, UserPermissionsDetailResp
from agent_platform_service.services.account_service import TenantService

logger = logging.getLogger(__name__)


class UserPermissionsService:

    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

    """
    校验是否是拥有超管读权限
    """

    async def check_user_is_super_admin_read_auth(self, user_id: str):
        # 缓存键名
        cache_key = f"user_is_super_can_read:{user_id}"
        # 先从缓存中获取数据 todo 数据同步一致性保证
        cache_value = await async_redis_client.get(cache_key)
        if cache_value is not None:
            permissions_data = json.loads(cache_value)
            if permissions_data.get('can_view_all', False):
                return True
            return False
        # 如果缓存中没有数据，从数据库查询
        result_global = await self.session.execute(select(GlobalUserPermissions)
                                                   .where(GlobalUserPermissions.user_id == user_id)
                                                   .where(GlobalUserPermissions.can_view_all == True))
        global_reader = result_global.scalars().first()
        if global_reader:
            # 存储到缓存中
            permissions_data = {
                "can_view_all": global_reader.can_view_all
            }
            # todo 失败了暂时不考虑
            await async_redis_client.set(cache_key, json.dumps(permissions_data))
            return True
        return False

    """
       校验是否是拥有超管写权限
    """

    async def check_user_is_super_admin_edit_auth(self, user_id: str):
        # 缓存键名
        cache_key = f"use_is_super_can_edit:{user_id}"
        # 先从缓存中获取数据  todo 数据同步一致性保证
        cache_value = await async_redis_client.get(cache_key)
        if cache_value is not None:
            permissions_data = json.loads(cache_value)
            if permissions_data.get('can_edit_all', False):
                return True
            return False

        # 如果缓存中没有数据，从数据库查询
        result_global = await self.session.execute(
            select(GlobalUserPermissions)
                .where(GlobalUserPermissions.user_id == user_id)
                .where(GlobalUserPermissions.can_edit_all.is_(True))
        )
        global_admin = result_global.scalars().first()

        if global_admin:
            # 存储到缓存中
            permissions_data = {
                "can_edit_all": global_admin.can_edit_all
            }
            # todo 失败了暂时不考虑
            await async_redis_client.set(cache_key, json.dumps(permissions_data))
            return True
        return False

    """
    编辑权限校验
    """

    async def check_user_edit_auth(self, user_id: str, app_id: Optional[str] = None) -> bool:
        # 缓存键名
        cache_key = f"user_can_edit:{user_id}"
        # 先从缓存中获取数据  todo 数据同步一致性保证
        cache_value = await async_redis_client.get(cache_key)
        if cache_value is not None:
            permissions_data = json.loads(cache_value)

            # 如果提供了 app_id，检查特定应用的编辑权限
            if app_id:
                for perm in permissions_data.get('userpermissionsList', []):
                    if perm.get('appId') == app_id and perm.get('can_edit', False):
                        return True
                logger.error("check_user_edit_auth.not app_id edit auth")
                raise UserPermissionError('not app_id edit auth')
            # 如果没有提供 app_id 则没有编辑权限
            return False

        if app_id:
            # 如果提供了 app_id，查询所有相关的权限记录
            result_app = await self.session.execute(select(UserPermissions)
                                                    .where(UserPermissions.user_id == user_id)
                                                    .where(UserPermissions.can_edit.is_(True)))
            app_permissions = result_app.scalars().all()

            if not app_permissions:
                logger.error("no permissions found for app_id")
                raise UserPermissionError('no permissions found for app_id')

            userpermissions_list = [
                {
                    "appId": perm.app_id,
                    "can_edit": perm.can_edit
                }
                for perm in app_permissions
            ]

            # 检查特定应用的编辑权限
            for perm in userpermissions_list:
                if perm.get('appId') == app_id and perm.get('can_edit', False):
                    # 存储到缓存中
                    permissions_data = {
                        "userpermissionsList": userpermissions_list
                    }
                    await async_redis_client.set(cache_key, json.dumps(permissions_data))
                    return True
            logger.error("check_user_edit_auth.not app_id edit auth")
            raise UserPermissionError('not app_id edit auth')

        return False

    """
    读权限校验
    """

    async def check_user_read_auth(self, user_id: str, app_id: Optional[str] = None) -> List[str]:
        # 缓存键名
        cache_key = f"user_can_read:{user_id}"
        # 先从缓存中获取数据 todo 数据同步一致性保证
        cache_value = await async_redis_client.get(cache_key)
        if cache_value is not None:
            permissions_data = json.loads(cache_value)
            if app_id is None:
                # 如果 app_id 为空，返回所有授权的 appId
                return [perm['appId'] for perm in permissions_data.get('userpermissionsList', []) if
                        perm.get('can_view', False)]
                # 如果提供了 app_id，检查特定应用的读取权限
            for perm in permissions_data.get('userpermissionsList', []):
                if perm.get('appId') == app_id and perm.get('can_view', False):
                    return [app_id]
            logger.error("check_user_read_auth.not app_id read auth")
            raise UserPermissionError('not app_id read auth')

        # 查询所有相关的权限记录
        result_app = await self.session.execute(select(UserPermissions)
                                                .where(UserPermissions.user_id == user_id)
                                                .where(UserPermissions.can_view == True))
        app_permissions = result_app.scalars().all()

        if not app_permissions:
            logger.error("check_user_read_auth.no permissions found for the user")
            raise UserPermissionError('no permissions found for the user')

        userpermissions_list = [
            {
                "appId": perm.app_id,
                "can_view": perm.can_view
            }
            for perm in app_permissions
        ]

        # 收集所有有权限的 appId 列表
        authorized_apps = [perm['appId'] for perm in userpermissions_list if perm.get('can_view', False)]

        # 如果 app_id 不为 None，则检查特定应用的读取权限
        if app_id is not None:
            has_permission_for_app = any(
                perm.get('appId') == app_id and perm.get('can_view', False)
                for perm in userpermissions_list
            )
            if not has_permission_for_app:
                raise UserPermissionError('not app_id read auth')

        # 存储到缓存中
        permissions_data = {
            "userpermissionsList": userpermissions_list
        }
        await async_redis_client.set(cache_key, json.dumps(permissions_data))

        return authorized_apps

    async def user_permissions_edit_syn_redis(self, app_id: str, result_existing: List[UserPermissions],
                                              app_permissions: List[UserPermission]):
        if result_existing:
            for perm in result_existing:
                old_read_cache_key = f"user_can_read:{perm.user_id}"
                old_edit_cache_key = f"user_can_edit:{perm.user_id}"
                await async_redis_client.delete(old_read_cache_key)
                await async_redis_client.delete(old_edit_cache_key)
        if app_permissions:
            for perm in app_permissions:
                # 删除旧的缓存键
                old_read_cache_key = f"user_can_read:{perm.user_id}"
                old_edit_cache_key = f"user_can_edit:{perm.user_id}"
                await async_redis_client.delete(old_read_cache_key)
                await async_redis_client.delete(old_edit_cache_key)
            # 筛选出 can_view=True 的列表
            viewable_users = [perm for perm in app_permissions if perm.can_view]

            # 筛选出 can_edit=True 的列表
            editable_users = [perm for perm in app_permissions if perm.can_edit]

            for perm in viewable_users:
                if perm.can_view:
                    await self.check_user_read_auth(perm.user_id, app_id)

            for perm in editable_users:
                if perm.can_view:
                    await self.check_user_edit_auth(perm.user_id, app_id)

    """
    增删改查逻辑
    """

    async def user_permissions_edit(self, app_id: str, user_permission_list: List[UserPermissionReq], username: str,
                                    employee_number: str):
        # await self.check_user_edit_auth(employee_number,app_id)
        # 如果 user_permission_list 为空，则删除所有对应 app_id 的记录
        result_existing = await self.session.execute(
            select(UserPermissions).where(UserPermissions.app_id == app_id)
        )
        existing_permissions = {perm.user_id for perm in result_existing.scalars().all()}
        if not user_permission_list:
            try:
                await self.session.execute(
                    delete(UserPermissions).where(UserPermissions.app_id == app_id)
                )
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        else:
            new_permissions = {perm.user_id for perm in user_permission_list} if user_permission_list else set()

            to_delete = existing_permissions - new_permissions
            to_update = existing_permissions & new_permissions
            to_add = new_permissions - existing_permissions

            # 删除不需要的用户权限
            for user_id in to_delete:
                try:
                    await self.session.execute(
                        delete(UserPermissions)
                            .where(UserPermissions.user_id == user_id)
                            .where(UserPermissions.app_id == app_id)
                    )
                except Exception as e:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
            for user_id in to_update:
                try:
                    await self.session.execute(
                        delete(UserPermissions)
                            .where(UserPermissions.user_id == user_id)
                            .where(UserPermissions.app_id == app_id)
                    )
                except Exception as e:
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

            # 添加新的用户权限
            for perm in user_permission_list:
                if perm.user_id in to_add:
                    try:
                        await self.session.execute(
                            insert(UserPermissions),
                            {
                                "user_id": perm.user_id,
                                "app_id": app_id,
                                "can_view": perm.can_view,
                                "can_edit": perm.can_edit,
                                "operator": username,
                                "created_at": datetime.now()
                            }
                        )
                    except IntegrityError as e:
                        # 处理主键冲突等情况
                        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e.orig))
                    except Exception as e:
                        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
                if perm.user_id in to_update:
                    try:
                        await self.session.execute(
                            insert(UserPermissions),
                            {
                                "user_id": perm.user_id,
                                "app_id": app_id,
                                "can_view": perm.can_view,
                                "can_edit": perm.can_edit,
                                "operator": username,
                                "created_at": datetime.now()
                            }
                        )
                    except IntegrityError as e:
                        # 处理主键冲突等情况
                        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e.orig))
                    except Exception as e:
                        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        await self.session.commit()
        await self.user_permissions_edit_syn_redis(app_id, result_existing, user_permission_list)
        return UserPermissionsDetailResp(app_id=app_id)

    async def user_permissions_api_get(self, app_id: str, employee_number: str):

        query = select(UserPermissions).where(UserPermissions.app_id == app_id)
        if employee_number and employee_number != "":
            query = query.where(UserPermissions.user_id == employee_number)
        result_app = await self.session.execute(query)

        app_permissions = result_app.scalars().all()
        user_permissions_list = []
        if app_permissions:
            user_ids = [permission.user_id for permission in app_permissions]
            accounts = []
            if user_ids:
                logger.info(f'user_ids:{user_ids}')
                result_accounts = await self.session.execute(select(Account).where(Account.employee_number.in_(user_ids)))
                accounts = result_accounts.scalars().all()
                logger.info(f'accounts:{accounts}')
            user_permissions_list = [
                UserPermission(
                    user_id=permission.user_id,
                    user_name=next((account.username for account in accounts if account.employee_number == permission.user_id),
                                   None),
                    app_id=permission.app_id,
                    can_view=permission.can_view,
                    can_edit=permission.can_edit,
                    operator=permission.operator,
                    created_at=permission.created_at
                ) for permission in app_permissions
            ]
        else:
            # 如果 app_permissions 为空，则直接返回空的响应模型
            user_permissions_list = []

        logger.info(f'app_id:{app_id}')
        logger.info(f'user_permissions_list:{user_permissions_list}')
        return UserPermissionsResp(user_permissions_list=user_permissions_list)

    async def user_super_permissions_api_get(self, employee_number: str):
        # 查询数据库
        result_global = await self.session.execute(
            select(GlobalUserPermissions).where(GlobalUserPermissions.user_id == employee_number)
        )
        global_reader = result_global.scalars().all()

        user_permissions_list = [
            UserPermission(
                user_id=permission.user_id,
                can_view=permission.can_view_all,
                can_edit=permission.can_edit_all,
                operator=permission.operator,
                created_at=permission.created_at
            ) for permission in global_reader
        ]

        return UserPermissionsResp(user_permissions_list=user_permissions_list)
