from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core_api.infrastructure.settings import settings


# ------------------------------------
# ENGINE
# ------------------------------------
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# ------------------------------------
# SESSION FACTORY
# ------------------------------------
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


# ------------------------------------
# FASTAPI DEPENDENCY
# ------------------------------------
def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
