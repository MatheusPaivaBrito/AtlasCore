from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    DATABASE_URL_OVERRIDE: str | None = Field(
        default=None,
        validation_alias=AliasChoices("DATABASE_URL", "DATABASE_URL_OVERRIDE"),
    )

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )

    # ------------------------------------
    # REDIS
    # ------------------------------------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    REDIS_URL_OVERRIDE: str | None = Field(
        default=None,
        validation_alias=AliasChoices("REDIS_URL", "REDIS_URL_OVERRIDE"),
    )

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_URL_OVERRIDE:
            return self.REDIS_URL_OVERRIDE
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ------------------------------------
    # PYDANTIC
    # ------------------------------------
    model_config = SETTINGS_CONFIG


settings = CoreSettings()
