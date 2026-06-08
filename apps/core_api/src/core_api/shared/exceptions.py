from typing import Any
from uuid import UUID

from starlette import status

from shared_kernel.errors import ApplicationError, ErrorTarget


class CoreApiError(ApplicationError):
    code = "core_api.error"
    message = "A Core API error occurred."


class CoreResourceNotFoundError(CoreApiError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "core_api.resource_not_found"

    def __init__(self, *, entity: str, resource_id: UUID | None = None) -> None:
        payload = {"id": str(resource_id)} if resource_id else {}
        super().__init__(
            f"{entity} resource was not found.",
            target=ErrorTarget(
                location="path",
                entity=entity,
                field="resource_id",
                payload=payload,
            ),
        )


class CoreResourceConflictError(CoreApiError):
    status_code = status.HTTP_409_CONFLICT
    code = "core_api.resource_conflict"

    def __init__(self, *, entity: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            f"{entity} resource conflicts with existing data.",
            target=ErrorTarget(location="body", entity=entity),
            details=details,
        )


class CoreUnsupportedFilterError(CoreApiError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "core_api.unsupported_filter"

    def __init__(self, *, entity: str, field: str) -> None:
        super().__init__(
            f"Unsupported filter field: {field}.",
            target=ErrorTarget(location="query", entity=entity, field=field),
        )


class CoreInvalidFilterValueError(CoreApiError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "core_api.invalid_filter_value"

    def __init__(self, *, entity: str, field: str, expected_type: str, value: str) -> None:
        super().__init__(
            f"Invalid {expected_type} for filter field: {field}.",
            target=ErrorTarget(
                location="query",
                entity=entity,
                field=field,
                payload={"value": value, "expected_type": expected_type},
            ),
        )


class CoreAuthenticationRequiredError(CoreApiError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "core_api.authentication_required"
    message = "Authentication is required for this Core API route."


class CoreAuthorizationDeniedError(CoreApiError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "core_api.authorization_denied"
    message = "The authenticated user is not allowed to perform this Core API action."

    def __init__(self, *, domain: str, action: str) -> None:
        super().__init__(
            f"Missing permission: {domain}:{action}.",
            target=ErrorTarget(
                entity="auth_user_permissions",
                payload={"domain": domain, "action": action},
            ),
        )


class CoreAuthServiceUnavailableError(CoreApiError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    code = "core_api.auth_service_unavailable"
    message = "Auth API is unavailable for Core API authorization."
