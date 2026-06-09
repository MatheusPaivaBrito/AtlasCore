from __future__ import annotations

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import orjson

from core_api.infrastructure.settings import settings
from core_api.shared.auth.schemas import AuthIntrospectionResponse, RequiredPermission
from core_api.shared.exceptions import (
    CoreAuthenticationRequiredError,
    CoreAuthServiceUnavailableError,
    CoreAuthorizationDeniedError,
)

SERVICE_NAME_HEADER = "X-Atlas-Service"
SERVICE_KEY_HEADER = "X-Atlas-Service-Key"


class AuthIntrospectionClient:
    def introspect(
        self,
        *,
        access_token: str,
        required_permission: RequiredPermission,
    ) -> AuthIntrospectionResponse:
        payload = {
            "required_permission": required_permission.model_dump(),
        }
        request = Request(
            self._introspection_url(),
            data=orjson.dumps(payload),
            headers={
                "Authorization": f"Bearer {access_token}",
                SERVICE_NAME_HEADER: settings.SERVICE_NAME,
                SERVICE_KEY_HEADER: settings.CORE_TO_AUTH_SERVICE_KEY,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=settings.AUTH_INTROSPECTION_TIMEOUT_SECONDS) as response:
                raw_content = response.read()
        except HTTPError as exc:
            if exc.code == 401:
                raise CoreAuthenticationRequiredError() from exc
            if exc.code == 403:
                if self._is_service_auth_failure(exc):
                    raise CoreAuthServiceUnavailableError() from exc
                raise CoreAuthorizationDeniedError(domain=required_permission.domain, action=required_permission.action) from exc
            raise CoreAuthServiceUnavailableError() from exc
        except URLError as exc:
            raise CoreAuthServiceUnavailableError() from exc

        data = orjson.loads(raw_content)
        return AuthIntrospectionResponse.model_validate(data)

    @staticmethod
    def _introspection_url() -> str:
        return f"{settings.AUTH_API_INTERNAL_URL.rstrip('/')}/{settings.AUTH_INTROSPECTION_PATH.lstrip('/')}"

    @staticmethod
    def _is_service_auth_failure(exc: HTTPError) -> bool:
        try:
            raw_content = exc.read()
            data = orjson.loads(raw_content)
        except Exception:
            return False

        error = data.get("error") if isinstance(data, dict) else None
        if not isinstance(error, dict):
            return False
        return error.get("code") == "auth.service_authentication_failed"


def get_auth_introspection_client() -> AuthIntrospectionClient:
    return AuthIntrospectionClient()
