from flask import current_app
from flask_login import current_user
from flask_restful import Resource, abort, marshal_with, reqparse

import agent_platform_basic
from agent_platform_basic.exceptions.services.account import AccountAlreadyInTenantError
from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.libs import StringUtils
from agent_platform_basic.libs.login import login_required
from agent_platform_basic.models.db_model import Account, Tenant
from agent_platform_basic.models.enum_model.tenant import TenantAccountRole
from agent_platform_service.controllers.console import api
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required, \
    cloud_edition_billing_resource_check
from agent_platform_service.fields.member_fields import account_with_role_list_fields
from agent_platform_service.services.account_service import RegisterService, TenantService


class MemberListApi(Resource):
    """List all members of current tenant."""

    @setup_required
    @login_required
    @account_initialization_required
    @marshal_with(account_with_role_list_fields)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('tenant_id', type=str, required=False, nullable=True, location='args')
        args = parser.parse_args()
        tenant = current_user.current_tenant
        if StringUtils.is_not_blank(args.get('tenant_id')):
            tenant_id = args.get('tenant_id')
            tenant = db.session.query(Tenant).filter(Tenant.id == tenant_id).first()
        members = TenantService.get_tenant_members(tenant)
        return {'result': 'success', 'accounts': members}, 200


class MemberInviteEmailApi(Resource):
    """Invite a new member by email."""

    @setup_required
    @login_required
    @account_initialization_required
    @cloud_edition_billing_resource_check('members')
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('emails', type=str, required=True, location='json', action='append')
        parser.add_argument('role', type=str, required=True, default='admin', location='json')
        parser.add_argument('language', type=str, required=False, location='json')
        parser.add_argument('tenant_id', type=str, required=False, nullable=True, location='json')

        args = parser.parse_args()

        invitee_emails = args['emails']
        invitee_role = args['role']
        interface_language = args['language']
        if not TenantAccountRole.is_non_owner_role(invitee_role):
            return {'code': 'invalid-role', 'message': 'Invalid role'}, 400

        inviter = current_user
        invitation_results = []
        console_web_url = current_app.config.get("CONSOLE_WEB_URL")

        tenant = current_user.current_tenant
        if StringUtils.is_not_blank(args.get('tenant_id')):
            tenant_id = args.get('tenant_id')
            tenant = db.session.query(Tenant).filter(Tenant.id == tenant_id).first()

        for invitee_email in invitee_emails:
            try:
                token = RegisterService.invite_new_member(tenant, invitee_email, interface_language,
                                                          role=invitee_role, inviter=inviter)
                invitation_results.append({
                    'status': 'success',
                    'email': invitee_email,
                    'url': f'{console_web_url}/activate?email={invitee_email}&token={token}'
                })
            except AccountAlreadyInTenantError:
                invitation_results.append({
                    'status': 'success',
                    'email': invitee_email,
                    'url': f'{console_web_url}/signin'
                })
                break
            except Exception as e:
                invitation_results.append({
                    'status': 'failed',
                    'email': invitee_email,
                    'message': str(e)
                })

        return {
            'result': 'success',
            'invitation_results': invitation_results,
        }, 201


class MemberCancelInviteApi(Resource):
    """Cancel an invitation by member id."""

    @setup_required
    @login_required
    @account_initialization_required
    def delete(self, member_id):

        parser = reqparse.RequestParser()
        parser.add_argument('tenant_id', type=str, required=False, nullable=True, location='args')
        args = parser.parse_args()
        tenant = current_user.current_tenant
        if StringUtils.is_not_blank(args.get('tenant_id')):
            tenant_id = args.get('tenant_id')
            tenant = db.session.query(Tenant).filter(Tenant.id == tenant_id).first()

        member = db.session.query(Account).filter(Account.id == str(member_id)).first()
        if not member:
            abort(404)

        try:
            TenantService.remove_member_from_tenant(tenant, member, current_user)
        except agent_platform_basic.exceptions.services.account.CannotOperateSelfError as e:
            return {'code': 'cannot-operate-self', 'message': str(e)}, 400
        except agent_platform_basic.exceptions.services.account.NoPermissionError as e:
            return {'code': 'forbidden', 'message': str(e)}, 403
        except agent_platform_basic.exceptions.services.account.MemberNotInTenantError as e:
            return {'code': 'member-not-found', 'message': str(e)}, 404
        except Exception as e:
            raise ValueError(str(e))

        return {'result': 'success'}, 204


class MemberUpdateRoleApi(Resource):
    """Update member role."""

    @setup_required
    @login_required
    @account_initialization_required
    def put(self, member_id):
        parser = reqparse.RequestParser()
        parser.add_argument('role', type=str, required=True, location='json')
        parser.add_argument('tenant_id', type=str, required=False, nullable=True, location='json')
        args = parser.parse_args()
        new_role = args['role']

        if not TenantAccountRole.is_valid_role(new_role):
            return {'code': 'invalid-role', 'message': 'Invalid role'}, 400

        member = db.session.query(Account).get(str(member_id))
        if not member:
            abort(404)

        try:
            tenant = current_user.current_tenant
            if StringUtils.is_not_blank(args.get('tenant_id')):
                tenant_id = args.get('tenant_id')
                tenant = db.session.query(Tenant).filter(Tenant.id == tenant_id).first()
            TenantService.update_member_role(tenant, member, new_role, current_user)
        except Exception as e:
            raise ValueError(str(e))

        # todo: 403

        return {'result': 'success'}


api.add_resource(MemberListApi, '/workspaces/current/members')
api.add_resource(MemberInviteEmailApi, '/workspaces/current/members/invite-email')
api.add_resource(MemberCancelInviteApi, '/workspaces/current/members/<uuid:member_id>')
api.add_resource(MemberUpdateRoleApi, '/workspaces/current/members/<uuid:member_id>/update-role')
