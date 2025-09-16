from functools import wraps
from typing import Union

from fastapi import Depends
from flask_login import current_user
from flask_restful import Resource
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_
from werkzeug.exceptions import NotFound

from agent_platform_basic.exceptions.controllers.console.app import AppNotFoundError
from agent_platform_basic.extensions.ext_database import db, async_db
from agent_platform_basic.libs import DbUtils
from agent_platform_basic.libs.login import login_required
from agent_platform_basic.models.db_model import Account
from agent_platform_core.models.db_model.model import App
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_core.models.enum_model.app_status import AppStatus
from agent_platform_service.controllers.console.wraps import account_initialization_required
from agent_platform_service.services.auth_service import login_user


def get_installed_app(view=None):
    def decorator(view):
        @wraps(view)
        def decorated(*args, **kwargs):
            if not kwargs.get('installed_app_id'):
                raise ValueError('missing installed_app_id in path parameters')

            installed_app_id = kwargs.get('installed_app_id')
            installed_app_id = str(installed_app_id)

            del kwargs['installed_app_id']

            installed_app = db.session.query(App).filter(
                App.id == str(installed_app_id),
                # App.tenant_id == current_user.current_tenant_id,
                or_(
                    App.status == AppStatus.INSTALLED.value,
                    App.status == AppStatus.PUBLISHED.value,
                    App.status == AppStatus.DRAFT.value
                )
            ).first()

            if installed_app is None:
                raise NotFound('Installed app not found')
            kwargs['app_model'] = installed_app
            return view(*args, **kwargs)

        return decorated

    if view:
        return decorator(view)
    return decorator


async def async_get_published_app(app_id: str,
                              mode: Union[AppMode, list[AppMode]] = None):

    if not app_id:
        raise ValueError('missing app_id in path parameters')

    async with async_db.AsyncSessionLocal() as session:
        app_model_sc = await session.execute(select(App).filter(
            App.id == app_id,
            App.status == AppStatus.PUBLISHED.value
        ))
        app_model = app_model_sc.scalar_one_or_none()

    if not app_model:
        raise AppNotFoundError()

    app_mode = AppMode.value_of(app_model.mode)
    if app_mode == AppMode.CHANNEL:
        raise AppNotFoundError()

    if mode is not None:
        if isinstance(mode, list):
            modes = mode
        else:
            modes = [mode]

        if app_mode not in modes:
            mode_values = {m.value for m in modes}
            raise AppNotFoundError(f"App mode is not in the supported list: {mode_values}")

    return app_model


class InstalledAppResource(Resource):
    # must be reversed if there are multiple decorators
    method_decorators = [get_installed_app, account_initialization_required, login_required]
