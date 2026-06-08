from typing import Any, TypeVar

from fastapi import APIRouter
from pydantic import BaseModel

from core_api.infrastructure.database.connection import get_session
from core_api.shared.auth import core_auth_guard
from core_api.shared.crud.handlers import CrudCommandHandler, CrudQueryHandler, core_crud_error_factory
from shared_kernel.http.crud import CrudRouteGuards
from shared_kernel.http.crud.route_factory import create_crud_router as create_shared_crud_router

ModelT = TypeVar("ModelT")


def create_crud_router(
    *,
    model: type[ModelT],
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    read_schema: type[BaseModel],
    prefix: str,
    tags: list[str] | None = None,
    query_tag: str | None = None,
    command_tag: str | None = None,
    resource_label: str | None = None,
    permission_domain: str | None = None,
    command_handler: type[CrudCommandHandler[Any]] | None = None,
    query_handler: type[CrudQueryHandler[Any]] | None = None,
    search_fields: tuple[str, ...] = (),
    filter_fields: tuple[str, ...] = (),
) -> APIRouter:
    authorization_domain = permission_domain or prefix.strip("/")
    require_write = core_auth_guard.require_permission(domain=authorization_domain, action="write")
    require_delete = core_auth_guard.require_permission(domain=authorization_domain, action="delete")

    return create_shared_crud_router(
        model=model,
        create_schema=create_schema,
        update_schema=update_schema,
        read_schema=read_schema,
        session_dependency=get_session,
        prefix=prefix,
        tags=tags,
        query_tag=query_tag,
        command_tag=command_tag,
        resource_label=resource_label,
        guards=CrudRouteGuards(
            create=require_write,
            update=require_write,
            delete=require_delete,
            restore=require_write,
        ),
        command_handler=command_handler,
        query_handler=query_handler,
        error_factory=core_crud_error_factory,
        search_fields=search_fields,
        filter_fields=filter_fields,
    )
