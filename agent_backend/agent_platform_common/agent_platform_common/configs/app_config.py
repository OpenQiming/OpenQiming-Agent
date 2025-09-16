from pydantic_settings import SettingsConfigDict, BaseSettings, PydanticBaseSettingsSource

from agent_platform_common.configs.deploy import DeploymentConfig
from agent_platform_common.configs.extra import ExtraServiceConfig
from agent_platform_common.configs.feature import FeatureConfig
from agent_platform_common.configs.middleware import MiddlewareConfig
from agent_platform_common.configs.packaging import PackagingInfo


class AgentPlatformConfig(
    # Packaging info
    PackagingInfo,
    # Deployment configs
    DeploymentConfig,
    # Feature configs
    FeatureConfig,
    # Middleware configs
    MiddlewareConfig,
    # Extra service configs
    ExtraServiceConfig,
):
    model_config = SettingsConfigDict(
        # read from dotenv format config file
        # env_file=os.path.join(os.path.abspath(os.path.curdir), ".env"),
        env_file=".env",
        env_file_encoding="utf-8",
        # ignore extra attributes
        extra="ignore",
    )

    # Before adding any config,
    # please consider to arrange it in the proper config group of existed or added
    # for better readability and maintainability.
    # Thanks for your concentration and consideration.
