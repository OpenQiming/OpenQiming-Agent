from datetime import datetime, timedelta

import httpx
from fastapi import Depends
from sqlalchemy import  select, func
from sqlalchemy.ext.asyncio import AsyncSession
from agent_platform_basic.libs import DbUtils
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.models.db_model.model import App
from agent_platform_basic.models.db_model import Account
from sqlalchemy.future import select as future_select


class StatisticsService:
    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session

    STATISTICS_URL = (f"{agent_platform_config.BASE_TOOLCHAIN_INTERFACE_ENDPOINT}/"
                      f"{agent_platform_config.INTF_RESTFUL_SERVICE}/"
                      f"{agent_platform_config.TOOL_CHAIN_STATISTICS_PATH}")
    headers = {
        "Content-Type": "application/json",
    }
    async def get_app_statistics(self) -> dict:
        """
        获取 app 的数量
        返回例如: dict{
            agent: 100,
            workflow: 100
        }
        """
        workflow_count = await self.session.execute(select(func.count(App.id)).filter(App.mode == "workflow"))
        workflow_count = workflow_count.scalar_one()

        agent_count = await self.session.execute(select(func.count(App.id)).filter(App.mode == "agent-chat"))
        agent_count = agent_count.scalar_one()

        return {
            "agent": agent_count,
            "workflow": workflow_count
        }

    async def get_app_by_province_statistics(self, type: str) -> dict:
        """
        获取各省份的构建的app的数量，包含draft和publibshed
        如果 type==ALL, 表示累计所有的app; 如果 type==MONTH, 表示只查询当月的app
        返回一个dict, key 为 employee_number 的后两位， value 为 该省份的 app 数量
        """

        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)

        # 使用子查询来获取 accountid 的后两位字符
        if type == 'ALL':
            subquery = (
                future_select(
                    App.id,
                    func.right(Account.employee_number, 2).label('suffix')
                )
                .join(Account, App.account_id == Account.id)
                .subquery()
            )
        elif type == 'MONTH':
            subquery = (
                future_select(
                    App.id,
                    func.right(Account.employee_number, 2).label('suffix')
                )
                .join(Account, App.account_id == Account.id)
                .where(App.created_at >= month_start)
                .where(App.created_at < month_end)
                .subquery()
            )
        else:
            raise ValueError("Invalid type. Use 'ALL' or 'MONTH'.")
        # 主查询，根据后缀分组并计算数量
        query = (
            future_select(
                subquery.c.suffix,
                func.count(subquery.c.id).label('count')
            )
            .group_by(subquery.c.suffix)
        )
        result = await self.session.execute(query)
        result_dict = {row[0]: row[1] for row in result}
        return result_dict
    @staticmethod
    def get_month_start_time():
        # 获取当前时间
        now = datetime.now()
        # 计算本月的起始时间
        month_start = datetime(now.year, now.month, 1)
        return month_start

    async def add_api(self, json=None):
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.STATISTICS_URL, headers=self.headers, json=json)

        return response.json()