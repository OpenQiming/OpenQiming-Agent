import datetime

from flask import request
from flask_login import current_user
from flask_restful import Resource, marshal_with
from werkzeug.exceptions import NotFound

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.libs.login import login_required
from agent_platform_basic.models.db_model import DataSourceOauthBinding
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.fields.data_source_fields import integrate_list_fields


class DataSourceApi(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(integrate_list_fields)
    def get(self):
        # get workspace data source integrates
        data_source_integrates = db.session.query(DataSourceOauthBinding).filter(
            DataSourceOauthBinding.tenant_id == current_user.current_tenant_id,
            DataSourceOauthBinding.disabled == False
        ).all()

        base_url = request.url_root.rstrip('/')
        data_source_oauth_base_path = "/console/api/oauth/data-source"
        providers = ["notion"]

        integrate_data = []
        for provider in providers:
            # existing_integrate = next((ai for ai in data_source_integrates if ai.provider == provider), None)
            existing_integrates = filter(lambda item: item.provider == provider, data_source_integrates)
            if existing_integrates:
                for existing_integrate in list(existing_integrates):
                    integrate_data.append({
                        'id': existing_integrate.id,
                        'provider': provider,
                        'created_at': existing_integrate.created_at,
                        'is_bound': True,
                        'disabled': existing_integrate.disabled,
                        'source_info': existing_integrate.source_info,
                        'link': f'{base_url}{data_source_oauth_base_path}/{provider}'
                    })
            else:
                integrate_data.append({
                    'id': None,
                    'provider': provider,
                    'created_at': None,
                    'source_info': None,
                    'is_bound': False,
                    'disabled': None,
                    'link': f'{base_url}{data_source_oauth_base_path}/{provider}'
                })
        return {'data': integrate_data}, 200

    @setup_required
    @login_required
    @account_initialization_required
    def patch(self, binding_id, action):
        binding_id = str(binding_id)
        action = str(action)
        data_source_binding = DataSourceOauthBinding.query.filter_by(
            id=binding_id
        ).first()
        if data_source_binding is None:
            raise NotFound('Data source binding not found.')
        # enable binding
        if action == 'enable':
            if data_source_binding.disabled:
                data_source_binding.disabled = False
                data_source_binding.updated_at = datetime.datetime.now().replace(tzinfo=None)
                db.session.add(data_source_binding)
                db.session.commit()
            else:
                raise ValueError('Data source is not disabled.')
        # disable binding
        if action == 'disable':
            if not data_source_binding.disabled:
                data_source_binding.disabled = True
                data_source_binding.updated_at = datetime.datetime.now().replace(tzinfo=None)
                db.session.add(data_source_binding)
                db.session.commit()
            else:
                raise ValueError('Data source is disabled.')
        return {'result': 'success'}, 200


api.add_resource(DataSourceApi, '/data-source/integrates', '/data-source/integrates/<uuid:binding_id>/<string:action>')
