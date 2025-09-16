import logging

import yaml  # type: ignore
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agent_platform_basic.libs import DbUtils
from agent_platform_core.factories import variable_factory
from agent_platform_core.models.enum_model.app_status import AppStatus
from agent_platform_service.events.app_event import app_was_created_async
from agent_platform_basic.models.db_model import Account
from agent_platform_core.models.db_model.model import App, AppModelConfig
from agent_platform_core.models.db_model.workflow import Workflow
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_service.fields.model_async.site_async import SiteAsync
from agent_platform_service.services.workflow_service import WorkflowService

logger = logging.getLogger(__name__)

current_yaml_version = "0.1.2"
yaml_to_agent_platform_version_mapping: dict[str, str] = {
    "0.1.2": "0.8.0",
    "0.1.1": "0.6.0",  # yaml version -> from agent platform version
}


class AppYamlService:

    def __init__(self, session: AsyncSession = Depends(DbUtils.get_db_async_session)):
        self.session = session
        self.site_async = SiteAsync(session)
        self.workflow_service = WorkflowService(session)

    async def import_and_create_new_app(self, tenant_id: str, data: str, args: dict, account: Account) -> App:
        """
        Import app yaml and create new app
        :param tenant_id: tenant id
        :param data: import data
        :param args: request args
        :param account: Account instance
        """
        try:
            import_data = yaml.safe_load(data)
        except yaml.YAMLError:
            raise ValueError("Invalid YAML format in data argument.")
        print("import_data:::", import_data)
        # check or repair yaml version
        import_data = self._check_or_fix_yaml(import_data)

        app_data = import_data.get("app")
        if not app_data:
            raise ValueError("Missing app in data argument")

        # get app basic info
        name = args.get("name") or app_data.get("name")
        description = args.get("description") or app_data.get("description", "")
        icon = args.get("icon") or app_data.get("icon")
        icon_background = args.get("icon_background") or app_data.get("icon_background")

        # import yaml and create app
        app_mode = AppMode.value_of(app_data.get("mode"))
        if app_mode in {AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC}:
            app = await self._import_and_create_new_workflow_based_app(
                tenant_id=tenant_id,
                app_mode=app_mode,
                workflow_data=import_data.get("workflow"),
                account=account,
                name=name,
                description=description,
                icon=icon,
                icon_background=icon_background,
            )
        elif app_mode in {AppMode.CHAT, AppMode.AGENT_CHAT, AppMode.COMPLETION}:
            app = await self._import_and_create_new_model_config_based_app(
                tenant_id=tenant_id,
                app_mode=app_mode,
                model_config_data=import_data.get("model_config"),
                account=account,
                name=name,
                description=description,
                icon=icon,
                icon_background=icon_background,
            )
        else:
            raise ValueError("Invalid app mode")

        return app

    async def import_and_overwrite_workflow(self, app_model: App, data: str, account: Account) -> Workflow:
        """
        Import app yaml and overwrite workflow
        :param app_model: App instance
        :param data: import data
        :param account: Account instance
        """
        try:
            import_data = yaml.safe_load(data)
        except yaml.YAMLError:
            raise ValueError("Invalid YAML format in data argument.")

        # check or repair yaml version
        import_data = self._check_or_fix_yaml(import_data)

        app_data = import_data.get("app")
        if not app_data:
            raise ValueError("Missing app in data argument")

        # import yaml and overwrite app
        app_mode = AppMode.value_of(app_data.get("mode"))
        if app_mode not in {AppMode.ADVANCED_CHAT, AppMode.WORKFLOW}:
            raise ValueError("Only support import workflow in advanced-chat or workflow app.")

        if app_data.get("mode") != app_model.mode:
            raise ValueError(f"App mode {app_data.get('mode')} is not matched with current app mode {app_mode.value}")

        return await self._import_and_overwrite_workflow_based_app(
            app_model=app_model,
            workflow_data=import_data.get("workflow"),
            account=account,
        )

    async def export_yaml(self, app_model: App, include_secret: bool = False) -> str:
        """
        Export app
        :param include_secret:
        :param app_model: App instance
        :return:
        """
        app_mode = AppMode.value_of(app_model.mode)

        export_data = {
            "version": current_yaml_version,
            "kind": "app",
            "app": {
                "name": app_model.name,
                "mode": app_model.mode,
                "icon": app_model.icon,
                "icon_background": app_model.icon_background,
                "description": app_model.description,
            },
        }

        #chatflow 工作流
        if app_mode in {AppMode.ADVANCED_CHAT, AppMode.WORKFLOW, AppMode.METABOLIC}:
            await self._append_workflow_export_data(
                export_data=export_data, app_model=app_model, include_secret=include_secret
            )
        else:
            #智能体
            await self._append_model_config_export_data(export_data, app_model)

        return yaml.dump(export_data, allow_unicode=True)

    @classmethod
    def _check_or_fix_yaml(cls, import_data: dict) -> dict:
        """
        Check or fix yaml

        :param import_data: import data
        """
        if not import_data.get("version"):
            import_data["version"] = "0.1.0"

        if not import_data.get("kind") or import_data.get("kind") != "app":
            import_data["kind"] = "app"

        if import_data.get("version") != current_yaml_version:
            # Currently only one yaml version, so no difference checks or compatibility fixes will be performed.
            logger.warning(
                f"yaml version {import_data.get('version')} is not compatible "
                f"with current version {current_yaml_version}, related to "
                f"agent platform version {yaml_to_agent_platform_version_mapping.get(current_yaml_version)}."
            )

        return import_data

    async def _import_and_create_new_workflow_based_app(
        self,
        tenant_id: str,
        app_mode: AppMode,
        workflow_data: dict,
        account: Account,
        name: str,
        description: str,
        icon: str,
        icon_background: str,
    ) -> App:
        """
        Import app yaml and create new workflow based app

        :param tenant_id: tenant id
        :param app_mode: app mode
        :param workflow_data: workflow data
        :param account: Account instance
        :param name: app name
        :param description: app description
        :param icon: app icon
        :param icon_background: app icon background
        """
        if not workflow_data:
            raise ValueError("Missing workflow in data argument when app mode is advanced-chat or workflow")

        app = await self._create_app(
            tenant_id=tenant_id,
            app_mode=app_mode,
            account=account,
            name=name,
            description=description,
            icon=icon,
            icon_background=icon_background,
        )

        # init draft workflow
        environment_variables_list = workflow_data.get("environment_variables") or []
        environment_variables = [variable_factory.build_environment_variable_from_mapping(obj) for obj in environment_variables_list]
        conversation_variables_list = workflow_data.get("conversation_variables") or []
        conversation_variables = [variable_factory.build_conversation_variable_from_mapping(obj) for obj in conversation_variables_list]
        # workflow_service = WorkflowService()
        draft_workflow = await self.workflow_service.sync_draft_workflow_async(
            app_model=app,
            graph=workflow_data.get("graph", {}),
            features=workflow_data.get("../core/app/features", {}),
            workflow_id=None,
            account=account,
            environment_variables=environment_variables,
            conversation_variables=conversation_variables,
        )
        # 导入为草稿
        # workflow_service.publish_workflow(app_model=app, account=account, draft_workflow=draft_workflow)

        return app

    async def _import_and_overwrite_workflow_based_app(
        self, app_model: App, workflow_data: dict, account: Account
    ) -> Workflow:
        """
        Import app yaml and overwrite workflow based app

        :param app_model: App instance
        :param workflow_data: workflow data
        :param account: Account instance
        """
        if not workflow_data:
            raise ValueError("Missing workflow in data argument when app mode is advanced-chat or workflow")

        # fetch draft workflow by app_model
        current_draft_workflow = await self.workflow_service.get_draft_workflow_async(app_model=app_model)
        if current_draft_workflow:
            unique_hash = current_draft_workflow.unique_hash
        else:
            unique_hash = None

        # sync draft workflow
        environment_variables_list = workflow_data.get("environment_variables") or []
        environment_variables = [variable_factory.build_environment_variable_from_mapping(obj) for obj in environment_variables_list]
        conversation_variables_list = workflow_data.get("conversation_variables") or []
        conversation_variables = [
            variable_factory.build_conversation_variable_from_mapping(obj) for obj in conversation_variables_list
        ]
        draft_workflow = await self.workflow_service.sync_draft_workflow_async(
            app_model=app_model,
            graph=workflow_data.get("graph", {}),
            features=workflow_data.get("features", {}),
            # unique_hash=unique_hash,
            account=account,
            environment_variables=environment_variables,
            workflow_id=workflow_data.get('workflow_id', None),
            conversation_variables=conversation_variables
        )

        return draft_workflow

    async def _import_and_create_new_model_config_based_app(
        self,
        tenant_id: str,
        app_mode: AppMode,
        model_config_data: dict,
        account: Account,
        name: str,
        description: str,
        icon: str,
        icon_background: str,
    ) -> App:
        """
        Import app yaml and create new model config based app

        :param tenant_id: tenant id
        :param app_mode: app mode
        :param model_config_data: model config data
        :param account: Account instance
        :param name: app name
        :param description: app description
        :param icon: app icon
        :param icon_background: app icon background
        """
        if not model_config_data:
            raise ValueError("Missing model_config in data argument when app mode is chat, agent-chat or completion")

        app = await self._create_app(
            tenant_id=tenant_id,
            app_mode=app_mode,
            account=account,
            name=name,
            description=description,
            icon=icon,
            icon_background=icon_background,
        )

        app_model_config = AppModelConfig()
        app_model_config = app_model_config.from_model_config_dict(model_config_data)
        app_model_config.app_id = app.id
        app_model_config.version = AppStatus.DRAFT.value
        # app_model_config.created_by = account.id
        # app_model_config.updated_by = account.id

        self.session.add(app_model_config)
        await self.session.flush()

        app.app_model_config_id = app_model_config.id
        await self.session.commit()

        # 导入为草稿状态
        # app_published_model_config_was_updated.send(app, app_model_config=app_model_config)

        return app

    async def _create_app(
        self,
        tenant_id: str,
        app_mode: AppMode,
        account: Account,
        name: str,
        description: str,
        icon: str,
        icon_background: str,
    ) -> App:
        """
        Create new app

        :param tenant_id: tenant id
        :param app_mode: app mode
        :param account: Account instance
        :param name: app name
        :param description: app description
        :param icon: app icon
        :param icon_background: app icon background
        """
        app = App(
            tenant_id=tenant_id,
            account_id=account.id,
            mode=app_mode.value,
            name=name,
            description=description,
            icon=icon,
            icon_background=icon_background,
            enable_site=True,
            enable_api=True,
            status=AppStatus.DRAFT.value
        )

        self.session.add(app)
        await self.session.commit()

        await app_was_created_async.send_async(app, account=account, session=self.session, site_async=self.site_async)

        return app

    async def _append_workflow_export_data(self, *, export_data: dict, app_model: App, include_secret: bool) -> None:
        """
        Append workflow export data
        :param export_data: export data
        :param app_model: App instance
        """
        workflow = await self.workflow_service.get_draft_workflow_async(app_model=app_model)
        if not workflow:
            raise ValueError("Missing draft workflow configuration, please check.")

        export_data["workflow"] = workflow.to_dict(include_secret=include_secret)

    async def _append_model_config_export_data(self, export_data: dict, app_model: App) -> None:
        """
        Append model config export data
        :param export_data: export data
        :param app_model: App instance
        """
        records = await self.session.execute(select(AppModelConfig).filter(AppModelConfig.app_id == app_model.id).order_by(AppModelConfig.created_at.desc()))
        # app_model_config = records.scalar_one_or_none()
        app_model_config = records.scalars().first()
        if not app_model_config:
            raise ValueError("Missing app configuration, please check.")

        export_data["model_config"] = app_model_config.to_dict()
