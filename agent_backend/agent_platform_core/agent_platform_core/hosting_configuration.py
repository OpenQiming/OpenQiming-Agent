from typing import Optional

from flask import Config, Flask
from pydantic import BaseModel

from agent_platform_core.entities.provider_entities import QuotaUnit, RestrictModel
from agent_platform_core.model_runtime.entities.model_entities import ModelType
from agent_platform_core.models.enum_model.provider import ProviderQuotaType


class HostingQuota(BaseModel):
    quota_type: ProviderQuotaType
    restrict_models: list[RestrictModel] = []


class TrialHostingQuota(HostingQuota):
    quota_type: ProviderQuotaType = ProviderQuotaType.TRIAL
    quota_limit: int = 0
    """Quota limit for the hosting provider models. -1 means unlimited."""


class PaidHostingQuota(HostingQuota):
    quota_type: ProviderQuotaType = ProviderQuotaType.PAID


class FreeHostingQuota(HostingQuota):
    quota_type: ProviderQuotaType = ProviderQuotaType.FREE


class HostingProvider(BaseModel):
    enabled: bool = False
    credentials: Optional[dict] = None
    quota_unit: Optional[QuotaUnit] = None
    quotas: list[HostingQuota] = []


class HostedModerationConfig(BaseModel):
    enabled: bool = False
    providers: list[str] = []


class HostingConfiguration:
    provider_map: dict[str, HostingProvider] = {}
    moderation_config: HostedModerationConfig = None

    def init_app(self, app: Flask) -> None:
        config = app.config

        if config.get('EDITION') != 'CLOUD':
            return

        self.provider_map["openai"] = self.init_openai(config)

        self.moderation_config = self.init_moderation_config(config)

    def init_openai(self, app_config: Config) -> HostingProvider:
        quota_unit = QuotaUnit.CREDITS
        quotas = []

        if app_config.get("HOSTED_OPENAI_TRIAL_ENABLED"):
            hosted_quota_limit = int(app_config.get("HOSTED_OPENAI_QUOTA_LIMIT", "200"))
            trial_models = self.parse_restrict_models_from_env(app_config, "HOSTED_OPENAI_TRIAL_MODELS")
            trial_quota = TrialHostingQuota(
                quota_limit=hosted_quota_limit,
                restrict_models=trial_models
            )
            quotas.append(trial_quota)

        if app_config.get("HOSTED_OPENAI_PAID_ENABLED"):
            paid_models = self.parse_restrict_models_from_env(app_config, "HOSTED_OPENAI_PAID_MODELS")
            paid_quota = PaidHostingQuota(
                restrict_models=paid_models
            )
            quotas.append(paid_quota)

        if len(quotas) > 0:
            credentials = {
                "openai_api_key": app_config.get("HOSTED_OPENAI_API_KEY"),
            }

            if app_config.get("HOSTED_OPENAI_API_BASE"):
                credentials["openai_api_base"] = app_config.get("HOSTED_OPENAI_API_BASE")

            if app_config.get("HOSTED_OPENAI_API_ORGANIZATION"):
                credentials["openai_organization"] = app_config.get("HOSTED_OPENAI_API_ORGANIZATION")

            return HostingProvider(
                enabled=True,
                credentials=credentials,
                quota_unit=quota_unit,
                quotas=quotas
            )

        return HostingProvider(
            enabled=False,
            quota_unit=quota_unit,
        )

    def init_moderation_config(self, app_config: Config) -> HostedModerationConfig:
        if app_config.get("HOSTED_MODERATION_ENABLED") \
                and app_config.get("HOSTED_MODERATION_PROVIDERS"):
            return HostedModerationConfig(
                enabled=True,
                providers=app_config.get("HOSTED_MODERATION_PROVIDERS").split(',')
            )

        return HostedModerationConfig(
            enabled=False
        )

    @staticmethod
    def parse_restrict_models_from_env(app_config: Config, env_var: str) -> list[RestrictModel]:
        models_str = app_config.get(env_var)
        models_list = models_str.split(",") if models_str else []
        return [RestrictModel(model=model_name.strip(), model_type=ModelType.LLM) for model_name in models_list if
                model_name.strip()]
