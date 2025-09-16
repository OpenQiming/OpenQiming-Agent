from flask import current_app
from pydantic import BaseModel, ConfigDict
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field
from agent_platform_common.configs import agent_platform_config
from agent_platform_service.services.billing_service import BillingService


class SubscriptionModel(BaseModel):
    plan: str = 'sandbox'
    interval: str = ''


class BillingModel(BaseModel):
    enabled: bool = False
    subscription: SubscriptionModel = SubscriptionModel()


class LimitationModel(BaseModel):
    size: int = 0
    limit: int = 0


class FeatureModel(BaseModel):
    billing: BillingModel = BillingModel()
    members: LimitationModel = LimitationModel(size=0, limit=1)
    apps: LimitationModel = LimitationModel(size=0, limit=10)
    vector_space: LimitationModel = LimitationModel(size=0, limit=5)
    annotation_quota_limit: LimitationModel = LimitationModel(size=0, limit=10)
    documents_upload_quota: LimitationModel = LimitationModel(size=0, limit=50)
    docs_processing: str = 'standard'
    model_load_balancing_enabled: bool = False

    # pydantic configs
    model_config = ConfigDict(protected_namespaces=())

class PluginInstallationScope(StrEnum):
    NONE = "none"
    OFFICIAL_ONLY = "official_only"
    OFFICIAL_AND_SPECIFIC_PARTNERS = "official_and_specific_partners"
    ALL = "all"

class PluginInstallationPermissionModel(BaseModel):
    # Plugin installation scope – possible values:
    #   none: prohibit all plugin installations
    #   official_only: allow only Dify official plugins
    #   official_and_specific_partners: allow official and specific partner plugins
    #   all: allow installation of all plugins
    plugin_installation_scope: PluginInstallationScope = PluginInstallationScope.ALL

    # If True, restrict plugin installation to the marketplace only
    # Equivalent to ForceEnablePluginVerification
    restrict_to_marketplace_only: bool = False

class SystemFeatureModel(BaseModel):
    sso_enforced_for_signin: bool = False
    sso_enforced_for_signin_protocol: str = ''
    sso_enforced_for_web: bool = False
    sso_enforced_for_web_protocol: str = ''
    plugin_installation_permission: PluginInstallationPermissionModel = PluginInstallationPermissionModel()

class KnowledgeRateLimitModel(BaseModel):
    enabled: bool = False
    limit: int = 10
    subscription_plan: str = ""


class FeatureService:

    @classmethod
    def get_features(cls, tenant_id: str) -> FeatureModel:
        features = FeatureModel()

        cls._fulfill_params_from_env(features)

        if current_app.config['BILLING_ENABLED']:
            cls._fulfill_params_from_billing_api(features, tenant_id)

        return features

    @classmethod
    def get_system_features(cls) -> SystemFeatureModel:
        system_features = SystemFeatureModel()
        return system_features

    @classmethod
    def _fulfill_params_from_env(cls, features: FeatureModel):
        # features.can_replace_logo = current_app.config['CAN_REPLACE_LOGO']
        features.model_load_balancing_enabled = current_app.config['MODEL_LB_ENABLED']

    @classmethod
    def get_knowledge_rate_limit(cls, tenant_id: str):
        knowledge_rate_limit = KnowledgeRateLimitModel()
        if agent_platform_config.BILLING_ENABLED and tenant_id:
            knowledge_rate_limit.enabled = True
            limit_info = BillingService.get_knowledge_rate_limit(tenant_id)
            knowledge_rate_limit.limit = limit_info.get("limit", 10)
            knowledge_rate_limit.subscription_plan = limit_info.get("subscription_plan", "sandbox")
        return knowledge_rate_limit
