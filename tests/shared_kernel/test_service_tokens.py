import pytest

from shared_kernel.security import (
    ServiceTokenInvalidAudienceError,
    ServiceTokenManager,
    ServiceTokenPermissionDeniedError,
)

TEST_SERVICE_SECRET = "atlas-service-token-test-secret-32-bytes"


def test_service_token_manager_creates_and_validates_service_jwt() -> None:
    manager = ServiceTokenManager(
        secret_key=TEST_SERVICE_SECRET,
        issuer="atlascore",
        default_ttl_seconds=300,
    )
    token = manager.create_token(
        subject="core_api",
        audience="notification_api",
        scopes=("notifications:send",),
    )

    payload = manager.verify_token(
        token=token,
        audience="notification_api",
        required_scopes=("notifications:send",),
        allowed_subjects=("core_api",),
    )

    assert payload.subject == "core_api"
    assert payload.audience == "notification_api"
    assert payload.scopes == ("notifications:send",)


def test_service_token_manager_rejects_wrong_audience() -> None:
    manager = ServiceTokenManager(secret_key=TEST_SERVICE_SECRET)
    token = manager.create_token(
        subject="core_api",
        audience="notification_api",
        scopes=("notifications:send",),
    )

    with pytest.raises(ServiceTokenInvalidAudienceError):
        manager.verify_token(token=token, audience="auth_api")


def test_service_token_manager_rejects_missing_scope() -> None:
    manager = ServiceTokenManager(secret_key=TEST_SERVICE_SECRET)
    token = manager.create_token(
        subject="core_api",
        audience="notification_api",
        scopes=("notifications:read",),
    )

    with pytest.raises(ServiceTokenPermissionDeniedError):
        manager.verify_token(
            token=token,
            audience="notification_api",
            required_scopes=("notifications:send",),
        )
