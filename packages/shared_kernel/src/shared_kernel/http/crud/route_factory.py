from typing import Any, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel

from shared_kernel.http.crud.errors import CrudErrorFactory
from shared_kernel.http.crud.guards import CrudRouteGuards, resolve_guard
from shared_kernel.http.crud.handlers import CrudCommandHandler, CrudQueryHandler

ModelT = TypeVar("ModelT")

_RESERVED_QUERY_PARAMS = {"q", "limit", "offset", "include_deleted", "only_deleted"}


def create_crud_router(
    *,
    model: type[ModelT],
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    read_schema: type[BaseModel],
    session_dependency: Any,
    prefix: str,
    tags: list[str] | None = None,
    query_tag: str | None = None,
    command_tag: str | None = None,
    resource_label: str | None = None,
    guards: CrudRouteGuards | None = None,
    command_handler: type[CrudCommandHandler[Any]] | None = None,
    query_handler: type[CrudQueryHandler[Any]] | None = None,
    error_factory: CrudErrorFactory | None = None,
    search_fields: tuple[str, ...] = (),
    filter_fields: tuple[str, ...] = (),
) -> APIRouter:
    """Build CRUD routes by translating HTTP requests into CQRS commands and queries."""

    router = APIRouter(prefix=prefix)
    resource_name = getattr(model, "__tablename__", model.__name__)
    readable_name = resource_label or resource_name.replace("_", " ")
    fallback_tag = tags[0] if tags else readable_name
    query_tags = [query_tag or f"{fallback_tag}: query"]
    command_tags = [command_tag or f"{fallback_tag}: command"]
    route_guards = guards or CrudRouteGuards()

    generated_command_attrs: dict[str, Any] = {"model": model}
    generated_query_attrs: dict[str, Any] = {
        "model": model,
        "search_fields": search_fields,
        "filter_fields": filter_fields,
    }
    if error_factory is not None:
        generated_command_attrs["error_factory"] = error_factory
        generated_query_attrs["error_factory"] = error_factory

    command_handler_type = command_handler or type(
        "GeneratedCrudCommandHandler",
        (CrudCommandHandler,),
        generated_command_attrs,
    )
    query_handler_type = query_handler or type(
        "GeneratedCrudQueryHandler",
        (CrudQueryHandler,),
        generated_query_attrs,
    )
    active_filter_fields = filter_fields or tuple(getattr(query_handler_type, "filter_fields", ()))

    def _filters_from_request(request: Request) -> dict[str, str]:
        filters: dict[str, str] = {}
        for field_name in active_filter_fields:
            if field_name in _RESERVED_QUERY_PARAMS:
                continue
            raw_value = request.query_params.get(field_name)
            if raw_value is None or raw_value == "":
                continue
            filters[field_name] = raw_value
        return filters

    @router.post(
        "",
        response_model=read_schema,
        status_code=status.HTTP_201_CREATED,
        name=f"create_{resource_name}",
        tags=command_tags,
        summary=f"Create {readable_name}",
    )
    def create_resource(
        payload: create_schema,  # type: ignore[valid-type]
        authorized_user: Any = resolve_guard(route_guards.create),
        session: Any = Depends(session_dependency),
    ) -> Any:
        handler = command_handler_type(session)
        command = handler.create_command_type(payload=payload)
        return handler.create(command)

    @router.get(
        "",
        response_model=list[read_schema],
        name=f"list_{resource_name}",
        tags=query_tags,
        summary=f"List {readable_name}",
    )
    def list_resources(
        request: Request,
        q: str | None = None,
        include_deleted: bool = False,
        only_deleted: bool = False,
        limit: int = 50,
        offset: int = 0,
        authorized_user: Any = resolve_guard(route_guards.list),
        session: Any = Depends(session_dependency),
    ) -> Any:
        handler = query_handler_type(session)
        query = handler.list_query_type(
            q=q,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
            limit=limit,
            offset=offset,
            filters=_filters_from_request(request),
        )
        return handler.list(query)

    @router.get(
        "/{resource_id}",
        response_model=read_schema,
        name=f"get_{resource_name}",
        tags=query_tags,
        summary=f"Get {readable_name}",
    )
    def get_resource(
        resource_id: UUID,
        include_deleted: bool = False,
        authorized_user: Any = resolve_guard(route_guards.get),
        session: Any = Depends(session_dependency),
    ) -> Any:
        handler = query_handler_type(session)
        query = handler.get_query_type(resource_id=resource_id, include_deleted=include_deleted)
        return handler.get(query)

    @router.patch(
        "/{resource_id}",
        response_model=read_schema,
        name=f"update_{resource_name}",
        tags=command_tags,
        summary=f"Update {readable_name}",
    )
    def update_resource(
        resource_id: UUID,
        payload: update_schema,  # type: ignore[valid-type]
        authorized_user: Any = resolve_guard(route_guards.update),
        session: Any = Depends(session_dependency),
    ) -> Any:
        handler = command_handler_type(session)
        command = handler.update_command_type(resource_id=resource_id, payload=payload)
        return handler.update(command)

    @router.delete(
        "/{resource_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        name=f"delete_{resource_name}",
        tags=command_tags,
        summary=f"Delete {readable_name}",
    )
    def delete_resource(
        resource_id: UUID,
        authorized_user: Any = resolve_guard(route_guards.delete),
        session: Any = Depends(session_dependency),
    ) -> None:
        handler = command_handler_type(session)
        command = handler.delete_command_type(resource_id=resource_id)
        handler.delete(command)

    @router.post(
        "/{resource_id}/restore",
        response_model=read_schema,
        name=f"restore_{resource_name}",
        tags=command_tags,
        summary=f"Restore {readable_name}",
    )
    def restore_resource(
        resource_id: UUID,
        authorized_user: Any = resolve_guard(route_guards.restore),
        session: Any = Depends(session_dependency),
    ) -> Any:
        handler = command_handler_type(session)
        command = handler.restore_command_type(resource_id=resource_id)
        return handler.restore(command)

    return router
