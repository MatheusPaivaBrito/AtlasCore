from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared_kernel.http import CorsConfig, parse_cors_origins


class AuthSettings(BaseSettings):
    # ------------------------------------
    # APP
    # ------------------------------------
    APP_NAME: str = "AtlasCore"
    SERVICE_NAME: str = "auth_api"

    # ------------------------------------
    # POSTGRES
    # ------------------------------------
    POSTGRES_USER: str = "atlas"
    POSTGRES_PASSWORD: str = "atlas"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    AUTH_POSTGRES_DB: str = "atlas_auth"
    DATABASE_URL_OVERRIDE: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AUTH_DATABASE_URL", "DATABASE_URL", "DATABASE_URL_OVERRIDE"),
    )

    @property
    def DATABASE_URL(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        return (
            f"postgresql+psycopg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.AUTH_POSTGRES_DB}"
        )

    # ------------------------------------
    # REDIS
    # ------------------------------------
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    AUTH_REDIS_DB: int = 1
    REDIS_KEY_PREFIX: str = Field(default="auth", validation_alias=AliasChoices("AUTH_REDIS_KEY_PREFIX", "REDIS_KEY_PREFIX"))
    REDIS_URL_OVERRIDE: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AUTH_REDIS_URL", "REDIS_URL", "REDIS_URL_OVERRIDE"),
    )
    REDIS_SOCKET_TIMEOUT_SECONDS: float = Field(
        default=1.0,
        validation_alias=AliasChoices("AUTH_REDIS_SOCKET_TIMEOUT_SECONDS", "REDIS_SOCKET_TIMEOUT_SECONDS"),
    )

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_URL_OVERRIDE:
            return self.REDIS_URL_OVERRIDE
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.AUTH_REDIS_DB}"

    # ------------------------------------
    # JWT
    # ------------------------------------
    JWT_ACCESS_TOKEN_SECRET_KEY: str = Field(
        default="atlas-auth-dev-access-secret-change-me-32-bytes",
        validation_alias=AliasChoices("AUTH_JWT_ACCESS_TOKEN_SECRET_KEY", "JWT_ACCESS_TOKEN_SECRET_KEY"),
    )
    JWT_REFRESH_TOKEN_SECRET_KEY: str = Field(
        default="atlas-auth-dev-refresh-secret-change-me-32-bytes",
        validation_alias=AliasChoices("AUTH_JWT_REFRESH_TOKEN_SECRET_KEY", "JWT_REFRESH_TOKEN_SECRET_KEY"),
    )
    JWT_ALGORITHM: str = Field(default="HS256", validation_alias=AliasChoices("AUTH_JWT_ALGORITHM", "JWT_ALGORITHM"))
    JWT_ISSUER: str = Field(default="atlascore.auth", validation_alias=AliasChoices("AUTH_JWT_ISSUER", "JWT_ISSUER"))
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15,
        validation_alias=AliasChoices("AUTH_JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "JWT_ACCESS_TOKEN_EXPIRE_MINUTES"),
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        validation_alias=AliasChoices("AUTH_JWT_REFRESH_TOKEN_EXPIRE_DAYS", "JWT_REFRESH_TOKEN_EXPIRE_DAYS"),
    )

    # ------------------------------------
    # AUTH COOKIES
    # ------------------------------------
    JWT_COOKIE_SECURE: bool = Field(
        default=False,
        validation_alias=AliasChoices("AUTH_JWT_COOKIE_SECURE", "JWT_COOKIE_SECURE"),
    )
    JWT_COOKIE_SAMESITE: str = Field(
        default="lax",
        validation_alias=AliasChoices("AUTH_JWT_COOKIE_SAMESITE", "JWT_COOKIE_SAMESITE"),
    )
    JWT_COOKIE_PATH: str = Field(default="/", validation_alias=AliasChoices("AUTH_JWT_COOKIE_PATH", "JWT_COOKIE_PATH"))

    # ------------------------------------
    # SESSIONS AND PERMISSIONS
    # ------------------------------------
    AUTH_MAX_DEVICES: int = Field(default=3, validation_alias=AliasChoices("AUTH_MAX_DEVICES", "MAX_DEVICES"))
    AUTH_PERMISSIONS_TTL_SECONDS: int = Field(
        default=3600,
        validation_alias=AliasChoices("AUTH_PERMISSIONS_TTL_SECONDS", "USER_REDIS_TTL"),
    )

    @property
    def AUTH_SESSION_TTL_SECONDS(self) -> int:
        return self.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    # ------------------------------------
    # PASSWORDS
    # ------------------------------------
    BCRYPT_ROUNDS: int = Field(default=12, validation_alias=AliasChoices("AUTH_BCRYPT_ROUNDS", "BCRYPT_ROUNDS"))

    # ------------------------------------
    # CORS
    # ------------------------------------
    CORS_ENABLED: bool = Field(default=True, validation_alias=AliasChoices("AUTH_API_CORS_ENABLED", "CORS_ENABLED"))
    CORS_ALLOWED_ORIGINS_RAW: str = Field(
        default="http://localhost:3000,http://localhost:5173",
        validation_alias=AliasChoices("AUTH_API_CORS_ALLOWED_ORIGINS", "CORS_ALLOWED_ORIGINS"),
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(
        default=True,
        validation_alias=AliasChoices("AUTH_API_CORS_ALLOW_CREDENTIALS", "CORS_ALLOW_CREDENTIALS"),
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
    # PYDANTIC
    # ------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


settings = AuthSettings()
