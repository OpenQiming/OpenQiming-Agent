from datetime import datetime, timezone

from flask_login import current_user
from flask_restful import Resource, inputs, marshal_with, reqparse
from sqlalchemy import and_, select
from werkzeug.exceptions import BadRequest, Forbidden, NotFound

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.libs.login import login_required
from agent_platform_basic.models.db_model.application_audit_share import ApplicationAuditShare
from agent_platform_common.configs import agent_platform_config
from agent_platform_core.models.db_model.model import App, InstalledApp
from agent_platform_core.models.db_model.workflow import Workflow
from agent_platform_core.models.enum_model.app_status import AppStatus
from agent_platform_core.tools.tool_manager import ToolManager
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.explore.wraps import InstalledAppResource
from agent_platform_service.controllers.console.wraps import account_initialization_required, \
    cloud_edition_billing_resource_check
from agent_platform_service.fields.installed_app_fields import installed_app_list_fields
from agent_platform_basic.libs import DbUtils


class InstalledAppsListApi(Resource):
    @login_required
    @account_initialization_required
    @marshal_with(installed_app_list_fields)
    def get(self):
        tenant_id = reqparse.request.args.get('tenant_id')
        current_tenant_id = current_user.current_tenant_id
        if tenant_id is None:
            tenant_id = agent_platform_config.GLOBAL_TENANT_ID
        installed_apps = db.session.query(App).filter(
            App.tenant_id == tenant_id,
            App.status == AppStatus.PUBLISHED.value
        ).all()

        installed_apps = [
            {
                'id': installed_app.id,
                'app': installed_app,
                'app_owner_tenant_id': installed_app.tenant_id,
                'editable': False,
                'uninstallable': False
            }
            for installed_app in installed_apps
        ]
        return {'installed_apps': installed_apps}

    @login_required
    @account_initialization_required
    @cloud_edition_billing_resource_check('apps')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('app_id', type=str, required=True, help='Invalid app_id')
        args = parser.parse_args()

        current_tenant_id = current_user.current_tenant_id
        app = db.session.query(App).filter(
            App.id == args['app_id'],
            App.status == AppStatus.PUBLISHED.value,
            App.tenant_id == current_tenant_id
        ).first()

        # 校验app
        if app is None:
            raise NotFound('App not found')

        # if not app.is_public:
        #     raise Forbidden('You can\'t install a non-public app')

        # #校验工具：graph-nodes-type: "tool"
        # if app.graph is not None:
        #     graph = app.graph
        #     if graph.get('nodes') is not None:
        #         for node in graph['nodes']:
        #             if node.get('type') == 'tool':
        #                 #查询工具
        #                 tool = ToolManager.get_tool(node.get('provider_type'), node.get('provider_id'),
        #                                             node.get('tool_name'), node.get('tenant_id'))
        #                 if tool is None or tool.status != AppStatus.PUBLISHED:
        #                     raise BadRequest('Tool not found or tool is not published')

        installed_app = InstalledApp.query.filter(
            and_(InstalledApp.app_id == args["app_id"], InstalledApp.tenant_id == current_tenant_id)
        ).first()

        if installed_app is None:

            new_installed_app = InstalledApp(
                app_id=args["app_id"],
                tenant_id=current_tenant_id,
                app_owner_tenant_id=app.tenant_id,
                is_pinned=False,
                last_used_at=datetime.now().replace(tzinfo=None),
            )
            db.session.add(new_installed_app)
            db.session.commit()

        db.session.commit()

        return {'message': 'App installed successfully'}


# class InstalledAppApi(InstalledAppResource):
#     """
#     update and delete an installed app
#     use InstalledAppResource to apply default decorators and get installed_app
#     """
#
#
#     def delete(self, installed_app):
#         if installed_app.app_owner_tenant_id == current_user.current_tenant_id:
#             raise BadRequest('You can\'t uninstall an app owned by the current tenant')
#
#         db.session.delete(installed_app)
#         db.session.commit()
#
#         return {'result': 'success', 'message': 'App uninstalled successfully'}
#
#     def patch(self, installed_app):
#         parser = reqparse.RequestParser()
#         parser.add_argument('is_pinned', type=inputs.boolean)
#         args = parser.parse_args()
#
#         commit_args = False
#         if 'is_pinned' in args:
#             installed_app.is_pinned = args['is_pinned']
#             commit_args = True
#
#         if commit_args:
#             db.session.commit()
#
#         return {'result': 'success', 'message': 'App info updated successfully'}

class InstalledShareAppsListApi(Resource):
    @login_required
    @account_initialization_required
    @marshal_with(installed_app_list_fields)
    def get(self):

        result = db.session.execute(select(ApplicationAuditShare.app_id))
        app_ids = result.scalars().all()
        ids_list = [id for id in app_ids]

        filters = []
        filters.append(App.id.in_(ids_list))

        installed_apps = db.session.query(App).filter(
            *filters
        ).all()

        installed_apps = [
            {
                'id': installed_app.id,
                'app': installed_app,
                'app_owner_tenant_id': installed_app.tenant_id,
                'editable': False,
                'uninstallable': False
            }
            for installed_app in installed_apps
        ]
        return {'installed_apps': installed_apps}


api.add_resource(InstalledAppsListApi, '/installed-apps')
api.add_resource(InstalledShareAppsListApi, '/installed-share-apps')
# api.add_resource(InstalledAppApi, '/installed-apps/<uuid:installed_app_id>')
