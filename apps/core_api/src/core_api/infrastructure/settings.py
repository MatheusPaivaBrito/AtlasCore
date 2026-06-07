from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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
    # API PORTS
    # ------------------------------------
    CORE_API_PORT: int = 8000
    AUTH_API_PORT: int = 8001
    EVENTING_API_PORT: int = 8002
    NOTIFICATION_API_PORT: int = 8003
    OBSERVABILITY_API_PORT: int = 8004

    # ------------------------------------
    # AUTH API DISCOVERY
    # ------------------------------------
    AUTH_API_PUBLIC_URL: str = "http://localhost:8001"
    AUTH_API_HEALTH_PATH: str = "/health"
    AUTH_API_DOCS_PATH: str = "/docs"
    AUTH_API_CHECK_TIMEOUT_SECONDS: float = 0.2

    # ------------------------------------
    # KAFKA
    # ------------------------------------
    KAFKA_HOST: str = "localhost"
    KAFKA_PORT: int = 9092
    KAFKA_BOOTSTRAP_SERVERS_OVERRIDE: str | None = Field(
        default=None,
        validation_alias=AliasChoices("KAFKA_BOOTSTRAP_SERVERS", "KAFKA_BOOTSTRAP_SERVERS_OVERRIDE"),
    )

    @property
    def KAFKA_BOOTSTRAP_SERVERS(self) -> str:
        if self.KAFKA_BOOTSTRAP_SERVERS_OVERRIDE:
            return self.KAFKA_BOOTSTRAP_SERVERS_OVERRIDE
        return f"{self.KAFKA_HOST}:{self.KAFKA_PORT}"

    # ------------------------------------
    # DOCUMENTATION
    # ------------------------------------
    DOCS_PT_PORT: int = 8080
    DOCS_EN_PORT: int = 8081

    # ------------------------------------
    # PYDANTIC
    # ------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


settings = Settings()
