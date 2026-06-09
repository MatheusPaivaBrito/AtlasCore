from uuid import UUID

from starlette import status

from shared_kernel.errors import ApplicationError, ErrorTarget


class AuthResourceNotFoundError(ApplicationError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "auth.resource_not_found"
    message = "Auth resource was not found."

    def __init__(self, *, entity: str, resource_id: UUID) -> None:
        super().__init__(
            message=f"{entity} was not found.",
            target=ErrorTarget(entity=entity, payload={"id": str(resource_id)}),
        )


class AuthResourceConflictError(ApplicationError):
    status_code = status.HTTP_409_CONFLICT
    code = "auth.resource_conflict"
    message = "Auth resource conflicts with an existing record."

    def __init__(self, *, entity: str, field: str = "email") -> None:
        super().__init__(
            message=f"{entity} already exists.",
            target=ErrorTarget(entity=entity, field=field),
        )


class AuthInvalidCredentialsError(ApplicationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "auth.invalid_credentials"
    message = "Invalid credentials."


class AuthWeakPasswordError(ApplicationError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "auth.weak_password"
    message = "Password does not match the required security policy."

    def __init__(self, *, missing_requirements: list[str]) -> None:
        super().__init__(
            target=ErrorTarget(
                entity="auth_password_policy",
                field="password",
                payload={"missing_requirements": missing_requirements},
            ),
        )


class AuthTooManyLoginAttemptsError(ApplicationError):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    code = "auth.too_many_login_attempts"
    message = "Too many failed login attempts. Try again later."


class AuthInactiveUserError(ApplicationError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "auth.inactive_user"
    message = "User is inactive."


class AuthMissingTokenError(ApplicationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "auth.missing_token"
    message = "Authentication token was not provided."


class AuthExpiredTokenError(ApplicationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "auth.expired_token"
    message = "Authentication token has expired."


class AuthInvalidTokenError(ApplicationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "auth.invalid_token"
    message = "Authentication token is invalid."


class AuthInvalidSessionError(ApplicationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "auth.invalid_session"
    message = "Authentication session is invalid or expired."


class AuthInvalidPasswordResetTokenError(ApplicationError):
    status_code = status.HTTP_400_BAD_REQUEST
    code = "auth.invalid_password_reset_token"
    message = "Password reset token is invalid or expired."


class AuthPermissionDeniedError(ApplicationError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "auth.permission_denied"
    message = "User does not have permission to perform this action."

    def __init__(self, *, domain: str, action: str) -> None:
        super().__init__(
            message=f"Missing permission: {domain}:{action}.",
            target=ErrorTarget(entity="auth_user_permissions", payload={"domain": domain, "action": action}),
        )


class AuthServiceAuthenticationError(ApplicationError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "auth.service_authentication_failed"
    message = "Calling service is not allowed to access this internal Auth route."

    def __init__(self, *, service_name: str | None = None) -> None:
        super().__init__(
            target=ErrorTarget(
                entity="internal_service",
                payload={"service_name": service_name or "unknown"},
            ),
        )
