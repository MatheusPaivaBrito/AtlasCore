from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared_kernel.http import CorsConfig, parse_cors_origins


class AuthSettings(BaseSettings):
    # ------------------------------------
    # APP
    # ------------------------------------
    APP_NAME: str = "AtlasCore"
    SERVICE_NAME: str = Field(
        default="auth_api",
        validation_alias=AliasChoices("AUTH_SERVICE_NAME", "SERVICE_NAME"),
    )

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
    AUTH_PASSWORD_RESET_TOKEN_TTL_SECONDS: int = Field(
        default=900,
        validation_alias=AliasChoices("AUTH_PASSWORD_RESET_TOKEN_TTL_SECONDS", "PASSWORD_RESET_TOKEN_TTL_SECONDS"),
    )
    AUTH_EXPOSE_PASSWORD_RESET_TOKEN: bool = Field(
        default=False,
        validation_alias=AliasChoices("AUTH_EXPOSE_PASSWORD_RESET_TOKEN", "EXPOSE_PASSWORD_RESET_TOKEN"),
    )
    AUTH_LOGIN_MAX_ATTEMPTS: int = Field(
        default=5,
        validation_alias=AliasChoices("AUTH_LOGIN_MAX_ATTEMPTS", "LOGIN_MAX_ATTEMPTS"),
    )
    AUTH_LOGIN_WINDOW_SECONDS: int = Field(
        default=900,
        validation_alias=AliasChoices("AUTH_LOGIN_WINDOW_SECONDS", "LOGIN_WINDOW_SECONDS"),
    )
    AUTH_LOGIN_BLOCK_SECONDS: int = Field(
        default=900,
        validation_alias=AliasChoices("AUTH_LOGIN_BLOCK_SECONDS", "LOGIN_BLOCK_SECONDS"),
    )

    @property
    def AUTH_SESSION_TTL_SECONDS(self) -> int:
        return self.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    # ------------------------------------
    # INTERNAL SERVICE AUTH
    # ------------------------------------
    INTERNAL_SERVICE_KEYS_RAW: str = Field(
        default="core_api:atlas-core-to-auth-dev-key",
        validation_alias=AliasChoices("AUTH_INTERNAL_SERVICE_KEYS", "INTERNAL_SERVICE_KEYS"),
    )

    @property
    def INTERNAL_SERVICE_KEYS(self) -> dict[str, str]:
        keys: dict[str, str] = {}
        for item in self.INTERNAL_SERVICE_KEYS_RAW.split(","):
            service_pair = item.strip()
            if not service_pair or ":" not in service_pair:
                continue
            service_name, service_key = service_pair.split(":", 1)
            service_name = service_name.strip()
            service_key = service_key.strip()
            if service_name and service_key:
                keys[service_name] = service_key
        return keys

    # ------------------------------------
    # PASSWORDS
    # ------------------------------------
    BCRYPT_ROUNDS: int = Field(default=12, validation_alias=AliasChoices("AUTH_BCRYPT_ROUNDS", "BCRYPT_ROUNDS"))
    AUTH_PASSWORD_MIN_LENGTH: int = Field(
        default=10,
        validation_alias=AliasChoices("AUTH_PASSWORD_MIN_LENGTH", "PASSWORD_MIN_LENGTH"),
    )
    AUTH_PASSWORD_REQUIRE_UPPERCASE: bool = Field(
        default=True,
        validation_alias=AliasChoices("AUTH_PASSWORD_REQUIRE_UPPERCASE", "PASSWORD_REQUIRE_UPPERCASE"),
    )
    AUTH_PASSWORD_REQUIRE_LOWERCASE: bool = Field(
        default=True,
        validation_alias=AliasChoices("AUTH_PASSWORD_REQUIRE_LOWERCASE", "PASSWORD_REQUIRE_LOWERCASE"),
    )
    AUTH_PASSWORD_REQUIRE_NUMBER: bool = Field(
        default=True,
        validation_alias=AliasChoices("AUTH_PASSWORD_REQUIRE_NUMBER", "PASSWORD_REQUIRE_NUMBER"),
    )
    AUTH_PASSWORD_REQUIRE_SPECIAL: bool = Field(
        default=True,
        validation_alias=AliasChoices("AUTH_PASSWORD_REQUIRE_SPECIAL", "PASSWORD_REQUIRE_SPECIAL"),
    )

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
