from core_api.infrastructure.settings import Settings


def test_settings_builds_connection_values_from_env_parts() -> None:
    settings = Settings(
        APP_DEBUG=False,
        POSTGRES_USER="atlas",
        POSTGRES_PASSWORD="secret",
        POSTGRES_HOST="postgres",
        POSTGRES_PORT=5433,
        POSTGRES_DB="atlas_test",
        REDIS_HOST="redis",
        REDIS_PORT=6380,
        REDIS_DB=2,
        KAFKA_HOST="kafka",
        KAFKA_PORT=9094,
    )

    assert settings.DEBUG is False
    assert settings.DATABASE_URL == "postgresql+psycopg://atlas:secret@postgres:5433/atlas_test"
    assert settings.REDIS_URL == "redis://redis:6380/2"
    assert settings.KAFKA_BOOTSTRAP_SERVERS == "kafka:9094"


def test_settings_allow_connection_url_overrides() -> None:
    settings = Settings(
        DATABASE_URL_OVERRIDE="postgresql+psycopg://override:secret@db:5432/app",
        REDIS_URL_OVERRIDE="redis://cache:6379/4",
        KAFKA_BOOTSTRAP_SERVERS_OVERRIDE="broker:9092",
    )

    assert settings.DATABASE_URL == "postgresql+psycopg://override:secret@db:5432/app"
    assert settings.REDIS_URL == "redis://cache:6379/4"
    assert settings.KAFKA_BOOTSTRAP_SERVERS == "broker:9092"
