from agent_platform_basic.extensions.ext_database import db
from agent_platform_core.models.db_model.model import App, AppModelConfig
from agent_platform_core.moderation.factory import ModerationFactory, ModerationOutputsResult


class ModerationService:

    def moderation_for_outputs(self, app_id: str, app_model: App, text: str) -> ModerationOutputsResult:
        app_model_config: AppModelConfig = None

        app_model_config = db.session.query(AppModelConfig).filter(
            AppModelConfig.id == app_model.app_model_config_id).first()

        if not app_model_config:
            raise ValueError("app model config not found")

        name = app_model_config.sensitive_word_avoidance_dict['type']
        config = app_model_config.sensitive_word_avoidance_dict['config']

        moderation = ModerationFactory(name, app_id, app_model.tenant_id, config)
        return moderation.moderation_for_outputs(text)
