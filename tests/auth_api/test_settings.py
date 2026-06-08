from auth_api.infrastructure.settings import AuthSettings


def test_auth_settings_build_database_and_redis_urls() -> None:
    settings = AuthSettings(
        POSTGRES_USER="atlas",
        POSTGRES_PASSWORD="secret",
        POSTGRES_HOST="postgres",
        POSTGRES_PORT=5433,
        AUTH_POSTGRES_DB="atlas_auth_test",
        REDIS_HOST="redis",
        REDIS_PORT=6380,
        AUTH_REDIS_DB=3,
        AUTH_REDIS_KEY_PREFIX="auth",
        AUTH_BCRYPT_ROUNDS=12,
    )

    assert settings.DATABASE_URL == "postgresql+psycopg://atlas:secret@postgres:5433/atlas_auth_test"
    assert settings.REDIS_URL == "redis://redis:6380/3"
    assert settings.REDIS_KEY_PREFIX == "auth"
    assert settings.BCRYPT_ROUNDS == 12
