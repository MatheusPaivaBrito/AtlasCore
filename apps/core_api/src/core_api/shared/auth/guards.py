from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core_api.shared.auth.client import AuthIntrospectionClient, get_auth_introspection_client
from core_api.shared.auth.schemas import AuthorizedUser, RequiredPermission
from core_api.shared.exceptions import CoreAuthenticationRequiredError, CoreAuthorizationDeniedError


ACCESS_TOKEN_COOKIE = "access_token"
bearer_scheme = HTTPBearer(auto_error=False)


class CoreAuthGuard:
    @staticmethod
    def extract_access_token(
        *,
        request: Request,
        credentials: HTTPAuthorizationCredentials | None,
    ) -> str | None:
        if credentials is not None:
            return credentials.credentials
        return request.cookies.get(ACCESS_TOKEN_COOKIE)

    def require_permission(self, *, domain: str, action: str):
        required_permission = RequiredPermission(domain=domain, action=action)

        def dependency(
            request: Request,
            credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
            client: AuthIntrospectionClient = Depends(get_auth_introspection_client),
        ) -> AuthorizedUser:
            token = self.extract_access_token(request=request, credentials=credentials)
            if not token:
                raise CoreAuthenticationRequiredError()

            introspection = client.introspect(
                access_token=token,
                required_permission=required_permission,
            )
            if not introspection.active or not introspection.allowed:
                raise CoreAuthorizationDeniedError(domain=domain, action=action)
            return introspection.user

        return Depends(dependency)


core_auth_guard = CoreAuthGuard()
