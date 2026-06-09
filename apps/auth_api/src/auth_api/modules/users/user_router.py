from uuid import UUID

from fastapi import APIRouter, Depends, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from auth_api.infrastructure.database.connection import get_session
from auth_api.modules.access_control.application.permissions import user_has_permission
from auth_api.modules.access_control.domain.permissions import USERS_DELETE, USERS_READ, USERS_WRITE
from auth_api.modules.auth.application.guards import auth_guard, bearer_scheme
from auth_api.modules.sessions.application.service import SessionService, get_session_service
from auth_api.modules.users.user_command_handlers import UserCommandHandler
from auth_api.modules.users.user_commands import CreateUserCommand, DeleteUserCommand, RestoreUserCommand, UpdateUserCommand
from auth_api.modules.users.user_entity import UserEntity
from auth_api.modules.users.user_queries import GetUserQuery, ListUsersQuery
from auth_api.modules.users.user_query_handlers import UserQueryHandler
from auth_api.modules.users.user_schema import UserCreate, UserRead, UserUpdate
from auth_api.shared.exceptions import AuthPermissionDeniedError

router = APIRouter(prefix="/users")


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
    if not user_has_permission(user, domain=USERS_WRITE.domain, action=USERS_WRITE.action):
        raise AuthPermissionDeniedError(domain=USERS_WRITE.domain, action=USERS_WRITE.action)
    return user


def _filters_from_request(request: Request) -> dict[str, str]:
    filters: dict[str, str] = {}
    for field_name in ("email", "is_active", "is_superuser"):
        value = request.query_params.get(field_name)
        if value is not None and value != "":
            filters[field_name] = value
    return filters


def _load_user(session: Session, user_id: UUID, *, include_deleted: bool = False) -> UserEntity:
    return UserQueryHandler(session).load_user(user_id=user_id, include_deleted=include_deleted)


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
    return UserCommandHandler(session).create(CreateUserCommand(payload=payload))


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
    current_user: UserEntity = auth_guard.require_permission(domain=USERS_READ.domain, action=USERS_READ.action),
    session: Session = Depends(get_session),
) -> list[UserEntity]:
    return UserQueryHandler(session).list(
        ListUsersQuery(
            q=q,
            include_deleted=include_deleted,
            only_deleted=only_deleted,
            limit=limit,
            offset=offset,
            filters=_filters_from_request(request),
        )
    )


@router.get(
    "/{user_id}",
    response_model=UserRead,
    tags=["users - query"],
    summary="Get user",
)
def get_user(
    user_id: UUID,
    include_deleted: bool = False,
    current_user: UserEntity = auth_guard.require_permission(domain=USERS_READ.domain, action=USERS_READ.action),
    session: Session = Depends(get_session),
) -> UserEntity:
    return UserQueryHandler(session).get(GetUserQuery(user_id=user_id, include_deleted=include_deleted))


@router.patch(
    "/{user_id}",
    response_model=UserRead,
    tags=["users - command"],
    summary="Update user",
)
def update_user(
    user_id: UUID,
    payload: UserUpdate,
    current_user: UserEntity = auth_guard.require_permission(domain=USERS_WRITE.domain, action=USERS_WRITE.action),
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> UserEntity:
    return UserCommandHandler(session, session_service).update(
        UpdateUserCommand(user_id=user_id, payload=payload),
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["users - command"],
    summary="Delete user",
)
def delete_user(
    user_id: UUID,
    current_user: UserEntity = auth_guard.require_permission(domain=USERS_DELETE.domain, action=USERS_DELETE.action),
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> None:
    UserCommandHandler(session, session_service).delete(DeleteUserCommand(user_id=user_id))


@router.post(
    "/{user_id}/restore",
    response_model=UserRead,
    tags=["users - command"],
    summary="Restore user",
)
def restore_user(
    user_id: UUID,
    current_user: UserEntity = auth_guard.require_permission(domain=USERS_WRITE.domain, action=USERS_WRITE.action),
    session: Session = Depends(get_session),
) -> UserEntity:
    return UserCommandHandler(session).restore(RestoreUserCommand(user_id=user_id))
