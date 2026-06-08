from __future__ import annotations

from typing import Any, Protocol
from uuid import UUID

from starlette import status

from shared_kernel.errors import ApplicationError, ErrorTarget


class CrudResourceNotFoundError(ApplicationError):
    status_code = status.HTTP_404_NOT_FOUND
    code = "crud.resource_not_found"

    def __init__(self, *, entity: str, resource_id: UUID | None = None) -> None:
        payload = {"id": str(resource_id)} if resource_id else {}
        super().__init__(
            f"{entity} resource was not found.",
            target=ErrorTarget(location="path", entity=entity, field="resource_id", payload=payload),
        )


class CrudResourceConflictError(ApplicationError):
    status_code = status.HTTP_409_CONFLICT
    code = "crud.resource_conflict"

    def __init__(self, *, entity: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            f"{entity} resource conflicts with existing data.",
            target=ErrorTarget(location="body", entity=entity),
            details=details,
        )


class CrudUnsupportedFilterError(ApplicationError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "crud.unsupported_filter"

    def __init__(self, *, entity: str, field: str) -> None:
        super().__init__(
            f"Unsupported filter field: {field}.",
            target=ErrorTarget(location="query", entity=entity, field=field),
        )


class CrudInvalidFilterValueError(ApplicationError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "crud.invalid_filter_value"

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


class CrudErrorFactory(Protocol):
    def not_found(self, *, entity: str, resource_id: UUID | None = None) -> Exception:
        raise NotImplementedError

    def conflict(self, *, entity: str, details: dict[str, Any] | None = None) -> Exception:
        raise NotImplementedError

    def unsupported_filter(self, *, entity: str, field: str) -> Exception:
        raise NotImplementedError

    def invalid_filter_value(self, *, entity: str, field: str, expected_type: str, value: str) -> Exception:
        raise NotImplementedError


class DefaultCrudErrorFactory:
    def not_found(self, *, entity: str, resource_id: UUID | None = None) -> Exception:
        return CrudResourceNotFoundError(entity=entity, resource_id=resource_id)

    def conflict(self, *, entity: str, details: dict[str, Any] | None = None) -> Exception:
        return CrudResourceConflictError(entity=entity, details=details)

    def unsupported_filter(self, *, entity: str, field: str) -> Exception:
        return CrudUnsupportedFilterError(entity=entity, field=field)

    def invalid_filter_value(self, *, entity: str, field: str, expected_type: str, value: str) -> Exception:
        return CrudInvalidFilterValueError(
            entity=entity,
            field=field,
            expected_type=expected_type,
            value=value,
        )
