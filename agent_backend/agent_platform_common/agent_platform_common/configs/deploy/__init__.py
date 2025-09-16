from pydantic import Field
from pydantic_settings import BaseSettings


class DeploymentConfig(BaseSettings):
    """
    Configuration settings for application deployment
    """

    APPLICATION_NAME: str = Field(
        description='Application name',
        default='ChinaTele/AgentPlatform'
    )

    DEBUG: bool = Field(
        description="Enable debug mode for additional logging and development features",
        default=False,
    )

    EDITION: str = Field(
        description="Deployment edition of the application (e.g., 'SELF_HOSTED', 'CLOUD')",
        default="SELF_HOSTED",
    )

    DEPLOY_ENV: str = Field(
        description="Deployment environment (e.g., 'PRODUCTION', 'DEVELOPMENT'), default to PRODUCTION",
        default="PRODUCTION",
    )

    GLOBAL_APIROUTER_PREFIX: str = Field(
        description="Global API router prefix",
        default="")
