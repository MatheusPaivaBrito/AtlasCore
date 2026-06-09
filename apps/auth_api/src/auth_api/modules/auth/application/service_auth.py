from __future__ import annotations

from dataclasses import dataclass
from secrets import compare_digest

from fastapi import Depends, Request

from auth_api.infrastructure.settings import settings
from auth_api.shared.exceptions import AuthServiceAuthenticationError

SERVICE_NAME_HEADER = "X-Atlas-Service"
SERVICE_KEY_HEADER = "X-Atlas-Service-Key"


@dataclass(frozen=True, slots=True)
class InternalService:
    name: str


class InternalServiceGuard:
    def require_service(self):
        def dependency(request: Request) -> InternalService:
            service_name = request.headers.get(SERVICE_NAME_HEADER)
            service_key = request.headers.get(SERVICE_KEY_HEADER)

            if not service_name or not service_key:
                raise AuthServiceAuthenticationError(service_name=service_name)

            expected_key = settings.INTERNAL_SERVICE_KEYS.get(service_name)
            if expected_key is None or not compare_digest(expected_key, service_key):
                raise AuthServiceAuthenticationError(service_name=service_name)

            request.state.internal_service = service_name
            return InternalService(name=service_name)

        return Depends(dependency)


internal_service_guard = InternalServiceGuard()
