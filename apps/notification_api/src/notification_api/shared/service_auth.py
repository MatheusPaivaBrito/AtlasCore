from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from notification_api.infrastructure.settings import settings
from shared_kernel.security import ServiceToken, ServiceTokenManager, ServiceTokenMissingError


NOTIFICATIONS_SEND_SCOPE = "notifications:send"

bearer_scheme = HTTPBearer(auto_error=False)


def _service_token_manager() -> ServiceTokenManager:
    return ServiceTokenManager(
        secret_key=settings.SERVICE_JWT_SECRET_KEY,
        issuer=settings.SERVICE_JWT_ISSUER,
        algorithm=settings.SERVICE_JWT_ALGORITHM,
        default_ttl_seconds=settings.SERVICE_JWT_TTL_SECONDS,
    )


def require_service_scope(required_scope: str):
    def dependency(
        request: Request,
        credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    ) -> ServiceToken:
        if credentials is None or credentials.scheme.lower() != "bearer":
            raise ServiceTokenMissingError()

        service_token = _service_token_manager().verify_token(
            token=credentials.credentials,
            audience=settings.SERVICE_NAME,
            required_scopes=(required_scope,),
            allowed_subjects=settings.SERVICE_JWT_ALLOWED_CALLERS,
        )
        request.state.service_token = service_token
        return service_token

    return Depends(dependency)


require_notification_sender = require_service_scope(NOTIFICATIONS_SEND_SCOPE)
