from sqlalchemy import select

from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.models.db_model.model import App
from agent_platform_core.models.enum_model.app_status import AppStatus
from agent_platform_service.events.app_event import app_was_published, app_was_published_async


@app_was_published.connect
def handle(sender, **kwargs):
    """Create an installed app when an app is created."""
    app = sender

    app = db.session.query(App).filter(App.id == app.id).first()
    app.status = AppStatus.PUBLISHED.value
    db.session.commit()


@app_was_published_async.connect
async def handle(sender, **kwargs):
    """Create an installed app when an app is created."""
    session = kwargs.get('session')
    app = sender

    app_scalar = await session.execute(select(App).filter(App.id == app.id))
    app = app_scalar.scalar_one_or_none()
    app.status = AppStatus.PUBLISHED.value
    await session.commit()
