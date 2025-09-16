import os

from flask import current_app, session
from flask_restful import Resource, reqparse

from agent_platform_basic.libs.helper import str_len
from agent_platform_core.models.db_model.model import AgentPlatformSetup
from agent_platform_service.services.account_service import TenantService

from . import api
from agent_platform_basic.exceptions.controllers.console_exceptions import AlreadySetupError, InitValidateFailedError
from .wraps import only_edition_self_hosted


class InitValidateAPI(Resource):

    def get(self):
        init_status = get_init_validate_status()
        if init_status:
            return { 'status': 'finished' }
        return {'status': 'not_started' }

    @only_edition_self_hosted
    def post(self):
        # is tenant created
        tenant_count = TenantService.get_tenant_count()
        if tenant_count > 0:
            raise AlreadySetupError()

        parser = reqparse.RequestParser()
        parser.add_argument('password', type=str_len(30),
                            required=True, location='json')
        input_password = parser.parse_args()['password']

        if input_password != os.environ.get('INIT_PASSWORD'):
            session['is_init_validated'] = False
            raise InitValidateFailedError()
            
        session['is_init_validated'] = True
        return {'result': 'success'}, 201

def get_init_validate_status():
    if current_app.config['EDITION'] == 'SELF_HOSTED':
        if os.environ.get('INIT_PASSWORD'):
            return session.get('is_init_validated') or AgentPlatformSetup.query.first()
    
    return True

api.add_resource(InitValidateAPI, '/init')
