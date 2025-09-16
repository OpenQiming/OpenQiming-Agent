from datetime import datetime, timezone

from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.app.entities.app_invoke_entities import AgentChatAppGenerateEntity, ChatAppGenerateEntity
from agent_platform_core.events.message_event import message_was_created
from agent_platform_core.models.db_model.provider import Provider


@message_was_created.connect
def handle(sender, **kwargs):
    message = sender
    application_generate_entity = kwargs.get('application_generate_entity')

    if not isinstance(application_generate_entity, ChatAppGenerateEntity | AgentChatAppGenerateEntity):
        return

    db.session.query(Provider).filter(
        Provider.tenant_id == application_generate_entity.app_config.tenant_id,
        Provider.provider_name == application_generate_entity.model_conf.provider
    ).update({'last_used': datetime.now().replace(tzinfo=None)})
    db.session.commit()
