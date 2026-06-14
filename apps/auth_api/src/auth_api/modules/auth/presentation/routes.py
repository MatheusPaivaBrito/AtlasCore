from uuid import UUID

from fastapi import APIRouter, Depends, Request, Response, Security
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from auth_api.infrastructure.database.connection import get_session
from auth_api.infrastructure.settings import settings
from auth_api.modules.access_control.application.permissions import serialize_user_permissions, user_has_permission
from auth_api.modules.auth.application.cookies import REFRESH_TOKEN_COOKIE, clear_auth_cookies, set_auth_cookies
from auth_api.modules.auth.application.guards import auth_guard, bearer_scheme
from auth_api.modules.auth.application.login_attempts import LoginAttemptService
from auth_api.modules.auth.application.password_policy import password_policy
from auth_api.modules.auth.application.password_recovery import PasswordRecoveryService
from auth_api.modules.auth.application.passwords import hash_password, verify_password
from auth_api.modules.auth.application.service_auth import InternalService, internal_service_guard
from auth_api.modules.auth.application.tokens import jwt_service
from auth_api.modules.auth.presentation.schemas import (
    IntrospectionRequest,
    IntrospectionResponse,
    IntrospectionUser,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    PasswordPolicyResponse,
    PasswordRecoveryRequest,
    PasswordRecoveryResponse,
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse,
    RefreshResponse,
)
from auth_api.modules.sessions.application.service import SessionService, get_session_service
from auth_api.modules.users.user_entity import UserEntity
from auth_api.shared.exceptions import (
    AuthExpiredTokenError,
    AuthInactiveUserError,
    AuthInvalidCredentialsError,
    AuthInvalidPasswordResetTokenError,
    AuthInvalidSessionError,
    AuthInvalidTokenError,
)
from shared_kernel.time import DateTimeService

router = APIRouter(prefix="/auth", tags=["auth"])
internal_router = APIRouter(prefix="/internal/auth", tags=["internal-auth"])


def _set_user_password(user: UserEntity, new_password: str) -> None:
    password_policy.validate(new_password)
    user.credential.password_hash = hash_password(new_password)
    user.credential.password_updated_at = DateTimeService.utc_now()
    user.token_version += 1


@router.post("/login", response_model=LoginResponse, summary="Login with email and password")
def login(
    payload: LoginRequest,
    response: Response,
    request: Request,
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> LoginResponse:
    user_agent = request.headers.get("user-agent")
    ip = request.client.host if request.client else None
    attempts = LoginAttemptService(session_service.store)
    attempts.ensure_not_blocked(email=payload.email, ip=ip)

    user = session.scalar(
        select(UserEntity)
        .options(selectinload(UserEntity.credential), selectinload(UserEntity.permissions))
        .where(UserEntity.email == payload.email)
        .limit(1)
    )

    if user is None or user.deleted_at is not None or user.credential is None:
        attempts.record_failure(email=payload.email, ip=ip)
        raise AuthInvalidCredentialsError()

    if not verify_password(payload.password, user.credential.password_hash):
        attempts.record_failure(email=payload.email, ip=ip)
        raise AuthInvalidCredentialsError()

    if not user.is_active:
        raise AuthInactiveUserError()

    attempts.clear(email=payload.email, ip=ip)
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


@router.get(
    "/password-policy",
    response_model=PasswordPolicyResponse,
    summary="Get current password policy",
)
def get_password_policy() -> PasswordPolicyResponse:
    return PasswordPolicyResponse(**password_policy.describe())


@router.post(
    "/change-password",
    response_model=PasswordChangeResponse,
    summary="Change current user password",
)
def change_password(
    payload: PasswordChangeRequest,
    response: Response,
    current_user: UserEntity = auth_guard.require_user(),
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> PasswordChangeResponse:
    if current_user.credential is None or not verify_password(
        payload.current_password,
        current_user.credential.password_hash,
    ):
        raise AuthInvalidCredentialsError()

    _set_user_password(current_user, payload.new_password)
    session.flush()
    session_service.delete_all_sessions(user_id=current_user.id)
    clear_auth_cookies(response=response)
    return PasswordChangeResponse()


@router.post(
    "/password-recovery/request",
    response_model=PasswordRecoveryResponse,
    summary="Request password recovery",
)
def request_password_recovery(
    payload: PasswordRecoveryRequest,
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> PasswordRecoveryResponse:
    user = session.scalar(
        select(UserEntity)
        .options(selectinload(UserEntity.credential))
        .where(UserEntity.email == payload.email)
        .limit(1)
    )

    reset_token = None
    if user is not None and user.deleted_at is None and user.is_active and user.credential is not None:
        token = PasswordRecoveryService(session_service.store).create_reset_token(user=user)
        if settings.AUTH_EXPOSE_PASSWORD_RESET_TOKEN:
            reset_token = token

    return PasswordRecoveryResponse(reset_token=reset_token)


@router.post(
    "/password-recovery/confirm",
    response_model=PasswordResetConfirmResponse,
    summary="Confirm password recovery with reset token",
)
def confirm_password_recovery(
    payload: PasswordResetConfirmRequest,
    response: Response,
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> PasswordResetConfirmResponse:
    user_id = PasswordRecoveryService(session_service.store).consume_reset_token(token=payload.reset_token)
    user = session.scalar(
        select(UserEntity)
        .options(selectinload(UserEntity.credential))
        .where(UserEntity.id == user_id)
        .limit(1)
    )
    if user is None or user.deleted_at is not None or not user.is_active or user.credential is None:
        raise AuthInvalidPasswordResetTokenError()

    _set_user_password(user, payload.new_password)
    session.flush()
    session_service.delete_all_sessions(user_id=user.id)
    clear_auth_cookies(response=response)
    return PasswordResetConfirmResponse()


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


@internal_router.post(
    "/introspect",
    response_model=IntrospectionResponse,
    summary="Validate a token and optional permission for service-to-service authorization",
)
def introspect(
    payload: IntrospectionRequest,
    request: Request,
    internal_service: InternalService = internal_service_guard.require_service(),
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
    session: Session = Depends(get_session),
    session_service: SessionService = Depends(get_session_service),
) -> IntrospectionResponse:
    user = auth_guard.get_current_user(
        request=request,
        credentials=credentials,
        session=session,
        session_service=session_service,
    )
    permissions = serialize_user_permissions(user)
    allowed = True

    if payload.required_permission is not None:
        allowed = user_has_permission(
            user,
            domain=payload.required_permission.domain,
            action=payload.required_permission.action,
        )

    return IntrospectionResponse(
        active=True,
        allowed=allowed,
        user=IntrospectionUser(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            token_version=user.token_version,
        ),
        permissions=permissions,
        required_permission=payload.required_permission,
    )
