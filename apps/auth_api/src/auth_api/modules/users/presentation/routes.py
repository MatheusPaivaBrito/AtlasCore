from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from auth_api.infrastructure.database.connection import get_session
from auth_api.modules.access_control.application.permissions import sync_user_permissions
from auth_api.modules.auth.application.guards import auth_guard, bearer_scheme
from auth_api.modules.auth.application.passwords import hash_password
from auth_api.modules.sessions.application.service import SessionService, get_session_service
from auth_api.modules.users.domain.user_entity import UserCredentialEntity, UserEntity
from auth_api.modules.users.presentation.schemas import UserCreate, UserRead, UserUpdate
from auth_api.shared.exceptions import AuthPermissionDeniedError, AuthResourceConflictError, AuthResourceNotFoundError


router = APIRouter(prefix="/users")


def _load_user(session: Session, user_id: UUID, *, include_deleted: bool = False) -> UserEntity:
    user = session.scalar(
        select(UserEntity)
        .options(selectinload(UserEntity.credential), selectinload(UserEntity.permissions))
        .where(UserEntity.id == user_id)
        .limit(1)
    )
    if user is None:
        raise AuthResourceNotFoundError(entity="auth_users", resource_id=user_id)
    if not include_deleted and user.deleted_at is not None:
        raise AuthResourceNotFoundError(entity="auth_users", resource_id=user_id)
    return user


def _persist_user(session: Session, user: UserEntity) -> UserEntity:
    try:
        session.add(user)
        session.flush()
        session.refresh(user)
    except IntegrityError as exc:
        session.rollback()
        raise AuthResourceConflictError(entity="auth_users", field="email") from exc
    return user


def _permissions_payload(payload: UserCreate | UserUpdate) -> list[dict[str, str]] | None:
    permissions = getattr(payload, "permissions", None)
    if permissions is None:
        return None
    return [permission.model_dump() for permission in permissions]


def _require_user_write_or_bootstrap(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> UserEntity | None:
    user_count = session.scalar(select(func.count(UserEntity.id)))
    if not user_count:
        return None

    user = auth_guard.get_current_user(
        request=request,
        credentials=credentials,
        session=session,
        session_service=session_service,
    )
    if not user.is_superuser and not any(
        permission.deleted_at is None and permission.domain == "users" and permission.action == "write"
        for permission in (user.permissions or [])
    ):
        raise AuthPermissionDeniedError(domain="users", action="write")
    return user


def _apply_soft_delete_scope(
    statement: Any,
    *,
    include_deleted: bool,
    only_deleted: bool,
) -> Any:
    if only_deleted:
        return statement.where(UserEntity.deleted_at.is_not(None))
    if include_deleted:
        return statement
    return statement.where(UserEntity.deleted_at.is_(None))


def _apply_search(statement: Any, q: str | None) -> Any:
    if not q:
        return statement
    like_value = f"%{q.strip()}%"
    if like_value == "%%":
        return statement
    return statement.where(
        or_(
            cast(UserEntity.email, String).ilike(like_value),
            cast(UserEntity.full_name, String).ilike(like_value),
        ),
    )


def _apply_filters(statement: Any, request: Request) -> Any:
    email = request.query_params.get("email")
    is_active = request.query_params.get("is_active")
    is_superuser = request.query_params.get("is_superuser")

    if email:
        statement = statement.where(UserEntity.email == email.strip().lower())
    if is_active is not None:
        statement = statement.where(UserEntity.is_active == (is_active.lower() == "true"))
    if is_superuser is not None:
        statement = statement.where(UserEntity.is_superuser == (is_superuser.lower() == "true"))

    return statement


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    tags=["users - command"],
    summary="Create user",
)
def create_user(
    payload: UserCreate,
    current_user: UserEntity | None = Depends(_require_user_write_or_bootstrap),
    session: Session = Depends(get_session),
) -> UserEntity:
    user = UserEntity(
        email=payload.email,
        full_name=payload.full_name,
        is_active=payload.is_active,
        is_superuser=payload.is_superuser,
        token_version=1,
    )
    user.credential = UserCredentialEntity(password_hash=hash_password(payload.password))
    _persist_user(session, user)
    sync_user_permissions(session, user_id=user.id, permissions=_permissions_payload(payload) or [])
    return _load_user(session, user.id)


@router.get(
    "",
    response_model=list[UserRead],
    tags=["users - query"],
    summary="List users",
)
def list_users(
    request: Request,
    q: str | None = None,
    include_deleted: bool = False,
    only_deleted: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: UserEntity = auth_guard.require_permission(domain="users", action="read"),
    session: Session = Depends(get_session),
) -> list[UserEntity]:
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    statement = select(UserEntity).options(selectinload(UserEntity.permissions))
    statement = _apply_soft_delete_scope(statement, include_deleted=include_deleted, only_deleted=only_deleted)
    statement = _apply_search(statement, q)
    statement = _apply_filters(statement, request)
    statement = statement.order_by(UserEntity.email).offset(offset).limit(limit)
    return list(session.scalars(statement).all())


@router.get(
    "/{user_id}",
    response_model=UserRead,
    tags=["users - query"],
    summary="Get user",
)
def get_user(
    user_id: UUID,
    include_deleted: bool = False,
    current_user: UserEntity = auth_guard.require_permission(domain="users", action="read"),
    session: Session = Depends(get_session),
) -> UserEntity:
    return _load_user(session, user_id, include_deleted=include_deleted)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    tags=["users - command"],
    summary="Update user",
)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    current_user: UserEntity = auth_guard.require_permission(domain="users", action="write"),
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> UserEntity:
    user = _load_user(session, user_id)
    values = payload.model_dump(exclude_unset=True)
    password = values.pop("password", None)
    permissions = values.pop("permissions", None)

    for field_name, value in values.items():
        setattr(user, field_name, value)

    if password is not None:
        if user.credential is None:
            user.credential = UserCredentialEntity(password_hash=hash_password(password))
        else:
            user.credential.password_hash = hash_password(password)
        user.token_version += 1
        session_service.delete_all_sessions(user_id=user.id)

    _persist_user(session, user)
    if permissions is not None:
        sync_user_permissions(session, user_id=user.id, permissions=permissions)
    return _load_user(session, user.id)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["users - command"],
    summary="Delete user",
)
def delete_user(
    user_id: UUID,
    current_user: UserEntity = auth_guard.require_permission(domain="users", action="delete"),
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> None:
    user = _load_user(session, user_id)
    user.soft_delete()
    user.token_version += 1
    _persist_user(session, user)
    session_service.delete_all_sessions(user_id=user.id)


@router.post(
    "/{user_id}/restore",
    response_model=UserRead,
    tags=["users - command"],
    summary="Restore user",
)
def restore_user(
    user_id: UUID,
    current_user: UserEntity = auth_guard.require_permission(domain="users", action="write"),
    session: Session = Depends(get_session),
) -> UserEntity:
    user = _load_user(session, user_id, include_deleted=True)
    user.restore()
    return _persist_user(session, user)
