from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from auth_api.infrastructure.database.connection import get_session
from auth_api.modules.access_control.application.permissions import serialize_user_permissions
from auth_api.modules.auth.application.cookies import REFRESH_TOKEN_COOKIE, clear_auth_cookies, set_auth_cookies
from auth_api.modules.auth.application.guards import auth_guard, bearer_scheme
from auth_api.modules.auth.application.passwords import verify_password
from auth_api.modules.auth.application.tokens import jwt_service
from auth_api.modules.auth.presentation.schemas import LoginRequest, LoginResponse, LogoutResponse, RefreshResponse
from auth_api.modules.sessions.application.service import SessionService, get_session_service
from auth_api.modules.users.domain.user_entity import UserEntity
from auth_api.shared.exceptions import (
    AuthExpiredTokenError,
    AuthInactiveUserError,
    AuthInvalidCredentialsError,
    AuthInvalidSessionError,
    AuthInvalidTokenError,
)
from shared_kernel.time import DateTimeService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, summary="Login with email and password")
def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> LoginResponse:
    user = session.scalar(
        select(UserEntity)
        .options(selectinload(UserEntity.credential), selectinload(UserEntity.permissions))
        .where(UserEntity.email == payload.email)
        .limit(1)
    )

    if user is None or user.deleted_at is not None or user.credential is None:
        raise AuthInvalidCredentialsError()

    if not verify_password(payload.password, user.credential.password_hash):
        raise AuthInvalidCredentialsError()

    if not user.is_active:
        raise AuthInactiveUserError()

    user_agent = request.headers.get("user-agent")
    ip = request.client.host if request.client else None
    session_id = session_service.generate_device_id(user_id=user.id, user_agent=user_agent, ip=ip)
    access_token = jwt_service.create_access_token(user=user, session_id=session_id)
    refresh_token = jwt_service.create_refresh_token(user=user, session_id=session_id)

    session_service.register_session(
        user=user,
        session_id=session_id,
        refresh_token=refresh_token,
        user_agent=user_agent,
        ip=ip,
    )
    user.last_login_at = DateTimeService.utc_now()
    user.last_login_ip = ip
    user.last_login_user_agent = user_agent
    session.flush()
    session.refresh(user)

    set_auth_cookies(response=response, access_token=access_token, refresh_token=refresh_token)

    return LoginResponse(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
        session_id=session_id,
        permissions=serialize_user_permissions(user),
    )


@router.post("/refresh", response_model=RefreshResponse, summary="Refresh access and refresh tokens")
def refresh(
    request: Request,
    response: Response,
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> RefreshResponse:
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE)
    if not refresh_token:
        clear_auth_cookies(response=response)
        raise AuthInvalidSessionError()

    try:
        payload = jwt_service.verify_refresh_token(refresh_token)
    except (AuthExpiredTokenError, AuthInvalidTokenError):
        clear_auth_cookies(response=response)
        raise

    user_id = UUID(str(payload["sub"]))
    session_id = str(payload.get("session_id") or "")
    if not session_id:
        clear_auth_cookies(response=response)
        raise AuthInvalidSessionError()

    auth_session = session_service.get_session(user_id=user_id, session_id=session_id)
    if auth_session is None or auth_session.get("refresh_token") != refresh_token:
        clear_auth_cookies(response=response)
        raise AuthInvalidSessionError()

    user = session.scalar(
        select(UserEntity)
        .options(selectinload(UserEntity.permissions))
        .where(UserEntity.id == user_id)
        .limit(1)
    )
    if user is None or user.deleted_at is not None:
        clear_auth_cookies(response=response)
        raise AuthInvalidSessionError()
    if not user.is_active:
        clear_auth_cookies(response=response)
        raise AuthInactiveUserError()
    if int(payload.get("token_version") or 0) != user.token_version:
        clear_auth_cookies(response=response)
        raise AuthInvalidSessionError()
    if int(auth_session.get("token_version") or 0) != user.token_version:
        clear_auth_cookies(response=response)
        raise AuthInvalidSessionError()

    access_token = jwt_service.create_access_token(user=user, session_id=session_id)
    new_refresh_token = jwt_service.create_refresh_token(user=user, session_id=session_id)
    session_service.register_session(
        user=user,
        session_id=session_id,
        refresh_token=new_refresh_token,
        user_agent=auth_session.get("user_agent"),
        ip=auth_session.get("ip"),
    )
    set_auth_cookies(response=response, access_token=access_token, refresh_token=new_refresh_token)

    return RefreshResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        session_id=session_id,
    )


@router.post("/logout", response_model=LogoutResponse, summary="Logout current session")
def logout(
    request: Request,
    response: Response,
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    session_service: SessionService = Depends(get_session_service),
) -> LogoutResponse:
    token = auth_guard.extract_access_token(request=request, credentials=credentials)
    if token:
        try:
            payload = jwt_service.verify_access_token(token)
            user_id = UUID(str(payload["sub"]))
            session_id = str(payload.get("session_id") or "")
            if session_id:
                session_service.delete_session(user_id=user_id, session_id=session_id)
        except Exception:
            pass

    clear_auth_cookies(response=response)
    return LogoutResponse()


@router.post("/logout-all", response_model=LogoutResponse, summary="Logout every active session")
def logout_all(
    response: Response,
    current_user: UserEntity = auth_guard.require_user(),
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> LogoutResponse:
    current_user.token_version += 1
    session.flush()
    session_service.delete_all_sessions(user_id=current_user.id)
    clear_auth_cookies(response=response)
    return LogoutResponse()
