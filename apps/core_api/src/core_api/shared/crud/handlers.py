from collections.abc import Mapping
from typing import Any, ClassVar, Generic, TypeVar
from uuid import UUID

from sqlalchemy import String, cast, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core_api.shared.crud.commands import (
    CreateResourceCommand,
    DeleteResourceCommand,
    RestoreResourceCommand,
    UpdateResourceCommand,
)
from core_api.shared.crud.queries import GetResourceQuery, ListResourcesQuery
from core_api.shared.exceptions import (
    CoreInvalidFilterValueError,
    CoreResourceConflictError,
    CoreResourceNotFoundError,
    CoreUnsupportedFilterError,
)
from shared_kernel.time import DateTimeService

ModelT = TypeVar("ModelT")


class CrudHandlerBase(Generic[ModelT]):
    model: ClassVar[type[Any]]
    resource_name: ClassVar[str | None] = None

    def __init__(self, session: Session) -> None:
        self.session = session

    @property
    def entity_name(self) -> str:
        return self.resource_name or getattr(self.model, "__tablename__", self.model.__name__)

    @property
    def has_soft_delete(self) -> bool:
        return hasattr(self.model, "deleted_at")

    def _load(self, resource_id: UUID, *, include_deleted: bool = False) -> ModelT:
        instance = self.session.get(self.model, resource_id)
        if instance is None:
            raise CoreResourceNotFoundError(entity=self.entity_name, resource_id=resource_id)
        if self.has_soft_delete and not include_deleted and getattr(instance, "deleted_at") is not None:
            raise CoreResourceNotFoundError(entity=self.entity_name, resource_id=resource_id)
        return instance

    def _persist(self, instance: ModelT) -> ModelT:
        try:
            self.session.add(instance)
            self.session.flush()
            self.session.refresh(instance)
        except IntegrityError as exc:
            self.session.rollback()
            raise CoreResourceConflictError(entity=self.entity_name) from exc
        return instance

    def _column(self, field_name: str) -> Any:
        column = getattr(self.model, field_name, None)
        if column is None:
            raise CoreUnsupportedFilterError(entity=self.entity_name, field=field_name)
        return column


class CrudCommandHandler(CrudHandlerBase[ModelT]):
    create_command_type: ClassVar[type[CreateResourceCommand]] = CreateResourceCommand
    update_command_type: ClassVar[type[UpdateResourceCommand]] = UpdateResourceCommand
    delete_command_type: ClassVar[type[DeleteResourceCommand]] = DeleteResourceCommand
    restore_command_type: ClassVar[type[RestoreResourceCommand]] = RestoreResourceCommand

    def create(self, command: CreateResourceCommand) -> ModelT:
        instance = self.model(**command.payload.model_dump())
        return self._persist(instance)

    def update(self, command: UpdateResourceCommand) -> ModelT:
        instance = self._load(command.resource_id)
        for field, value in command.payload.model_dump(exclude_unset=True).items():
            setattr(instance, field, value)
        return self._persist(instance)

    def delete(self, command: DeleteResourceCommand) -> None:
        instance = self._load(command.resource_id)
        if self.has_soft_delete:
            soft_delete = getattr(instance, "soft_delete", None)
            if callable(soft_delete):
                soft_delete()
            else:
                setattr(instance, "deleted_at", DateTimeService.utc_now())
            self._persist(instance)
            return
        self.session.delete(instance)
        self.session.flush()

    def restore(self, command: RestoreResourceCommand) -> ModelT:
        instance = self._load(command.resource_id, include_deleted=True)
        if self.has_soft_delete:
            restore = getattr(instance, "restore", None)
            if callable(restore):
                restore()
            else:
                setattr(instance, "deleted_at", None)
        return self._persist(instance)


class CrudQueryHandler(CrudHandlerBase[ModelT]):
    list_query_type: ClassVar[type[ListResourcesQuery]] = ListResourcesQuery
    get_query_type: ClassVar[type[GetResourceQuery]] = GetResourceQuery
    search_fields: ClassVar[tuple[str, ...]] = ()
    filter_fields: ClassVar[tuple[str, ...]] = ()

    def list(self, query: ListResourcesQuery) -> list[ModelT]:
        limit = max(1, min(query.limit, 100))
        offset = max(0, query.offset)
        statement = select(self.model)
        statement = self._apply_soft_delete_scope(
            statement,
            include_deleted=query.include_deleted,
            only_deleted=query.only_deleted,
        )
        statement = self._apply_search(statement, query.q)
        statement = self._apply_exact_filters(statement, query.filters)
        statement = statement.offset(offset).limit(limit)
        return list(self.session.scalars(statement).all())

    def get(self, query: GetResourceQuery) -> ModelT:
        return self._load(query.resource_id, include_deleted=query.include_deleted)

    def _apply_soft_delete_scope(self, statement: Any, *, include_deleted: bool, only_deleted: bool) -> Any:
        if not self.has_soft_delete:
            return statement
        deleted_column = self._column("deleted_at")
        if only_deleted:
            return statement.where(deleted_column.is_not(None))
        if include_deleted:
            return statement
        return statement.where(deleted_column.is_(None))

    def _apply_search(self, statement: Any, q: str | None) -> Any:
        if not q or not self.search_fields:
            return statement
        like_value = f"%{q.strip()}%"
        if like_value == "%%":
            return statement
        conditions = [cast(self._column(field), String).ilike(like_value) for field in self.search_fields]
        return statement.where(or_(*conditions))

    def _apply_exact_filters(self, statement: Any, filters: Mapping[str, str]) -> Any:
        for field_name, raw_value in filters.items():
            if field_name not in self.filter_fields:
                raise CoreUnsupportedFilterError(entity=self.entity_name, field=field_name)
            statement = statement.where(self._column(field_name) == self._coerce_filter_value(field_name, raw_value))
        return statement

    def _coerce_filter_value(self, field_name: str, raw_value: str) -> Any:
        column = self._column(field_name)
        try:
            python_type = column.property.columns[0].type.python_type
        except (AttributeError, NotImplementedError):
            return raw_value

        if python_type is UUID:
            try:
                return UUID(raw_value)
            except ValueError as exc:
                raise CoreInvalidFilterValueError(
                    entity=self.entity_name,
                    field=field_name,
                    expected_type="UUID",
                    value=raw_value,
                ) from exc
        if python_type is int:
            try:
                return int(raw_value)
            except ValueError as exc:
                raise CoreInvalidFilterValueError(
                    entity=self.entity_name,
                    field=field_name,
                    expected_type="integer",
                    value=raw_value,
                ) from exc
        return raw_value
