from collections.abc import Generator

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from auth_api.infrastructure.database.base import Base
from auth_api.infrastructure.database.connection import get_session
from auth_api.main import app
from auth_api.modules.auth.presentation import routes as auth_routes
from auth_api.modules.sessions.application.service import SessionService, get_session_service
from auth_api.modules.sessions.application.stores import InMemorySessionStore

SERVICE_HEADERS = {
    "X-Atlas-Service": "core_api",
    "X-Atlas-Service-Key": "atlas-core-to-auth-dev-key",
}


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

        admin_introspection_response = await client.post(
            "/internal/auth/introspect",
            headers={**auth_headers, **SERVICE_HEADERS},
            json={"required_permission": {"domain": "users", "action": "delete"}},
        )
        assert admin_introspection_response.status_code == 200
        assert admin_introspection_response.json()["active"] is True
        assert admin_introspection_response.json()["allowed"] is True
        assert admin_introspection_response.json()["user"]["email"] == "admin@atlas.local"

        catalog_response = await client.get("/access-control/permissions/catalog", headers=auth_headers)
        assert catalog_response.status_code == 200
        catalog_values = {permission["value"] for permission in catalog_response.json()}
        assert "access_control:read" in catalog_values
        assert "books:write" in catalog_values

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
        user_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

        allowed_introspection_response = await client.post(
            "/internal/auth/introspect",
            headers={**user_headers, **SERVICE_HEADERS},
            json={"required_permission": {"domain": "users", "action": "read"}},
        )
        assert allowed_introspection_response.status_code == 200
        assert allowed_introspection_response.json()["allowed"] is True

        denied_introspection_response = await client.post(
            "/internal/auth/introspect",
            headers={**user_headers, **SERVICE_HEADERS},
            json={"required_permission": {"domain": "users", "action": "write"}},
        )
        assert denied_introspection_response.status_code == 200
        assert denied_introspection_response.json()["allowed"] is False

        change_password_response = await client.post(
            "/auth/change-password",
            headers=user_headers,
            json={
                "current_password": "AtlasUser456!",
                "new_password": "AtlasUser789!",
            },
        )
        assert change_password_response.status_code == 200
        assert change_password_response.json()["changed"] is True

        old_password_response = await client.post(
            "/auth/login",
            json={"email": "user@atlas.local", "password": "AtlasUser456!"},
        )
        assert old_password_response.status_code == 401

        new_password_response = await client.post(
            "/auth/login",
            json={"email": "user@atlas.local", "password": "AtlasUser789!"},
        )
        assert new_password_response.status_code == 200

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


@pytest.mark.asyncio
async def test_auth_rejects_weak_password(auth_database: None) -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/users",
            json={
                "email": "user@atlas.local",
                "full_name": "Atlas User",
                "password": "weakpass",
            },
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "auth.weak_password"
    assert set(response.json()["error"]["target"]["payload"]["missing_requirements"]) == {
        "min_length",
        "uppercase",
        "number",
        "special",
    }


@pytest.mark.asyncio
async def test_auth_password_recovery_resets_password(
    auth_database: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(auth_routes.settings, "AUTH_EXPOSE_PASSWORD_RESET_TOKEN", True)
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

        recovery_response = await client.post(
            "/auth/password-recovery/request",
            json={"email": "user@atlas.local"},
        )
        assert recovery_response.status_code == 200
        reset_token = recovery_response.json()["reset_token"]
        assert reset_token

        confirm_response = await client.post(
            "/auth/password-recovery/confirm",
            json={
                "reset_token": reset_token,
                "new_password": "AtlasUser456!",
            },
        )
        assert confirm_response.status_code == 200

        old_login_response = await client.post(
            "/auth/login",
            json={"email": "user@atlas.local", "password": "AtlasUser123!"},
        )
        new_login_response = await client.post(
            "/auth/login",
            json={"email": "user@atlas.local", "password": "AtlasUser456!"},
        )

    assert old_login_response.status_code == 401
    assert new_login_response.status_code == 200


@pytest.mark.asyncio
async def test_auth_login_blocks_after_too_many_failed_attempts(
    auth_database: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(auth_routes.settings, "AUTH_LOGIN_MAX_ATTEMPTS", 2)
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

        first_response = await client.post(
            "/auth/login",
            json={"email": "user@atlas.local", "password": "WrongPassword123!"},
        )
        second_response = await client.post(
            "/auth/login",
            json={"email": "user@atlas.local", "password": "WrongPassword123!"},
        )
        blocked_response = await client.post(
            "/auth/login",
            json={"email": "user@atlas.local", "password": "AtlasUser123!"},
        )

    assert first_response.status_code == 401
    assert second_response.status_code == 401
    assert blocked_response.status_code == 429
    assert blocked_response.json()["error"]["code"] == "auth.too_many_login_attempts"


@pytest.mark.asyncio
async def test_auth_introspection_requires_internal_service_credentials(auth_database: None) -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/users",
            json={
                "email": "admin@atlas.local",
                "full_name": "Atlas Admin",
                "password": "AtlasAdmin123!",
                "is_superuser": True,
            },
        )
        login_response = await client.post(
            "/auth/login",
            json={"email": "admin@atlas.local", "password": "AtlasAdmin123!"},
        )
        auth_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

        missing_service_response = await client.post(
            "/internal/auth/introspect",
            headers=auth_headers,
            json={"required_permission": {"domain": "books", "action": "write"}},
        )
        invalid_service_response = await client.post(
            "/internal/auth/introspect",
            headers={**auth_headers, "X-Atlas-Service": "core_api", "X-Atlas-Service-Key": "wrong"},
            json={"required_permission": {"domain": "books", "action": "write"}},
        )

    assert missing_service_response.status_code == 403
    assert missing_service_response.json()["error"]["code"] == "auth.service_authentication_failed"
    assert invalid_service_response.status_code == 403
    assert invalid_service_response.json()["error"]["code"] == "auth.service_authentication_failed"


def test_auth_user_routes_are_registered() -> None:
    paths = {route.path for route in app.routes}

    assert "/users" in paths
    assert "/users/{user_id}" in paths
    assert "/users/{user_id}/restore" in paths
    assert "/auth/login" in paths
    assert "/auth/refresh" in paths
    assert "/auth/logout" in paths
    assert "/auth/logout-all" in paths
    assert "/auth/change-password" in paths
    assert "/auth/password-recovery/request" in paths
    assert "/auth/password-recovery/confirm" in paths
    assert "/internal/auth/introspect" in paths
    assert "/sessions/me" in paths
    assert "/access-control/me" in paths
    assert "/access-control/permissions/catalog" in paths
