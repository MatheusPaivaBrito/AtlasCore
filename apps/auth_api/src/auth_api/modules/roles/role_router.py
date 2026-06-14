from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from auth_api.infrastructure.database.connection import get_session
from auth_api.modules.access_control.application.permissions import serialize_user_roles, sync_role_permissions, sync_user_roles
from auth_api.modules.access_control.domain.permissions import (
    ACCESS_CONTROL_READ,
    ACCESS_CONTROL_WRITE,
    ROLES_DELETE,
    ROLES_READ,
    ROLES_WRITE,
)
from auth_api.modules.auth.application.guards import auth_guard
from auth_api.modules.roles.role_command_handlers import RoleCommandHandler
from auth_api.modules.roles.role_commands import CreateRoleCommand, DeleteRoleCommand, RestoreRoleCommand, UpdateRoleCommand
from auth_api.modules.roles.role_queries import GetRoleQuery, ListRolesQuery
from auth_api.modules.roles.role_query_handlers import RoleQueryHandler
from auth_api.modules.roles.role_schema import RoleCreate, RolePermissionSyncRequest, RoleRead, RoleSyncRequest, RoleUpdate
from auth_api.modules.users.user_entity import UserEntity
from auth_api.modules.users.user_router import _load_user
from auth_api.modules.users.user_schema import UserRoleRead

router = APIRouter(prefix="/roles")
user_roles_router = APIRouter(prefix="/access-control/users")


def _filters_from_request(request: Request) -> dict[str, str]:
    filters: dict[str, str] = {}
    for field_name in ("code", "is_active"):
        value = request.query_params.get(field_name)
        if value is not None and value != "":
            filters[field_name] = value
    return filters


@router.post(
    "",
    response_model=RoleRead,
    status_code=status.HTTP_201_CREATED,
    tags=["roles - command"],
    summary="Create role",
)
def create_role(
    payload: RoleCreate,
    current_user: UserEntity = auth_guard.require_permission(
        domain=ROLES_WRITE.domain,
        action=ROLES_WRITE.action,
    ),
    session: Session = Depends(get_session),
) -> RoleRead:
    return RoleCommandHandler(session).create(CreateRoleCommand(payload=payload))


@router.get(
    "",
    response_model=list[RoleRead],
    tags=["roles - query"],
    summary="List roles",
)
def list_roles(
    request: Request,
    q: str | None = None,
    include_deleted: bool = False,
    only_deleted: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: UserEntity = auth_guard.require_permission(
        domain=ROLES_READ.domain,
        action=ROLES_READ.action,
    ),
    session: Session = Depends(get_session),
) -> list[RoleRead]:
    return RoleQueryHandler(session).list(
        ListRolesQuery(
            q=q,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
            limit=limit,
            offset=offset,
            filters=_filters_from_request(request),
        )
    )


@router.get(
    "/{role_id}",
    response_model=RoleRead,
    tags=["roles - query"],
    summary="Get role",
)
def get_role(
    role_id: UUID,
    include_deleted: bool = False,
    current_user: UserEntity = auth_guard.require_permission(
        domain=ROLES_READ.domain,
        action=ROLES_READ.action,
    ),
    session: Session = Depends(get_session),
) -> RoleRead:
    return RoleQueryHandler(session).get(GetRoleQuery(role_id=role_id, include_deleted=include_deleted))


@router.patch(
    "/{role_id}",
    response_model=RoleRead,
    tags=["roles - command"],
    summary="Update role",
)
def update_role(
    role_id: UUID,
    payload: RoleUpdate,
    current_user: UserEntity = auth_guard.require_permission(
        domain=ROLES_WRITE.domain,
        action=ROLES_WRITE.action,
    ),
    session: Session = Depends(get_session),
) -> RoleRead:
    return RoleCommandHandler(session).update(UpdateRoleCommand(role_id=role_id, payload=payload))


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["roles - command"],
    summary="Delete role",
)
def delete_role(
    role_id: UUID,
    current_user: UserEntity = auth_guard.require_permission(
        domain=ROLES_DELETE.domain,
        action=ROLES_DELETE.action,
    ),
    session: Session = Depends(get_session),
) -> None:
    RoleCommandHandler(session).delete(DeleteRoleCommand(role_id=role_id))


@router.post(
    "/{role_id}/restore",
    response_model=RoleRead,
    tags=["roles - command"],
    summary="Restore role",
)
def restore_role(
    role_id: UUID,
    current_user: UserEntity = auth_guard.require_permission(
        domain=ROLES_WRITE.domain,
        action=ROLES_WRITE.action,
    ),
    session: Session = Depends(get_session),
) -> RoleRead:
    return RoleCommandHandler(session).restore(RestoreRoleCommand(role_id=role_id))


@router.put(
    "/{role_id}/permissions",
    response_model=RoleRead,
    tags=["roles - command"],
    summary="Replace role permissions",
)
def replace_role_permissions(
    role_id: UUID,
    payload: RolePermissionSyncRequest,
    current_user: UserEntity = auth_guard.require_permission(
        domain=ROLES_WRITE.domain,
        action=ROLES_WRITE.action,
    ),
    session: Session = Depends(get_session),
) -> RoleRead:
    role = RoleQueryHandler(session).load_role(role_id=role_id)
    sync_role_permissions(
        session,
        role_id=role.id,
        permissions=[permission.model_dump() for permission in payload.permissions],
    )
    return RoleQueryHandler(session).load_role(role_id=role_id)


@user_roles_router.get(
    "/{user_id}/roles",
    response_model=list[UserRoleRead],
    tags=["access-control - query"],
    summary="Get user roles",
)
def get_user_roles(
    user_id: UUID,
    current_user: UserEntity = auth_guard.require_permission(
        domain=ACCESS_CONTROL_READ.domain,
        action=ACCESS_CONTROL_READ.action,
    ),
    session: Session = Depends(get_session),
) -> list[dict]:
    user = _load_user(session, user_id)
    return serialize_user_roles(user)


@user_roles_router.put(
    "/{user_id}/roles",
    response_model=list[UserRoleRead],
    tags=["access-control - command"],
    summary="Replace user roles",
)
def replace_user_roles(
    user_id: UUID,
    payload: RoleSyncRequest,
    current_user: UserEntity = auth_guard.require_permission(
        domain=ACCESS_CONTROL_WRITE.domain,
        action=ACCESS_CONTROL_WRITE.action,
    ),
    session: Session = Depends(get_session),
) -> list[dict]:
    user = _load_user(session, user_id)
    sync_user_roles(session, user_id=user.id, role_ids=payload.role_ids)
    user = _load_user(session, user_id)
    return serialize_user_roles(user)
