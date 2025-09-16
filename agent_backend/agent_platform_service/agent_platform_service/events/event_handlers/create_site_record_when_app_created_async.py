from sqlalchemy import select

from agent_platform_core.models.db_model.model import Site
from agent_platform_service.events.app_event import app_was_created_async


@app_was_created_async.connect
async def handle(sender, **kwargs):
    """Create site record when an app is created."""
    print("site:::::::::::::", sender)
    app = sender
    account = kwargs.get('account')
    session = kwargs.get('session')
    site_async = kwargs.get('site_async')
    site = await session.execute(select(Site).filter(Site.app_id == app.id))
    site = site.scalar_one_or_none()
    if not site:
        site = Site(
            app_id=app.id,
            title=app.name,
            icon=app.icon,
            icon_background=app.icon_background,
            default_language=account.interface_language,
            customize_token_strategy='not_allow',
            code=await site_async.generate_code(16)
        )
        session.add(site)
        await session.commit()
    else:
        return site
