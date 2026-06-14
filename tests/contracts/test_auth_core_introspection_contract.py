from __future__ import annotations

from collections.abc import Generator
import json
from pathlib import Path
from typing import Any
from uuid import UUID

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

ROOT_DIR = Path(__file__).resolve().parents[2]
CONTRACT_DIR = ROOT_DIR / "contracts" / "auth-core" / "introspection"
SERVICE_HEADERS = {
    "X-Atlas-Service": "core_api",
    "X-Atlas-Service-Key": "atlas-core-to-auth-dev-key",
}


@pytest.fixture
def auth_contract_database() -> Generator[None, None, None]:
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


def load_contract_schema(file_name: str) -> dict[str, Any]:
    with (CONTRACT_DIR / file_name).open(encoding="utf-8") as schema_file:
        return json.load(schema_file)


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

    if expected_type == "array":
        assert isinstance(instance, list)
        for item in instance:
            validate_contract(item, schema["items"], root)
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

    if expected_type == "integer":
        assert isinstance(instance, int)
        assert not isinstance(instance, bool)
        assert instance >= schema.get("minimum", instance)
        return

    if expected_type == "null":
        assert instance is None
        return


def resolve_ref(ref: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    assert ref.startswith("#/$defs/")
    definition_name = ref.removeprefix("#/$defs/")
    return root_schema["$defs"][definition_name]


@pytest.mark.asyncio
async def test_auth_core_introspection_contract(auth_contract_database: None) -> None:
    request_schema = load_contract_schema("request.v1.schema.json")
    response_schema = load_contract_schema("response.v1.schema.json")
    request_payload = {
        "required_permission": {
            "domain": "books",
            "action": "write",
        },
    }

    validate_contract(request_payload, request_schema)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        create_response = await client.post(
            "/users",
            json={
                "email": "admin@atlas.local",
                "full_name": "Atlas Admin",
                "password": "AtlasAdmin123!",
                "is_active": True,
                "is_superuser": True,
            },
        )
        assert create_response.status_code == 201

        login_response = await client.post(
            "/auth/login",
            json={"email": "admin@atlas.local", "password": "AtlasAdmin123!"},
        )
        assert login_response.status_code == 200

        response = await client.post(
            "/internal/auth/introspect",
            headers={
                "Authorization": f"Bearer {login_response.json()['access_token']}",
                **SERVICE_HEADERS,
            },
            json=request_payload,
        )

    assert response.status_code == 200
    validate_contract(response.json(), response_schema)
    assert response.json()["active"] is True
    assert response.json()["allowed"] is True
