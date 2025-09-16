from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.models.db_model.model import Site
from agent_platform_service.events.app_event import app_was_created


@app_was_created.connect
def handle(sender, **kwargs):
    """Create site record when an app is created."""
    app = sender
    account = kwargs.get('account')
    site = db.session.query(Site).filter(Site.app_id == app.id).first()
    if site:
        return
    site = Site(
        app_id=app.id,
        title=app.name,
        icon=app.icon,
        icon_background=app.icon_background,
        default_language=account.interface_language,
        customize_token_strategy='not_allow',
        code=Site.generate_code(16)
    )
    db.session.add(site)
    db.session.commit()
