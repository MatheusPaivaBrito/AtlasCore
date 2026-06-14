from __future__ import annotations

from collections.abc import Iterator
import json
from pathlib import Path
from typing import Any
from uuid import UUID

from httpx import ASGITransport, AsyncClient
import pytest

from notification_api.infrastructure.settings import settings
from notification_api.main import app
from notification_api.shared.service_auth import NOTIFICATIONS_SEND_SCOPE
from shared_kernel.security import ServiceTokenManager


ROOT_DIR = Path(__file__).resolve().parents[2]


def load_contract_schema(contract_path: str, file_name: str) -> dict[str, Any]:
    with (ROOT_DIR / "contracts" / contract_path / file_name).open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


def service_auth_headers(subject: str) -> dict[str, str]:
    token = ServiceTokenManager(
        secret_key=settings.SERVICE_JWT_SECRET_KEY,
        issuer=settings.SERVICE_JWT_ISSUER,
        algorithm=settings.SERVICE_JWT_ALGORITHM,
        default_ttl_seconds=settings.SERVICE_JWT_TTL_SECONDS,
    ).create_token(
        subject=subject,
        audience=settings.SERVICE_NAME,
        scopes=(NOTIFICATIONS_SEND_SCOPE,),
    )
    return {"Authorization": f"Bearer {token}"}


def iter_refs(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            yield ref

        for nested_value in value.values():
            yield from iter_refs(nested_value)

    if isinstance(value, list):
        for item in value:
            yield from iter_refs(item)


def resolve_ref(ref: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    assert ref.startswith("#/$defs/")
    definition_name = ref.removeprefix("#/$defs/")
    return root_schema["$defs"][definition_name]


def validate_contract(instance: Any, schema: dict[str, Any], root_schema: dict[str, Any] | None = None) -> None:
    root = root_schema or schema

    if "$ref" in schema:
        validate_contract(instance, resolve_ref(schema["$ref"], root), root)
        return

    if "oneOf" in schema:
        valid_options = 0
        for option in schema["oneOf"]:
            try:
                validate_contract(instance, option, root)
            except AssertionError:
                continue
            valid_options += 1
        assert valid_options == 1
        return

    expected_type = schema.get("type")
    if expected_type == "object":
        assert isinstance(instance, dict)
        for required_field in schema.get("required", []):
            assert required_field in instance

        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            assert set(instance).issubset(set(properties))

        for field_name, field_schema in properties.items():
            if field_name in instance:
                validate_contract(instance[field_name], field_schema, root)
        return

    if expected_type == "string":
        assert isinstance(instance, str)
        assert len(instance) >= schema.get("minLength", 0)
        assert len(instance) <= schema.get("maxLength", len(instance))
        if schema.get("format") == "uuid":
            UUID(instance)
        if schema.get("format") == "email":
            assert "@" in instance
        return

    if expected_type == "boolean":
        assert isinstance(instance, bool)
        return

    if expected_type == "null":
        assert instance is None
        return


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("contract_path", "subject"),
    [
        ("auth-notification/email-delivery", "auth_api"),
        ("core-notification/email-delivery", "core_api"),
    ],
)
async def test_notification_email_delivery_contract(contract_path: str, subject: str) -> None:
    request_schema = load_contract_schema(contract_path, "request.v1.schema.json")
    response_schema = load_contract_schema(contract_path, "response.v1.schema.json")
    request_payload = {
        "to": "reader@example.com",
        "subject": "Book reservation confirmed",
        "body": "Your reservation is ready.",
        "metadata": {"contract": contract_path},
    }

    validate_contract(request_payload, request_schema)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/notifications/email",
            headers=service_auth_headers(subject),
            json=request_payload,
        )

    assert response.status_code == 200
    validate_contract(response.json(), response_schema)
    assert response.json()["accepted"] is True


@pytest.mark.asyncio
async def test_notification_slack_delivery_contract() -> None:
    contract_path = "core-notification/slack-delivery"
    request_schema = load_contract_schema(contract_path, "request.v1.schema.json")
    response_schema = load_contract_schema(contract_path, "response.v1.schema.json")
    request_payload = {
        "message": "Incident created",
        "channel": "#ops",
        "metadata": {"contract": contract_path},
    }

    validate_contract(request_payload, request_schema)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/notifications/slack",
            headers=service_auth_headers("core_api"),
            json=request_payload,
        )

    assert response.status_code == 200
    validate_contract(response.json(), response_schema)
    assert response.json()["accepted"] is True
