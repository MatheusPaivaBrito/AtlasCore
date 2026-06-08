from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

import auth_api.infrastructure.database.loader  # noqa: F401
from auth_api.infrastructure.database.base import Base
from auth_api.infrastructure.settings import settings

# ------------------------------------
# Alembic Config
# ------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = settings.DATABASE_URL or config.get_main_option("sqlalchemy.url")
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata


# ------------------------------------
# Migration Runners
# ------------------------------------
def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# ------------------------------------
# Mode Selection
# ------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
