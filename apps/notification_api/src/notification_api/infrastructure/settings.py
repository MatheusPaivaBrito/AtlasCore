from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared_kernel.http import CorsConfig, parse_cors_origins


class NotificationSettings(BaseSettings):
    # ------------------------------------
    # APP
    # ------------------------------------
    APP_NAME: str = "AtlasCore"
    SERVICE_NAME: str = Field(
        default="notification_api",
        validation_alias=AliasChoices("NOTIFICATION_SERVICE_NAME", "SERVICE_NAME"),
    )

    # ------------------------------------
    # CORS
    # ------------------------------------
    CORS_ENABLED: bool = Field(
        default=True,
        validation_alias=AliasChoices("NOTIFICATION_API_CORS_ENABLED", "CORS_ENABLED"),
    )
    CORS_ALLOWED_ORIGINS_RAW: str = Field(
        default="",
        validation_alias=AliasChoices("NOTIFICATION_API_CORS_ALLOWED_ORIGINS", "CORS_ALLOWED_ORIGINS"),
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        validation_alias=AliasChoices("NOTIFICATION_API_CORS_ALLOW_CREDENTIALS", "CORS_ALLOW_CREDENTIALS"),
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
    # EMAIL
    # ------------------------------------
    SENDGRID_API_KEY: str | None = Field(
        default=None,
        validation_alias=AliasChoices("NOTIFICATION_SENDGRID_API_KEY", "SENDGRID_API_KEY"),
    )
    DEFAULT_EMAIL_FROM: str = Field(
        default="noreply@atlas.local",
        validation_alias=AliasChoices("NOTIFICATION_DEFAULT_EMAIL_FROM", "DEFAULT_EMAIL_FROM"),
    )

    # ------------------------------------
    # SLACK
    # ------------------------------------
    SLACK_WEBHOOK_URL: str | None = Field(
        default=None,
        validation_alias=AliasChoices("NOTIFICATION_SLACK_WEBHOOK_URL", "SLACK_WEBHOOK_URL"),
    )
    SLACK_DEFAULT_CHANNEL: str | None = Field(
        default=None,
        validation_alias=AliasChoices("NOTIFICATION_SLACK_DEFAULT_CHANNEL", "SLACK_DEFAULT_CHANNEL"),
    )

    # ------------------------------------
    # SERVICE AUTH
    # ------------------------------------
    SERVICE_JWT_SECRET_KEY: str = Field(
        default="atlas-service-jwt-dev-secret-change-me-32-bytes",
        validation_alias=AliasChoices("NOTIFICATION_SERVICE_JWT_SECRET_KEY", "SERVICE_JWT_SECRET_KEY"),
    )
    SERVICE_JWT_ALGORITHM: str = Field(
        default="HS256",
        validation_alias=AliasChoices("NOTIFICATION_SERVICE_JWT_ALGORITHM", "SERVICE_JWT_ALGORITHM"),
    )
    SERVICE_JWT_ISSUER: str = Field(
        default="atlascore",
        validation_alias=AliasChoices("NOTIFICATION_SERVICE_JWT_ISSUER", "SERVICE_JWT_ISSUER"),
    )
    SERVICE_JWT_TTL_SECONDS: int = Field(
        default=300,
        validation_alias=AliasChoices("NOTIFICATION_SERVICE_JWT_TTL_SECONDS", "SERVICE_JWT_TTL_SECONDS"),
    )
    SERVICE_JWT_ALLOWED_CALLERS_RAW: str = Field(
        default="auth_api,core_api",
        validation_alias=AliasChoices("NOTIFICATION_SERVICE_JWT_ALLOWED_CALLERS", "SERVICE_JWT_ALLOWED_CALLERS"),
    )

    @property
    def SERVICE_JWT_ALLOWED_CALLERS(self) -> tuple[str, ...]:
        return tuple(
            item.strip()
            for item in self.SERVICE_JWT_ALLOWED_CALLERS_RAW.split(",")
            if item.strip()
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


settings = NotificationSettings()
