from uuid import uuid4

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
import orjson
import pytest

from core_api.bootstrap.exceptions import register_api_exception_handlers
from core_api.shared.auth import client as auth_client_module
from core_api.shared.auth.client import AuthIntrospectionClient, get_auth_introspection_client
from core_api.shared.auth.guards import core_auth_guard
from core_api.shared.auth.schemas import AuthIntrospectionResponse, AuthorizedUser, RequiredPermission


class FakeAuthIntrospectionClient:
    def __init__(self, *, allowed: bool) -> None:
        self.allowed = allowed
        self.token: str | None = None
        self.required_permission: RequiredPermission | None = None

    def introspect(
        self,
        *,
        access_token: str,
        required_permission: RequiredPermission,
    ) -> AuthIntrospectionResponse:
        self.token = access_token
        self.required_permission = required_permission
        return AuthIntrospectionResponse(
            active=True,
            allowed=self.allowed,
            user=AuthorizedUser(
                id=uuid4(),
                email="admin@atlas.local",
                is_active=True,
                is_superuser=True,
                token_version=1,
            ),
            permissions=[required_permission],
            required_permission=required_permission,
        )


def build_test_app(fake_client: FakeAuthIntrospectionClient) -> FastAPI:
    app = FastAPI()
    register_api_exception_handlers(app)
    app.dependency_overrides[get_auth_introspection_client] = lambda: fake_client

    @app.post("/protected")
    def protected_route(
        user: AuthorizedUser = core_auth_guard.require_permission(domain="books", action="write"),
    ) -> dict[str, str]:
        return {"user_id": str(user.id), "email": user.email}

    return app


@pytest.mark.asyncio
async def test_core_auth_guard_allows_valid_permission() -> None:
    fake_client = FakeAuthIntrospectionClient(allowed=True)
    app = build_test_app(fake_client)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/protected", headers={"Authorization": "Bearer valid-token"})

    assert response.status_code == 200
    assert response.json()["email"] == "admin@atlas.local"
    assert fake_client.token == "valid-token"
    assert fake_client.required_permission == RequiredPermission(domain="books", action="write")


@pytest.mark.asyncio
async def test_core_auth_guard_rejects_missing_token() -> None:
    app = build_test_app(FakeAuthIntrospectionClient(allowed=True))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/protected")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "core_api.authentication_required"


@pytest.mark.asyncio
async def test_core_auth_guard_rejects_denied_permission() -> None:
    app = build_test_app(FakeAuthIntrospectionClient(allowed=False))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/protected", headers={"Authorization": "Bearer valid-token"})

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "core_api.authorization_denied"


def test_core_auth_client_sends_internal_service_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_headers: dict[str, str] = {}
    user_id = uuid4()

    class FakeResponse:
        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *args: object) -> None:
            return None

        @staticmethod
        def read() -> bytes:
            return orjson.dumps(
                {
                    "active": True,
                    "allowed": True,
                    "user": {
                        "id": str(user_id),
                        "email": "admin@atlas.local",
                        "is_active": True,
                        "is_superuser": True,
                        "token_version": 1,
                    },
                    "permissions": [{"domain": "books", "action": "write"}],
                    "required_permission": {"domain": "books", "action": "write"},
                }
            )

    def fake_urlopen(request, timeout: float) -> FakeResponse:
        captured_headers.update({key.lower(): value for key, value in request.header_items()})
        return FakeResponse()

    monkeypatch.setattr(auth_client_module.settings, "SERVICE_NAME", "core_api")
    monkeypatch.setattr(auth_client_module.settings, "CORE_TO_AUTH_SERVICE_KEY", "core-secret")
    monkeypatch.setattr(auth_client_module, "urlopen", fake_urlopen)

    response = AuthIntrospectionClient().introspect(
        access_token="access-token",
        required_permission=RequiredPermission(domain="books", action="write"),
    )

    assert response.allowed is True
    assert captured_headers["authorization"] == "Bearer access-token"
    assert captured_headers["x-atlas-service"] == "core_api"
    assert captured_headers["x-atlas-service-key"] == "core-secret"
