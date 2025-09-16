from fastapi import Depends, Request
from flask_login import current_user
from flask_restful import Resource, marshal_with, reqparse
from werkzeug.exceptions import Forbidden, NotFound
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select

from agent_platform_basic.extensions.ext_database import db
from agent_platform_basic.libs import DbUtils
from agent_platform_basic.libs.login import login_required
from agent_platform_basic.models.db_model import Account
from agent_platform_common.constants.languages import supported_language
from agent_platform_core.models.db_model.model import Site, App
from agent_platform_service.controllers.console import api, console_api
from agent_platform_service.controllers.console.app.wraps import get_app_model, get_app_model_async
from agent_platform_service.controllers.console.setup import setup_required
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.fields.app_fields import app_site_fields, site_fields
from agent_platform_service.fields.model_async.app_async import AppAsync
from agent_platform_service.fields.model_async.site_async import SiteAsync
from agent_platform_service.services.auth_service import login_user


def parse_app_site_args():
    parser = reqparse.RequestParser()
    parser.add_argument('title', type=str, required=False, location='json')
    parser.add_argument('icon', type=str, required=False, location='json')
    parser.add_argument('icon_background', type=str, required=False, location='json')
    parser.add_argument('description', type=str, required=False, location='json')
    parser.add_argument('default_language', type=supported_language, required=False, location='json')
    parser.add_argument('chat_color_theme', type=str, required=False, location='json')
    parser.add_argument('chat_color_theme_inverted', type=bool, required=False, location='json')
    parser.add_argument('customize_domain', type=str, required=False, location='json')
    parser.add_argument('copyright', type=str, required=False, location='json')
    parser.add_argument('privacy_policy', type=str, required=False, location='json')
    parser.add_argument('custom_disclaimer', type=str, required=False, location='json')
    parser.add_argument('customize_token_strategy', type=str, choices=['must', 'allow', 'not_allow'],
                        required=False,
                        location='json')
    parser.add_argument('prompt_public', type=bool, required=False, location='json')
    parser.add_argument('show_workflow_steps', type=bool, required=False, location='json')
    return parser.parse_args()


# @console_api.get("/apps/{app_id}/site")
async def app_site_get(request: Request, user: Account = Depends(login_user),
                       app_model: App = Depends(get_app_model_async), app_async=Depends(AppAsync)):
    return await app_async.site_fields_async(app_model, request)


# @console_api.post("/apps/{app_id}/site")
async def app_site_post(request: Request, app_id: str,
                        current_user: Account = Depends(login_user),
                        session: AsyncSession = Depends(DbUtils.get_db_async_session),
                        site_async=Depends(SiteAsync)):
    # The role of the current user in the ta table must be editor, admin, or owner
    if not current_user.is_editor:
        raise Forbidden()

    app_model = await get_app_model_async(app_id=app_id, mode=None)

    site = await session.execute(select(Site).filter(Site.app_id == app_model.id))
    site = site.scalar_one_or_none()

    if not site:
        raise NotFound

    request_json = await request.json()

    for attr_name in [
        'title',
        'icon',
        'icon_background',
        'description',
        'default_language',
        'chat_color_theme',
        'chat_color_theme_inverted',
        'customize_domain',
        'copyright',
        'privacy_policy',
        'custom_disclaimer',
        'customize_token_strategy',
        'prompt_public',
        'show_workflow_steps'
    ]:
        value = request_json.get(attr_name)
        if value is not None:
            setattr(site, attr_name, value)

    await session.commit()

    return site_async.app_site_fields_mapper(site, app_model.id)


class AppSite(Resource):
    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model
    @marshal_with(app_site_fields)
    def post(self, app_model):
        args = parse_app_site_args()

        # The role of the current user in the ta table must be editor, admin, or owner
        if not current_user.is_editor:
            raise Forbidden()

        site = db.session.query(Site). \
            filter(Site.app_id == app_model.id). \
            one_or_404()

        for attr_name in [
            'title',
            'icon',
            'icon_background',
            'description',
            'default_language',
            'chat_color_theme',
            'chat_color_theme_inverted',
            'customize_domain',
            'copyright',
            'privacy_policy',
            'custom_disclaimer',
            'customize_token_strategy',
            'prompt_public',
            'show_workflow_steps'
        ]:
            value = args.get(attr_name)
            if value is not None:
                setattr(site, attr_name, value)

        db.session.commit()

        return site

    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model
    @marshal_with(site_fields)
    def get(self, app_model):
        site = db.session.query(Site).filter(Site.app_id == app_model.id).first()
        return site


# @console_api.post("/apps/{app_id}/site/access-token-reset")
async def app_site_access_token_reset_post(app_model: App = Depends(get_app_model_async),
                                           current_user: Account = Depends(login_user),
                                           site_async=Depends(SiteAsync),
                                           session: AsyncSession = Depends(DbUtils.get_db_async_session)):
    # The role of the current user in the ta table must be admin or owner
    if not current_user.is_editor:
        raise Forbidden()

    site = await session.execute(select(Site).filter(Site.app_id == app_model.id))
    site = site.scalar_one_or_none()

    if not site:
        raise NotFound

    site.code = await site_async.generate_code(16)
    await session.commit()

    return site_async.app_site_fields_mapper(site, app_model.id)


class AppSiteAccessTokenReset(Resource):

    @setup_required
    @login_required
    @account_initialization_required
    @get_app_model
    @marshal_with(app_site_fields)
    def post(self, app_model):
        # The role of the current user in the ta table must be admin or owner
        if not current_user.is_editor:
            raise Forbidden()

        site = db.session.query(Site).filter(Site.app_id == app_model.id).first()

        if not site:
            raise NotFound

        site.code = Site.generate_code(16)
        db.session.commit()

        return site


api.add_resource(AppSite, '/apps/<uuid:app_id>/site')
api.add_resource(AppSiteAccessTokenReset, '/apps/<uuid:app_id>/site/access-token-reset')
