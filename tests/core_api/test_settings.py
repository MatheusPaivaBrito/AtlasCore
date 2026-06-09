from core_api.infrastructure.platform_discovery import PlatformDiscoverySettings
from core_api.infrastructure.settings import CoreSettings


def test_settings_builds_connection_values_from_env_parts() -> None:
    settings = CoreSettings(
        APP_DEBUG=False,
        POSTGRES_USER="atlas",
        POSTGRES_PASSWORD="secret",
        POSTGRES_HOST="postgres",
        POSTGRES_PORT=5433,
        CORE_POSTGRES_DB="atlas_core_test",
        REDIS_HOST="redis",
        REDIS_PORT=6380,
        CORE_REDIS_DB=2,
        CORE_REDIS_KEY_PREFIX="core",
        AUTH_API_INTERNAL_URL="http://auth-api:8000",
        AUTH_INTROSPECTION_TIMEOUT_SECONDS=0.7,
        CORE_TO_AUTH_SERVICE_KEY="core-secret",
    )

    assert settings.DEBUG is False
    assert settings.DATABASE_URL == "postgresql+psycopg://atlas:secret@postgres:5433/atlas_core_test"
    assert settings.REDIS_URL == "redis://redis:6380/2"
    assert settings.REDIS_KEY_PREFIX == "core"
    assert settings.AUTH_API_INTERNAL_URL == "http://auth-api:8000"
    assert settings.AUTH_INTROSPECTION_PATH == "/internal/auth/introspect"
    assert settings.AUTH_INTROSPECTION_TIMEOUT_SECONDS == 0.7
    assert settings.CORE_TO_AUTH_SERVICE_KEY == "core-secret"


def test_settings_allow_connection_url_overrides() -> None:
    settings = CoreSettings(
        DATABASE_URL_OVERRIDE="postgresql+psycopg://override:secret@db:5432/app",
        REDIS_URL_OVERRIDE="redis://cache:6379/4",
    )

    assert settings.DATABASE_URL == "postgresql+psycopg://override:secret@db:5432/app"
    assert settings.REDIS_URL == "redis://cache:6379/4"


def test_settings_describe_core_cors_policy() -> None:
    settings = CoreSettings(
        CORE_API_CORS_ALLOWED_ORIGINS="http://localhost:5173/, http://localhost:3000",
        CORE_API_CORS_ALLOW_CREDENTIALS=True,
    )

    assert settings.CORS_ALLOWED_ORIGINS == ("http://localhost:5173", "http://localhost:3000")
    assert settings.CORS_CONFIG.allow_origins == ("http://localhost:5173", "http://localhost:3000")
    assert settings.CORS_CONFIG.allow_credentials is True


def test_platform_discovery_settings_describe_local_service_urls() -> None:
    settings = PlatformDiscoverySettings(
        APP_NAME="AtlasCore Test",
        CORE_API_PORT=9000,
        AUTH_API_PORT=9001,
        AUTH_API_PUBLIC_URL="http://auth.local",
        AUTH_API_INTERNAL_URL="http://auth-api:8000",
        DOCS_PT_PORT=9080,
        DOCS_EN_PUBLIC_URL_OVERRIDE="http://docs.local/en",
        AUTH_API_CHECK_TIMEOUT_SECONDS=0.5,
    )

    assert settings.APP_NAME == "AtlasCore Test"
    assert settings.CORE_API_PORT == 9000
    assert settings.AUTH_API_PORT == 9001
    assert settings.AUTH_API_PUBLIC_URL == "http://auth.local"
    assert settings.AUTH_API_INTERNAL_URL == "http://auth-api:8000"
    assert settings.DOCS_PT_PUBLIC_URL == "http://localhost:9080"
    assert settings.DOCS_EN_PUBLIC_URL == "http://docs.local/en"
    assert settings.SERVICE_CHECK_TIMEOUT_SECONDS == 0.5
