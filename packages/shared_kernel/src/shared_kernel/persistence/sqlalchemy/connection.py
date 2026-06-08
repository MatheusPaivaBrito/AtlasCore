from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker


def create_sync_engine(database_url: str, *, pool_pre_ping: bool = True) -> Engine:
    return create_engine(
        database_url,
        pool_pre_ping=pool_pre_ping,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )


def create_session_dependency(session_factory: sessionmaker[Session]):
    def get_session() -> Generator[Session, None, None]:
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    return get_session
