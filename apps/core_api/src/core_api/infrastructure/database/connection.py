from core_api.infrastructure.settings import settings
from shared_kernel.persistence.sqlalchemy import (
    create_session_dependency,
    create_session_factory,
    create_sync_engine,
)


# ------------------------------------
# ENGINE
# ------------------------------------
engine = create_sync_engine(
    settings.DATABASE_URL,
)

# ------------------------------------
# SESSION FACTORY
# ------------------------------------
SessionLocal = create_session_factory(engine)


# ------------------------------------
# FASTAPI DEPENDENCY
# ------------------------------------
get_session = create_session_dependency(SessionLocal)
