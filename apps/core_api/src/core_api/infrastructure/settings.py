from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared_kernel.http import CorsConfig, parse_cors_origins

SETTINGS_CONFIG = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="ignore",
    populate_by_name=True,
)


class CoreSettings(BaseSettings):
    # ------------------------------------
    # APP
    # ------------------------------------
    APP_NAME: str = "AtlasCore"
    ENVIRONMENT: str = "development"
    DEBUG: bool = Field(default=True, validation_alias=AliasChoices("APP_DEBUG", "ATLAS_DEBUG"))
    SERVICE_NAME: str = "core_api"

    # ------------------------------------
    # POSTGRES
    # ------------------------------------
    POSTGRES_USER: str = "atlas"
    POSTGRES_PASSWORD: str = "atlas"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "atlas_core"
    CORE_POSTGRES_DB: str = "atlas_core"
    DATABASE_URL_OVERRIDE: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CORE_DATABASE_URL", "DATABASE_URL", "DATABASE_URL_OVERRIDE"),
    )

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.CORE_POSTGRES_DB}"
        )

    # ------------------------------------
    # REDIS
    # ------------------------------------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    REDIS_KEY_PREFIX: str = Field(default="core", validation_alias=AliasChoices("CORE_REDIS_KEY_PREFIX", "REDIS_KEY_PREFIX"))
    REDIS_URL_OVERRIDE: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CORE_REDIS_URL", "REDIS_URL", "REDIS_URL_OVERRIDE"),
    )

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_URL_OVERRIDE:
            return self.REDIS_URL_OVERRIDE
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ------------------------------------
    # CORS
    # ------------------------------------
    CORS_ENABLED: bool = Field(default=True, validation_alias=AliasChoices("CORE_API_CORS_ENABLED", "CORS_ENABLED"))
    CORS_ALLOWED_ORIGINS_RAW: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        validation_alias=AliasChoices("CORE_API_CORS_ALLOWED_ORIGINS", "CORS_ALLOWED_ORIGINS"),
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        validation_alias=AliasChoices("CORE_API_CORS_ALLOW_CREDENTIALS", "CORS_ALLOW_CREDENTIALS"),
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
    # AUTH API
    # ------------------------------------
    AUTH_API_INTERNAL_URL: str = "http://localhost:8001"
    AUTH_INTROSPECTION_PATH: str = "/internal/auth/introspect"
    AUTH_INTROSPECTION_TIMEOUT_SECONDS: float = Field(
        default=1.0,
        validation_alias=AliasChoices("AUTH_INTROSPECTION_TIMEOUT_SECONDS", "AUTH_API_CHECK_TIMEOUT_SECONDS"),
    )

    # ------------------------------------
    # PYDANTIC
    # ------------------------------------
    model_config = SETTINGS_CONFIG


settings = CoreSettings()
