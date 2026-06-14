from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared_kernel.http import CorsConfig, parse_cors_origins


class ObservabilitySettings(BaseSettings):
    # ------------------------------------
    # APP
    # ------------------------------------
    APP_NAME: str = "AtlasCore"
    SERVICE_NAME: str = Field(
        default="observability_api",
        validation_alias=AliasChoices("OBSERVABILITY_SERVICE_NAME", "SERVICE_NAME"),
    )

    # ------------------------------------
    # CORS
    # ------------------------------------
    CORS_ENABLED: bool = Field(
        default=True,
        validation_alias=AliasChoices("OBSERVABILITY_API_CORS_ENABLED", "CORS_ENABLED"),
    )
    CORS_ALLOWED_ORIGINS_RAW: str = Field(
        default="",
        validation_alias=AliasChoices("OBSERVABILITY_API_CORS_ALLOWED_ORIGINS", "CORS_ALLOWED_ORIGINS"),
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        validation_alias=AliasChoices("OBSERVABILITY_API_CORS_ALLOW_CREDENTIALS", "CORS_ALLOW_CREDENTIALS"),
    )

    @property
    def CORS_ALLOWED_ORIGINS(self) -> tuple[str, ...]:
        return parse_cors_origins(self.CORS_ALLOWED_ORIGINS_RAW)

    @property
    def CORS_CONFIG(self) -> CorsConfig:
        return CorsConfig(
            enabled=self.CORS_ENABLED,
            allow_origins=self.CORS_ALLOWED_ORIGINS,
            allow_credentials=self.CORS_ALLOW_CREDENTIALS,
        )

    # ------------------------------------
    # LOKI
    # ------------------------------------
    LOKI_URL: str = "http://localhost:3100"
    LOKI_READY_URL: str = "http://localhost:3100/ready"

    # ------------------------------------
    # GRAFANA
    # ------------------------------------
    GRAFANA_URL: str = "http://localhost:3000"
    GRAFANA_HEALTH_URL: str = "http://localhost:3000/api/health"

    # ------------------------------------
    # SENTRY
    # ------------------------------------
    SENTRY_DSN: str | None = None
    SENTRY_ENVIRONMENT: str = Field(
        default="development",
        validation_alias=AliasChoices("SENTRY_ENVIRONMENT", "ENVIRONMENT"),
    )

    # ------------------------------------
    # PYDANTIC
    # ------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


settings = ObservabilitySettings()
