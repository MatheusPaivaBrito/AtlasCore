from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings

from core_api.infrastructure.settings import SETTINGS_CONFIG


class PlatformDiscoverySettings(BaseSettings):
    # ------------------------------------
    # APP
    # ------------------------------------
    APP_NAME: str = "AtlasCore"

    # ------------------------------------
    # API PORTS
    # ------------------------------------
    CORE_API_PORT: int = 8000
    AUTH_API_PORT: int = 8001
    EVENTING_API_PORT: int = 8002
    NOTIFICATION_API_PORT: int = 8003
    OBSERVABILITY_API_PORT: int = 8004

    # ------------------------------------
    # API PUBLIC URLS
    # ------------------------------------
    CORE_API_PUBLIC_URL: str = "http://localhost:8000"
    AUTH_API_PUBLIC_URL: str = "http://localhost:8001"
    EVENTING_API_PUBLIC_URL: str = "http://localhost:8002"
    NOTIFICATION_API_PUBLIC_URL: str = "http://localhost:8003"
    OBSERVABILITY_API_PUBLIC_URL: str = "http://localhost:8004"

    # ------------------------------------
    # API INTERNAL URLS
    # ------------------------------------
    CORE_API_INTERNAL_URL: str = "http://localhost:8000"
    AUTH_API_INTERNAL_URL: str = "http://localhost:8001"
    EVENTING_API_INTERNAL_URL: str = "http://localhost:8002"
    NOTIFICATION_API_INTERNAL_URL: str = "http://localhost:8003"
    OBSERVABILITY_API_INTERNAL_URL: str = "http://localhost:8004"

    # ------------------------------------
    # SERVICE DISCOVERY PATHS
    # ------------------------------------
    SERVICE_HEALTH_PATH: str = Field(
        default="/health",
        validation_alias=AliasChoices("SERVICE_HEALTH_PATH", "AUTH_API_HEALTH_PATH"),
    )
    SERVICE_DOCS_PATH: str = Field(
        default="/docs",
        validation_alias=AliasChoices("SERVICE_DOCS_PATH", "AUTH_API_DOCS_PATH"),
    )
    SERVICE_REDOC_PATH: str = "/redoc"
    SERVICE_CHECK_TIMEOUT_SECONDS: float = Field(
        default=0.2,
        validation_alias=AliasChoices("SERVICE_CHECK_TIMEOUT_SECONDS", "AUTH_API_CHECK_TIMEOUT_SECONDS"),
    )

    # ------------------------------------
    # DOCUMENTATION
    # ------------------------------------
    DOCS_PT_PORT: int = 8080
    DOCS_EN_PORT: int = 8081
    DOCS_PT_PUBLIC_URL_OVERRIDE: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DOCS_PT_PUBLIC_URL", "DOCS_PT_PUBLIC_URL_OVERRIDE"),
    )
    DOCS_EN_PUBLIC_URL_OVERRIDE: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DOCS_EN_PUBLIC_URL", "DOCS_EN_PUBLIC_URL_OVERRIDE"),
    )

    @property
    def DOCS_PT_PUBLIC_URL(self) -> str:
        if self.DOCS_PT_PUBLIC_URL_OVERRIDE:
            return self.DOCS_PT_PUBLIC_URL_OVERRIDE
        return f"http://localhost:{self.DOCS_PT_PORT}"

    @property
    def DOCS_EN_PUBLIC_URL(self) -> str:
        if self.DOCS_EN_PUBLIC_URL_OVERRIDE:
            return self.DOCS_EN_PUBLIC_URL_OVERRIDE
        return f"http://localhost:{self.DOCS_EN_PORT}"

    # ------------------------------------
    # PYDANTIC
    # ------------------------------------
    model_config = SETTINGS_CONFIG


platform_discovery_settings = PlatformDiscoverySettings()
