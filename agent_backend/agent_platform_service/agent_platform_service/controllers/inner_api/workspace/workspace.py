from flask_restful import Resource, reqparse

from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.inner_api import api
from agent_platform_service.controllers.inner_api.wraps import inner_api_only
from agent_platform_service.events.tenant_event import tenant_was_created
from agent_platform_basic.models.db_model import Account
from agent_platform_service.services.account_service import TenantService


class EnterpriseWorkspace(Resource):

    @setup_required
    @inner_api_only
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, location='json')
        parser.add_argument('owner_email', type=str, required=True, location='json')
        args = parser.parse_args()

        account = db.session.query(Account).filter_by(email=args['owner_email']).first()
        if account is None:
            return {
                'message': 'owner account not found.'
            }, 404

        tenant = TenantService.create_tenant(args['name'])
        TenantService.create_tenant_member(tenant, account, role='owner')

        tenant_was_created.send(tenant)

        return {
            'message': 'enterprise workspace created.'
        }


api.add_resource(EnterpriseWorkspace, '/enterprise/workspace')
