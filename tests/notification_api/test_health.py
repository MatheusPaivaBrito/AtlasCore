from httpx import ASGITransport, AsyncClient
import pytest

from notification_api.infrastructure.settings import settings
from notification_api.main import app
from notification_api.shared.service_auth import NOTIFICATIONS_SEND_SCOPE
from shared_kernel.security import ServiceTokenManager


def service_auth_headers(
    *,
    subject: str = "core_api",
    audience: str | None = None,
    scopes: tuple[str, ...] = (NOTIFICATIONS_SEND_SCOPE,),
) -> dict[str, str]:
    token = ServiceTokenManager(
        secret_key=settings.SERVICE_JWT_SECRET_KEY,
        issuer=settings.SERVICE_JWT_ISSUER,
        algorithm=settings.SERVICE_JWT_ALGORITHM,
        default_ttl_seconds=settings.SERVICE_JWT_TTL_SECONDS,
    ).create_token(
        subject=subject,
        audience=audience or settings.SERVICE_NAME,
        scopes=scopes,
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_notification_api_health() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_notification_api_home_uses_shared_template() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "AtlasCore Notification API" in response.text
    assert "Open Swagger Docs" in response.text


@pytest.mark.asyncio
async def test_notification_api_docs_use_shared_theme() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        swagger = await client.get("/docs")
        redoc = await client.get("/redoc")

    assert swagger.status_code == 200
    assert "AtlasCore Notification API - Swagger" in swagger.text
    assert "SwaggerUIBundle" in swagger.text
    assert redoc.status_code == 200
    assert "AtlasCore Notification API - ReDoc" in redoc.text
    assert "Redoc.init" in redoc.text


@pytest.mark.asyncio
async def test_notification_api_static_contracts() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        channels = await client.get("/channels")
        templates = await client.get("/templates/examples")
        attempts = await client.get("/delivery-attempts/examples")

    assert channels.status_code == 200
    assert {channel["channel"] for channel in channels.json()["channels"]} == {"email", "slack"}
    assert templates.status_code == 200
    assert templates.json()["templates"]
    assert attempts.status_code == 200
    assert attempts.json()["states"]


@pytest.mark.asyncio
async def test_notification_api_rejects_email_without_service_token() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/notifications/email",
            json={
                "to": "reader@example.com",
                "subject": "Book reservation confirmed",
                "body": "Your reservation is ready.",
            },
        )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "service_auth.missing_token"


@pytest.mark.asyncio
async def test_notification_api_accepts_email_with_service_token() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/notifications/email",
            headers=service_auth_headers(subject="auth_api"),
            json={
                "to": "reader@example.com",
                "subject": "Book reservation confirmed",
                "body": "Your reservation is ready.",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["channel"] == "email"
    assert payload["provider"] == "local_ack"
    assert payload["provider_status"] == "not_configured"


@pytest.mark.asyncio
async def test_notification_api_rejects_slack_with_missing_scope() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/notifications/slack",
            headers=service_auth_headers(scopes=("notifications:read",)),
            json={
                "message": "Incident created",
                "channel": "#ops",
            },
        )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "service_auth.permission_denied"


@pytest.mark.asyncio
async def test_notification_api_accepts_slack_with_service_token() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/notifications/slack",
            headers=service_auth_headers(subject="core_api"),
            json={
                "message": "Incident created",
                "channel": "#ops",
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["accepted"] is True
    assert payload["channel"] == "slack"
    assert payload["provider"] == "local_ack"
    assert payload["target"] == "#ops"
