from sqlalchemy import and_

from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.models.db_model.model import InstalledApp
from agent_platform_service.events.app_event import app_was_installed


@app_was_installed.connect
def handle(sender, **kwargs):
    """Create an installed app when an app is created."""
    app = sender

    installed_app = db.session.query(InstalledApp).filter(and_(InstalledApp.app_id == app.id, InstalledApp.tenant_id == app.tenant_id)).first()
    if installed_app:
        return
    installed_app = InstalledApp(
        tenant_id=app.tenant_id,
        app_id=app.id,
        app_owner_tenant_id=app.tenant_id
    )
    db.session.add(installed_app)
    db.session.commit()
