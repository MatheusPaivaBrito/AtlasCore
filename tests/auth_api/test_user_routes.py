from collections.abc import Generator

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from auth_api.infrastructure.database.base import Base
from auth_api.infrastructure.database.connection import get_session
from auth_api.main import app
from auth_api.modules.sessions.application.service import SessionService, get_session_service
from auth_api.modules.sessions.application.stores import InMemorySessionStore


@pytest.fixture
def auth_database() -> Generator[None, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_session() -> Generator[Session, None, None]:
        session = testing_session_local()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    session_service = SessionService(InMemorySessionStore())

    def override_get_session_service() -> SessionService:
        return session_service

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_session_service] = override_get_session_service

    try:
        yield
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.mark.asyncio
async def test_auth_user_crud_restore_and_login(auth_database: None) -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        bootstrap_response = await client.post(
            "/users",
            json={
                "email": "Admin@Atlas.Local",
                "full_name": "Atlas Admin",
                "password": "AtlasAdmin123!",
                "is_active": True,
                "is_superuser": True,
            },
        )
        assert bootstrap_response.status_code == 201
        admin = bootstrap_response.json()
        assert admin["email"] == "admin@atlas.local"
        assert admin["token_version"] == 1
        assert "password" not in admin
        assert "password_hash" not in admin

        admin_login_response = await client.post(
            "/auth/login",
            json={"email": "admin@atlas.local", "password": "AtlasAdmin123!"},
        )
        assert admin_login_response.status_code == 200
        admin_auth = admin_login_response.json()
        assert admin_auth["authenticated"] is True
        assert admin_auth["user"]["id"] == admin["id"]
        assert admin_auth["access_token"]
        assert admin_auth["refresh_token"]
        auth_headers = {"Authorization": f"Bearer {admin_auth['access_token']}"}

        create_response = await client.post(
            "/users",
            headers=auth_headers,
            json={
                "email": "User@Atlas.Local",
                "full_name": "Atlas User",
                "password": "AtlasUser123!",
                "is_active": True,
                "is_superuser": False,
                "permissions": [{"domain": "users", "action": "read"}],
            },
        )
        assert create_response.status_code == 201
        created = create_response.json()
        assert created["email"] == "user@atlas.local"
        assert created["permissions"] == [{"domain": "users", "action": "read"}]

        user_id = created["id"]

        list_response = await client.get("/users", headers=auth_headers)
        assert list_response.status_code == 200
        assert [user["email"] for user in list_response.json()] == ["admin@atlas.local", "user@atlas.local"]

        get_response = await client.get(f"/users/{user_id}", headers=auth_headers)
        assert get_response.status_code == 200
        assert get_response.json()["email"] == "user@atlas.local"

        update_response = await client.patch(
            f"/users/{user_id}",
            headers=auth_headers,
            json={
                "full_name": "Atlas Root Admin",
                "password": "AtlasUser456!",
            },
        )
        assert update_response.status_code == 200
        assert update_response.json()["full_name"] == "Atlas Root Admin"
        assert update_response.json()["token_version"] == 2

        login_response = await client.post(
            "/auth/login",
            json={"email": "user@atlas.local", "password": "AtlasUser456!"},
        )
        assert login_response.status_code == 200
        assert login_response.json()["authenticated"] is True
        assert login_response.json()["user"]["id"] == user_id

        delete_response = await client.delete(f"/users/{user_id}", headers=auth_headers)
        assert delete_response.status_code == 204

        deleted_get_response = await client.get(f"/users/{user_id}", headers=auth_headers)
        assert deleted_get_response.status_code == 404

        deleted_query_response = await client.get(f"/users/{user_id}?include_deleted=true", headers=auth_headers)
        assert deleted_query_response.status_code == 200
        assert deleted_query_response.json()["deleted_at"] is not None

        restore_response = await client.post(f"/users/{user_id}/restore", headers=auth_headers)
        assert restore_response.status_code == 200
        assert restore_response.json()["deleted_at"] is None


@pytest.mark.asyncio
async def test_auth_login_rejects_invalid_credentials(auth_database: None) -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/users",
            json={
                "email": "user@atlas.local",
                "full_name": "Atlas User",
                "password": "AtlasUser123!",
            },
        )

        response = await client.post(
            "/auth/login",
            json={"email": "user@atlas.local", "password": "WrongPassword123!"},
        )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "auth.invalid_credentials"


def test_auth_user_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/users" in paths
    assert "/users/{user_id}" in paths
    assert "/users/{user_id}/restore" in paths
    assert "/auth/login" in paths
    assert "/auth/refresh" in paths
    assert "/auth/logout" in paths
    assert "/auth/logout-all" in paths
    assert "/sessions/me" in paths
    assert "/access-control/me" in paths
