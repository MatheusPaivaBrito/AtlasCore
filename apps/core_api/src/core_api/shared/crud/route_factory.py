from datetime import UTC, datetime
from typing import Any, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import String, cast, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core_api.infrastructure.database.connection import get_session

ModelT = TypeVar("ModelT")

_RESERVED_QUERY_PARAMS = {"q", "limit", "offset", "include_deleted", "only_deleted"}


def create_crud_router(
    *,
    model: type[ModelT],
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    read_schema: type[BaseModel],
    prefix: str,
    tags: list[str],
    search_fields: tuple[str, ...] = (),
    filter_fields: tuple[str, ...] = (),
) -> APIRouter:
    """Build conventional CRUD, soft-delete and restore routes for simple Core modules."""

    router = APIRouter(prefix=prefix, tags=tags)
    resource_name = getattr(model, "__tablename__", model.__name__)
    has_soft_delete = hasattr(model, "deleted_at")

    def _not_found() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} resource was not found",
        )

    def _load(session: Session, resource_id: UUID, *, include_deleted: bool = False) -> ModelT:
        instance = session.get(model, resource_id)
        if instance is None:
            raise _not_found()
        if has_soft_delete and not include_deleted and getattr(instance, "deleted_at") is not None:
            raise _not_found()
        return instance

    def _persist(session: Session, instance: ModelT) -> ModelT:
        try:
            session.add(instance)
            session.flush()
            session.refresh(instance)
        except IntegrityError as exc:
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{resource_name} resource conflicts with existing data",
            ) from exc
        return instance

    def _column(field_name: str) -> Any:
        column = getattr(model, field_name, None)
        if column is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unsupported filter field: {field_name}",
            )
        return column

    def _coerce_filter_value(field_name: str, raw_value: str) -> Any:
        column = _column(field_name)
        try:
            python_type = column.property.columns[0].type.python_type
        except (AttributeError, NotImplementedError):
            return raw_value

        if python_type is UUID:
            try:
                return UUID(raw_value)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid UUID for filter field: {field_name}",
                ) from exc
        if python_type is int:
            try:
                return int(raw_value)
            except ValueError as exc:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid integer for filter field: {field_name}",
                ) from exc
        return raw_value

    def _apply_soft_delete_scope(statement: Any, *, include_deleted: bool, only_deleted: bool) -> Any:
        if not has_soft_delete:
            return statement
        deleted_column = _column("deleted_at")
        if only_deleted:
            return statement.where(deleted_column.is_not(None))
        if include_deleted:
            return statement
        return statement.where(deleted_column.is_(None))

    def _apply_search(statement: Any, q: str | None) -> Any:
        if not q or not search_fields:
            return statement
        like_value = f"%{q.strip()}%"
        if like_value == "%%":
            return statement
        conditions = [cast(_column(field), String).ilike(like_value) for field in search_fields]
        return statement.where(or_(*conditions))

    def _apply_exact_filters(statement: Any, request: Request) -> Any:
        for field_name in filter_fields:
            if field_name in _RESERVED_QUERY_PARAMS:
                continue
            raw_value = request.query_params.get(field_name)
            if raw_value is None or raw_value == "":
                continue
            statement = statement.where(_column(field_name) == _coerce_filter_value(field_name, raw_value))
        return statement

    @router.post(
        "",
        response_model=read_schema,
        status_code=status.HTTP_201_CREATED,
        name=f"create_{resource_name}",
    )
    def create_resource(payload: create_schema, session: Session = Depends(get_session)) -> Any:  # type: ignore[valid-type]
        instance = model(**payload.model_dump())
        return _persist(session, instance)

    @router.get("", response_model=list[read_schema], name=f"list_{resource_name}")
    def list_resources(
        request: Request,
        q: str | None = None,
        include_deleted: bool = False,
        only_deleted: bool = False,
        limit: int = 50,
        offset: int = 0,
        session: Session = Depends(get_session),
    ) -> Any:
        limit = max(1, min(limit, 100))
        offset = max(0, offset)
        statement = select(model)
        statement = _apply_soft_delete_scope(
            statement,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
        )
        statement = _apply_search(statement, q)
        statement = _apply_exact_filters(statement, request)
        statement = statement.offset(offset).limit(limit)
        return session.scalars(statement).all()

    @router.get("/{resource_id}", response_model=read_schema, name=f"get_{resource_name}")
    def get_resource(
        resource_id: UUID,
        include_deleted: bool = False,
        session: Session = Depends(get_session),
    ) -> Any:
        return _load(session, resource_id, include_deleted=include_deleted)

    @router.patch("/{resource_id}", response_model=read_schema, name=f"update_{resource_name}")
    def update_resource(
        resource_id: UUID,
        payload: update_schema,  # type: ignore[valid-type]
        session: Session = Depends(get_session),
    ) -> Any:
        instance = _load(session, resource_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(instance, field, value)
        return _persist(session, instance)

    @router.delete(
        "/{resource_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        name=f"delete_{resource_name}",
    )
    def delete_resource(resource_id: UUID, session: Session = Depends(get_session)) -> None:
        instance = _load(session, resource_id)
        if has_soft_delete:
            setattr(instance, "deleted_at", datetime.now(UTC))
            _persist(session, instance)
            return
        session.delete(instance)
        session.flush()

    @router.post(
        "/{resource_id}/restore",
        response_model=read_schema,
        name=f"restore_{resource_name}",
    )
    def restore_resource(resource_id: UUID, session: Session = Depends(get_session)) -> Any:
        instance = _load(session, resource_id, include_deleted=True)
        if has_soft_delete:
            setattr(instance, "deleted_at", None)
        return _persist(session, instance)

    return router
