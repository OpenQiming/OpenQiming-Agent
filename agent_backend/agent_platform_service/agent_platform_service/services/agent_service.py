import pytz
from agent_platform_core.models.db_model.tools import WorkflowToolProvider
from flask_login import current_user

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.models.db_model import Account
from agent_platform_core.app.app_config.easy_ui_based_app.agent.manager import AgentConfigManager
from agent_platform_core.models.db_model.model import App, Conversation, EndUser, Message, MessageAgentThought, \
    AppModelConfig
from agent_platform_core.models.db_model.workflow import WorkflowNodeExecution, WorkflowAppLog, WorkflowRun
from agent_platform_core.tools.tool_manager import ToolManager
from agent_platform_core.tools.async_tool_manager import AsyncToolManager
from sqlalchemy.ext.asyncio import AsyncSession
from agent_platform_basic.libs import DbUtils
from fastapi import Depends
from sqlalchemy import select, or_, func

from agent_platform_service.fields.app_model_config_async import AppModelConfigAsync
from agent_platform_service.fields.message_agent_thought_async import MessageAgentThoughtAsync
from agent_platform_service.fields.model_async.app_async import AppAsync
from agent_platform_service.fields.model_async.conversation_async import ConversationAsync


class AsyncAgentService:

    def __init__(self,
                 session: AsyncSession = Depends(DbUtils.get_db_async_session),
                 conversation_service: ConversationAsync = Depends(ConversationAsync),
                 app_model_config_async: AppModelConfigAsync = Depends(AppModelConfigAsync),
                 agent_thought_async: MessageAgentThoughtAsync = Depends(MessageAgentThoughtAsync),
                 app_async: AppAsync = Depends(AppAsync)):
        self.session = session
        self.conversation_service = conversation_service
        self.app_model_config_async = app_model_config_async
        self.agent_thought_async = agent_thought_async
        self.app_async = app_async

    async def get_agent_logs(self,
                       app_model: App,
                       conversation_id: str,
                       message_id: str,
                       current_user: Account) -> dict:
        """
        Service to get agent logs
        """
        conversation = await self.session.execute(select(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.app_id == app_model.id,
        ))
        conversation = conversation.scalars().first()

        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")

        message = await self.session.execute(select(Message).filter(
            Message.id == message_id,
            Message.conversation_id == conversation_id,
        ))
        message: Message = message.scalars().first()

        if not message:
            raise ValueError(f"Message not found: {message_id}")

        agent_thoughts: list[MessageAgentThought]  = await self.conversation_service.agent_thoughts_async(message_id)

        if conversation.from_end_user_id:
            # only select name field
            executor = await self.session.execute(select(EndUser, EndUser.name).filter(
                EndUser.id == conversation.from_end_user_id
            ))
            executor = executor.scalars().first()
        else:
            executor = await self.session.execute(select(Account, Account.name).filter(
                Account.id == conversation.from_account_id
            ))
            executor = executor.scalars().first()

        if executor:
            executor = executor.name
        else:
            executor = 'Unknown'

        timezone = pytz.timezone(current_user.timezone)

        app_model_config: AppModelConfig = await self.app_model_config_async.get_app_model_config(app_model)
        agent_mode_dict = self.app_model_config_async.agent_mode_dict(app_model_config)

        result =  {
            'meta': {
                'status': 'success',
                'executor': executor,
                'start_time': message.created_at.astimezone(timezone).isoformat(),
                'elapsed_time': message.provider_response_latency,
                'total_tokens': message.answer_tokens + message.message_tokens,
                'agent_mode': agent_mode_dict.get('strategy', 'react'),
                'iterations': len(agent_thoughts),
            },
            'iterations': [],
            'files': await self.conversation_service.message_files_sync(message),
        }

        agent_config = await self.app_async.draft_app_model_config(app=app_model)
        agent_config = AgentConfigManager.convert(agent_config.to_dict())
        agent_tools = agent_config.tools

        def find_agent_tool(tool_name: str):
            for agent_tool in agent_tools:
                if agent_tool.tool_name == tool_name:
                    return agent_tool

        for agent_thought in agent_thoughts:
            tools = await self.agent_thought_async.tools(agent_thought)
            tool_labels = await self.agent_thought_async.tool_labels(agent_thought)
            tool_meta = await self.agent_thought_async.tool_meta(agent_thought)
            tool_inputs = await self.agent_thought_async.tool_inputs_dict(agent_thought)
            tool_outputs = await self.agent_thought_async.tool_outputs_dict(agent_thought)
            tool_calls = []
            for tool in tools:
                tool_name = tool
                tool_label = tool_labels.get(tool_name, tool_name)
                tool_input = tool_inputs.get(tool_name, {})
                tool_output = tool_outputs.get(tool_name, {})
                tool_meta_data = tool_meta.get(tool_name, {})
                tool_config = tool_meta_data.get('tool_config', {})
                tool_icon = ''
                # if tool_config.get('tool_provider_type', '') != 'dataset-retrieval':
                #     tool_icon = await AsyncToolManager.get_tool_icon(
                #         tenant_id=app_model.tenant_id,
                #         provider_type=tool_config.get('tool_provider_type', ''),
                #         provider_id=tool_config.get('tool_provider_id', ''),
                #     )
                #     if not tool_icon:
                #         tool_entity = find_agent_tool(tool_name)
                #         if tool_entity:
                #             tool_icon = await AsyncToolManager.get_tool_icon(
                #                 tenant_id=app_model.tenant_id,
                #                 provider_type=tool_entity.provider_type,
                #                 provider_id=tool_entity.provider_id,
                #             )
                # else:
                #     tool_icon = ''

                tool_calls.append({
                    'status': 'success' if not tool_meta_data.get('error') else 'error',
                    'error': tool_meta_data.get('error'),
                    'time_cost': tool_meta_data.get('time_cost', 0),
                    'tool_name': tool_name,
                    'tool_label': tool_label,
                    'tool_input': tool_input,
                    'tool_output': tool_output,
                    'tool_parameters': tool_meta_data.get('tool_parameters', {}),
                    'tool_icon': tool_icon,
                })

            result['iterations'].append({
                'tokens': agent_thought.tokens,
                'tool_calls': tool_calls,
                'tool_raw': {
                    'inputs': agent_thought.tool_input,
                    'outputs': agent_thought.observation,
                },
                'thought': agent_thought.thought,
                'created_at': agent_thought.created_at.isoformat(),
                'files': agent_thought.files,
            })

        return result

    async def get_agent_alllogs(self, app_id, page, page_size, keyword):
        offset = (page - 1) * page_size

        base_stmt = (
            select(Message, App.name.label("app_name"))
            .join(Conversation, Message.conversation_id == Conversation.id)
            .join(App, Conversation.app_id == App.id)
        )

        # 添加过滤条件
        if keyword:
            base_stmt = base_stmt.filter(
                or_(
                    Message.query.ilike(f"%{keyword}%"),
                    App.name.ilike(f"%{keyword}%")
                )
            )
        if app_id:
            base_stmt = base_stmt.filter(App.id==app_id)

        # 获取分页数据
        stmt = base_stmt.order_by(Message.created_at.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        rows = result.all()

        # 获取总数（去掉 offset/limit）
        count_stmt = (
            select(func.count())
            .select_from(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .join(App, Conversation.app_id == App.id)
        )
        if keyword:
            count_stmt = count_stmt.filter(
                or_(
                    Message.query.ilike(f"%{keyword}%"),
                    App.name.ilike(f"%{keyword}%")
                )
            )

        if app_id:
            count_stmt = count_stmt.filter(App.id==app_id)
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar()

        # 处理返回数据
        result_list = []
        for message, app_name in rows:
            data = message.to_dict()

            if "created_at" in data:
                dt = data["created_at"]
                if isinstance(dt, str):
                    data["created_at"] = dt.replace("T", " ")
                elif dt:
                    data["created_at"] = dt.isoformat(sep=' ').split('.')[0]

            data["app_name"] = app_name
            result_list.append(data)

        return {
            "total": total,
            "items": result_list,
            "page": page,
            "page_size": page_size
        }


    async def get_workflow_alllog(self, app_id, page, page_size, keyword):
        offset = (page - 1) * page_size


        base_stmt = (
            select(WorkflowRun, App.name.label("app_name"))
            .join(App, WorkflowRun.app_id == App.id)
        )

        if keyword:
            base_stmt = base_stmt.filter(
                or_(
                    App.name.ilike(f"%{keyword}%")
                )
            )

        if app_id:
            base_stmt = base_stmt.filter(App.id==app_id)

        stmt = base_stmt.order_by(WorkflowRun.created_at.desc()).offset(offset).limit(page_size)
        result = await self.session.execute(stmt)
        rows = result.all()

        count_stmt = (
            select(func.count())
            .select_from(WorkflowRun)
            .join(App, WorkflowRun.app_id == App.id)
        )
        if keyword:
            count_stmt = count_stmt.filter(
                or_(
                    App.name.ilike(f"%{keyword}%")
                )
            )
        if app_id:
            count_stmt = count_stmt.filter(App.id==app_id)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar()

        # 处理返回数据
        result_list = []
        for message, app_name in rows:
            data = message.to_dict()
            if "created_at" in data:
                dt = data["created_at"]
                if isinstance(dt, str):
                    data["created_at"] = dt.replace("T", " ")
                elif dt:
                    data["created_at"] = dt.isoformat(sep=' ').split('.')[0]

            data["app_name"] = app_name
            result_list.append(data)

        return {
            "total": total,
            "items": result_list,
            "page": page,
            "page_size": page_size
        }


    async def get_aget_workflow_log(self, tool_name, user):
        # 查询 tool_name 对应的 provider
        stmt_provider = select(WorkflowToolProvider).filter(WorkflowToolProvider.name == tool_name).order_by(WorkflowToolProvider.created_at.desc())
        result_provider = await self.session.execute(stmt_provider)
        provider = result_provider.scalars().first()

        if not provider:
            raise ValueError(f"无法找到 agent插件: {tool_name}")

        workflow_id = provider.workflow_id
        app_id = provider.app_id

        # 2. 查询最近的 workflow_run_id（通过 WorkflowNodeExecution）
        stmt_recent_run = (
            select(WorkflowNodeExecution.workflow_run_id)
            .filter(
                WorkflowNodeExecution.app_id == app_id,
                WorkflowNodeExecution.workflow_id == workflow_id,
            )
            .order_by(WorkflowNodeExecution.created_at.desc())
            .limit(1)
        )
        result_recent_run = await self.session.execute(stmt_recent_run)
        recent_run = result_recent_run.scalar_one_or_none()

        if not recent_run:
            return []  # 无执行记录

        # # 查询 WorkflowAppLog
        # stmt_log = (
        #     select(WorkflowAppLog)
        #     .filter(
        #         WorkflowAppLog.app_id == app_id,
        #         WorkflowAppLog.workflow_id == workflow_id,
        #         # WorkflowAppLog.created_by == user.id,
        #     )
        #     .order_by(WorkflowAppLog.created_at.desc())  # 注意字段改为 WorkflowAppLog 的
        # )
        # result_log = await self.session.execute(stmt_log)
        # workflow_app_log = result_log.scalars().first()
        #
        # if not workflow_app_log:
        #     return []  # 或 raise 异常

        # workflow_run_id = workflow_app_log.workflow_run_id

        workflow_run_id = recent_run

        # 查询 WorkflowNodeExecution
        stmt_nodes = (
            select(WorkflowNodeExecution)
            .filter(
                WorkflowNodeExecution.app_id == app_id,
                WorkflowNodeExecution.workflow_id == workflow_id,
                WorkflowNodeExecution.workflow_run_id == workflow_run_id
            )
        )
        result_nodes = await self.session.execute(stmt_nodes)
        workflow_node_executions = result_nodes.scalars().all()

        # result = []
        # for w in workflow_node_executions:
        #     result.append({
        #         "node_type": w.node_type,
        #         "title": w.title,
        #         "inputs": w.inputs,
        #         "outputs": w.outputs
        #     })
        return [i.to_dict() for i in workflow_node_executions]

class AgentService:
    @classmethod
    def get_agent_logs(cls, app_model: App,
                       conversation_id: str,
                       message_id: str) -> dict:
        """
        Service to get agent logs
        """
        conversation: Conversation = db.session.query(Conversation).filter(
            Conversation.id == conversation_id,
            Conversation.app_id == app_model.id,
        ).first()

        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")

        message: Message = db.session.query(Message).filter(
            Message.id == message_id,
            Message.conversation_id == conversation_id,
        ).first()

        if not message:
            raise ValueError(f"Message not found: {message_id}")

        agent_thoughts: list[MessageAgentThought] = message.agent_thoughts

        if conversation.from_end_user_id:
            # only select name field
            executor = db.session.query(EndUser, EndUser.name).filter(
                EndUser.id == conversation.from_end_user_id
            ).first()
        else:
            executor = db.session.query(Account, Account.name).filter(
                Account.id == conversation.from_account_id
            ).first()

        if executor:
            executor = executor.name
        else:
            executor = 'Unknown'

        timezone = pytz.timezone(current_user.timezone)

        result = {
            'meta': {
                'status': 'success',
                'executor': executor,
                'start_time': message.created_at.astimezone(timezone).isoformat(),
                'elapsed_time': message.provider_response_latency,
                'total_tokens': message.answer_tokens + message.message_tokens,
                'agent_mode': app_model.app_model_config.agent_mode_dict.get('strategy', 'react'),
                'iterations': len(agent_thoughts),
            },
            'iterations': [],
            'files': message.files,
        }

        agent_config = AgentConfigManager.convert(app_model.draft_app_model_config.to_dict())
        agent_tools = agent_config.tools

        def find_agent_tool(tool_name: str):
            for agent_tool in agent_tools:
                if agent_tool.tool_name == tool_name:
                    return agent_tool

        for agent_thought in agent_thoughts:
            tools = agent_thought.tools
            tool_labels = agent_thought.tool_labels
            tool_meta = agent_thought.tool_meta
            tool_inputs = agent_thought.tool_inputs_dict
            tool_outputs = agent_thought.tool_outputs_dict
            tool_calls = []
            for tool in tools:
                tool_name = tool
                tool_label = tool_labels.get(tool_name, tool_name)
                tool_input = tool_inputs.get(tool_name, {})
                tool_output = tool_outputs.get(tool_name, {})
                tool_meta_data = tool_meta.get(tool_name, {})
                tool_config = tool_meta_data.get('tool_config', {})
                if tool_config.get('tool_provider_type', '') != 'dataset-retrieval':
                    tool_icon = ToolManager.get_tool_icon(
                        tenant_id=app_model.tenant_id,
                        provider_type=tool_config.get('tool_provider_type', ''),
                        provider_id=tool_config.get('tool_provider', ''),
                    )
                    if not tool_icon:
                        tool_entity = find_agent_tool(tool_name)
                        if tool_entity:
                            tool_icon = ToolManager.get_tool_icon(
                                tenant_id=app_model.tenant_id,
                                provider_type=tool_entity.provider_type,
                                provider_id=tool_entity.provider_id,
                            )
                else:
                    tool_icon = ''

                tool_calls.append({
                    'status': 'success' if not tool_meta_data.get('error') else 'error',
                    'error': tool_meta_data.get('error'),
                    'time_cost': tool_meta_data.get('time_cost', 0),
                    'tool_name': tool_name,
                    'tool_label': tool_label,
                    'tool_input': tool_input,
                    'tool_output': tool_output,
                    'tool_parameters': tool_meta_data.get('tool_parameters', {}),
                    'tool_icon': tool_icon,
                })

            result['iterations'].append({
                'tokens': agent_thought.tokens,
                'tool_calls': tool_calls,
                'tool_raw': {
                    'inputs': agent_thought.tool_input,
                    'outputs': agent_thought.observation,
                },
                'thought': agent_thought.thought,
                'created_at': agent_thought.created_at.isoformat(),
                'files': agent_thought.files,
            })

        return result
