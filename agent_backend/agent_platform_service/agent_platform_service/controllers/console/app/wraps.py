from collections.abc import Callable
from functools import wraps
from typing import Optional, Union

from agent_platform_basic.exceptions.controllers.console.app import AppNotFoundError
from agent_platform_basic.extensions.ext_database import db, async_db
from agent_platform_basic.libs.redis_utils import RedisUtils
from agent_platform_core.models.db_model.model import App
from agent_platform_core.models.enum_model.app_mode import AppMode
from agent_platform_core.models.enum_model.app_status import AppStatus
from sqlalchemy import select


def get_app_model(view: Optional[Callable] = None, *,
                  mode: Union[AppMode, list[AppMode]] = None):
    def decorator(view_func):
        @wraps(view_func)
        def decorated_view(*args, **kwargs):
            if not kwargs.get('app_id'):
                raise ValueError('missing app_id in path parameters')

            app_id = kwargs.get('app_id')
            app_id = str(app_id)

            del kwargs['app_id']

            app_model = db.session.query(App).filter(
                App.id == app_id,
                App.status != AppStatus.DISABLED.value
            ).first()

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

            kwargs['app_model'] = app_model

            return view_func(*args, **kwargs)

        return decorated_view

    if view is None:
        return decorator
    else:
        return decorator(view)


@RedisUtils.cacheable_with_mutex("agent_platform_app_by_app_id: ",
                                 "agent_platform_get_app_with_mutex_by_app_id: ",
                                 ["app_id"],
                                 60)
async def get_app_model_async(app_id: str,
                              mode: Union[AppMode, list[AppMode]] = None):

    if not app_id:
        raise ValueError('missing app_id in path parameters')

    async with async_db.AsyncSessionLocal() as session:
        app_model_sc = await session.execute(select(App).filter(
            App.id == app_id,
            App.status != AppStatus.DISABLED.value
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
