from typing import Any, TypeVar
from uuid import UUID

from core_api.shared.exceptions import (
    CoreInvalidFilterValueError,
    CoreResourceConflictError,
    CoreResourceNotFoundError,
    CoreUnsupportedFilterError,
)
from shared_kernel.http.crud.handlers import (
    CrudCommandHandler as SharedCrudCommandHandler,
    CrudHandlerBase as SharedCrudHandlerBase,
    CrudQueryHandler as SharedCrudQueryHandler,
)

ModelT = TypeVar("ModelT")


class CoreCrudErrorFactory:
    def not_found(self, *, entity: str, resource_id: UUID | None = None) -> Exception:
        return CoreResourceNotFoundError(entity=entity, resource_id=resource_id)

    def conflict(self, *, entity: str, details: dict[str, Any] | None = None) -> Exception:
        return CoreResourceConflictError(entity=entity, details=details)

    def unsupported_filter(self, *, entity: str, field: str) -> Exception:
        return CoreUnsupportedFilterError(entity=entity, field=field)

    def invalid_filter_value(self, *, entity: str, field: str, expected_type: str, value: str) -> Exception:
        return CoreInvalidFilterValueError(
            entity=entity,
            field=field,
            expected_type=expected_type,
            value=value,
        )


core_crud_error_factory = CoreCrudErrorFactory()


class CrudHandlerBase(SharedCrudHandlerBase[ModelT]):
    error_factory = core_crud_error_factory


class CrudCommandHandler(SharedCrudCommandHandler[ModelT]):
    error_factory = core_crud_error_factory


class CrudQueryHandler(SharedCrudQueryHandler[ModelT]):
    error_factory = core_crud_error_factory


__all__ = [
    "CoreCrudErrorFactory",
    "CrudCommandHandler",
    "CrudHandlerBase",
    "CrudQueryHandler",
    "core_crud_error_factory",
]
