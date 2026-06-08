from fastapi import APIRouter, Depends, Response, status

from auth_api.modules.auth.application.cookies import clear_auth_cookies
from auth_api.modules.auth.application.guards import auth_guard
from auth_api.modules.sessions.application.service import SessionService, get_session_service
from auth_api.modules.sessions.presentation.schemas import SessionRead
from auth_api.modules.users.domain.user_entity import UserEntity

router = APIRouter(prefix="/sessions")


@router.get(
    "/me",
    response_model=list[SessionRead],
    tags=["sessions - query"],
    summary="List current user sessions",
)
def list_my_sessions(
    current_user: UserEntity = auth_guard.require_user(),
    session_service: SessionService = Depends(get_session_service),
) -> list[dict]:
    return session_service.list_sessions(user_id=current_user.id)


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["sessions - command"],
    summary="Revoke one current user session",
)
def revoke_session(
    session_id: str,
    current_user: UserEntity = auth_guard.require_user(),
    session_service: SessionService = Depends(get_session_service),
) -> None:
    session_service.delete_session(user_id=current_user.id, session_id=session_id)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["sessions - command"],
    summary="Revoke every current user session",
)
def revoke_all_sessions(
    response: Response,
    current_user: UserEntity = auth_guard.require_user(),
    session_service: SessionService = Depends(get_session_service),
) -> None:
    session_service.delete_all_sessions(user_id=current_user.id)
    clear_auth_cookies(response=response)
