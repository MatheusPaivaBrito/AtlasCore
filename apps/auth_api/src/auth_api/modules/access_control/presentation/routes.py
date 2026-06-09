from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth_api.infrastructure.database.connection import get_session
from auth_api.modules.access_control.application.permissions import serialize_user_permissions, sync_user_permissions
from auth_api.modules.access_control.presentation.schemas import AccessProfileRead, PermissionSyncRequest
from auth_api.modules.auth.application.guards import auth_guard
from auth_api.modules.users.user_entity import UserEntity
from auth_api.modules.users.user_router import _load_user

router = APIRouter(prefix="/access-control")


@router.get(
    "/me",
    response_model=AccessProfileRead,
    tags=["access-control - query"],
    summary="Get current access profile",
)
def get_my_access_profile(current_user: UserEntity = auth_guard.require_user()) -> AccessProfileRead:
    return AccessProfileRead(
        user_id=current_user.id,
        is_superuser=current_user.is_superuser,
        permissions=serialize_user_permissions(current_user),
    )


@router.get(
    "/users/{user_id}/permissions",
    response_model=AccessProfileRead,
    tags=["access-control - query"],
    summary="Get user permissions",
)
def get_user_permissions(
    user_id: UUID,
    current_user: UserEntity = auth_guard.require_permission(domain="access_control", action="read"),
    session: Session = Depends(get_session),
) -> AccessProfileRead:
    user = _load_user(session, user_id)
    return AccessProfileRead(
        user_id=user.id,
        is_superuser=user.is_superuser,
        permissions=serialize_user_permissions(user),
    )


@router.put(
    "/users/{user_id}/permissions",
    response_model=AccessProfileRead,
    tags=["access-control - command"],
    summary="Replace user permissions",
)
def replace_user_permissions(
    user_id: UUID,
    payload: PermissionSyncRequest,
    current_user: UserEntity = auth_guard.require_permission(domain="access_control", action="write"),
    session: Session = Depends(get_session),
) -> AccessProfileRead:
    user = _load_user(session, user_id)
    sync_user_permissions(
        session,
        user_id=user.id,
        permissions=[permission.model_dump() for permission in payload.permissions],
    )
    user = _load_user(session, user_id)
    return AccessProfileRead(
        user_id=user.id,
        is_superuser=user.is_superuser,
        permissions=serialize_user_permissions(user),
    )
