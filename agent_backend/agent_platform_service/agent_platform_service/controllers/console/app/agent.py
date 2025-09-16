from flask_restful import Resource, reqparse

from agent_platform_basic.libs.helper import uuid_value
from agent_platform_basic.libs.login import login_required
from agent_platform_basic.models.db_model import Account
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.controllers.console import api, console_api
from agent_platform_service.controllers.console.app.wraps import get_app_model, get_app_model_async
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.services.agent_service import AgentService, AsyncAgentService
from sqlalchemy.ext.asyncio import AsyncSession
from agent_platform_basic.libs import DbUtils
from fastapi import Depends

from agent_platform_service.services.auth_service import login_user


class AgentLogApi(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model(mode=[AppMode.AGENT_CHAT])
    def get(self, app_model):
        """Get agent logs"""
        parser = reqparse.RequestParser()
        parser.add_argument('message_id', type=uuid_value, required=True, location='args')
        parser.add_argument('conversation_id', type=uuid_value, required=True, location='args')

        args = parser.parse_args()

        return AgentService.get_agent_logs(
            app_model,
            args['conversation_id'],
            args['message_id']
        )

@console_api.get('/apps/{app_id}/agent/logs')
async def agent_log_api(app_id: str,
                        message_id: str,
                        conversation_id: str,
                        agent_service: AsyncAgentService = Depends(
                            AsyncAgentService),
                        current_user: Account = Depends(login_user),
                        ):
    app_model = await get_app_model_async(app_id=app_id, mode=AppMode.AGENT_CHAT)
    resukt = await agent_service.get_agent_logs(app_model, conversation_id, message_id, current_user)
    return resukt

@console_api.get('/apps/agent/alllogs')
async def agent_alllog_api(app_id: str = "", page: int = 1, page_size: int = 20, keyword: str = '',
                           agent_service: AsyncAgentService = Depends(
                            AsyncAgentService),):
    resukt = await agent_service.get_agent_alllogs(app_id, page, page_size, keyword)
    return resukt

@console_api.get('/apps/workflow/alllogs')
async def workflow_alllog_api(app_id: str = "", page: int = 1, page_size: int = 20, keyword: str = '',
                           agent_service: AsyncAgentService = Depends(
                            AsyncAgentService),):

    resukt = await agent_service.get_workflow_alllog(app_id, page, page_size, keyword)
    return resukt

@console_api.get('/apps/agent_workflow/log')
async def agent_workflow_log_api(tool_name: str = "",agent_service: AsyncAgentService = Depends(
                            AsyncAgentService), current_user: Account = Depends(login_user),):

    resukt = await agent_service.get_aget_workflow_log(tool_name, current_user)
    return resukt

# api.add_resource(AgentLogApi, '/apps/<uuid:app_id>/agent/logs')
