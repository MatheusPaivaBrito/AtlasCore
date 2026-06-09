from __future__ import annotations

from uuid import UUID

from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from auth_api.infrastructure.database.connection import get_session
from auth_api.modules.access_control.application.permissions import user_has_permission
from auth_api.modules.auth.application.cookies import ACCESS_TOKEN_COOKIE
from auth_api.modules.auth.application.tokens import jwt_service
from auth_api.modules.sessions.application.service import SessionService, get_session_service
from auth_api.modules.users.user_entity import UserEntity
from auth_api.shared.exceptions import (
    AuthInactiveUserError,
    AuthInvalidSessionError,
    AuthMissingTokenError,
    AuthPermissionDeniedError,
    AuthResourceNotFoundError,
)


bearer_scheme = HTTPBearer(auto_error=False)


class AuthGuard:
    @staticmethod
    def extract_access_token(
        *,
        request: Request,
        credentials: HTTPAuthorizationCredentials | None,
    ) -> str | None:
        if credentials is not None:
            return credentials.credentials
        return request.cookies.get(ACCESS_TOKEN_COOKIE)

    def get_current_user(
        self,
        *,
        request: Request,
        credentials: HTTPAuthorizationCredentials | None,
        session: Session,
        session_service: SessionService,
    ) -> UserEntity:
        token = self.extract_access_token(request=request, credentials=credentials)
        if not token:
            raise AuthMissingTokenError()

        payload = jwt_service.verify_access_token(token)
        user_id = UUID(str(payload["sub"]))
        session_id = str(payload.get("session_id") or "")

        if not session_id:
            raise AuthInvalidSessionError()

        auth_session = session_service.get_session(user_id=user_id, session_id=session_id)
        if auth_session is None:
            raise AuthInvalidSessionError()

        user = self._load_user(session=session, user_id=user_id)
        if not user.is_active:
            raise AuthInactiveUserError()

        token_version = int(payload.get("token_version") or 0)
        session_token_version = int(auth_session.get("token_version") or 0)
        if token_version != user.token_version or session_token_version != user.token_version:
            raise AuthInvalidSessionError()

        request.state.auth_session = auth_session
        request.state.jwt_payload = payload
        return user

    def require_user(self):
        def dependency(
            request: Request,
            credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
            session: Session = Depends(get_session),
            session_service: SessionService = Depends(get_session_service),
        ) -> UserEntity:
            return self.get_current_user(
                request=request,
                credentials=credentials,
                session=session,
                session_service=session_service,
            )

        return Depends(dependency)

    def require_permission(self, *, domain: str, action: str):
        def dependency(
            request: Request,
            credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
            session: Session = Depends(get_session),
            session_service: SessionService = Depends(get_session_service),
        ) -> UserEntity:
            user = self.get_current_user(
                request=request,
                credentials=credentials,
                session=session,
                session_service=session_service,
            )
            if not user_has_permission(user, domain=domain, action=action):
                raise AuthPermissionDeniedError(domain=domain, action=action)
            return user

        return Depends(dependency)

    @staticmethod
    def _load_user(*, session: Session, user_id: UUID) -> UserEntity:
        statement = (
            select(UserEntity)
            .options(selectinload(UserEntity.permissions))
            .where(UserEntity.id == user_id)
            .limit(1)
        )
        user = session.scalar(statement)
        if user is None or user.deleted_at is not None:
            raise AuthResourceNotFoundError(entity="auth_users", resource_id=user_id)
        return user


auth_guard = AuthGuard()
