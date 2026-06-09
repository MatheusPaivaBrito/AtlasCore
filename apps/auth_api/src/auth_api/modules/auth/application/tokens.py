from __future__ import annotations

from datetime import timedelta
from enum import StrEnum
from typing import Any
from uuid import uuid4

import jwt

from auth_api.infrastructure.settings import settings
from auth_api.modules.users.user_entity import UserEntity
from auth_api.shared.exceptions import AuthExpiredTokenError, AuthInvalidTokenError
from shared_kernel.time import DateTimeService


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class JWTService:
    def create_access_token(self, *, user: UserEntity, session_id: str) -> str:
        return self._create_token(
            user=user,
            session_id=session_id,
            token_type=TokenType.ACCESS,
            secret_key=settings.JWT_ACCESS_TOKEN_SECRET_KEY,
            expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        )

    def create_refresh_token(self, *, user: UserEntity, session_id: str) -> str:
        return self._create_token(
            user=user,
            session_id=session_id,
            token_type=TokenType.REFRESH,
            secret_key=settings.JWT_REFRESH_TOKEN_SECRET_KEY,
            expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        )

    def verify_access_token(self, token: str) -> dict[str, Any]:
        payload = self._verify_token(token=token, secret_key=settings.JWT_ACCESS_TOKEN_SECRET_KEY)
        if payload.get("type") != TokenType.ACCESS:
            raise AuthInvalidTokenError()
        return payload

    def verify_refresh_token(self, token: str) -> dict[str, Any]:
        payload = self._verify_token(token=token, secret_key=settings.JWT_REFRESH_TOKEN_SECRET_KEY)
        if payload.get("type") != TokenType.REFRESH:
            raise AuthInvalidTokenError()
        return payload

    def _create_token(
        self,
        *,
        user: UserEntity,
        session_id: str,
        token_type: TokenType,
        secret_key: str,
        expires_delta: timedelta,
    ) -> str:
        now = DateTimeService.utc_now()
        payload = {
            "iss": settings.JWT_ISSUER,
            "sub": str(user.id),
            "email": user.email,
            "type": token_type.value,
            "token_version": user.token_version,
            "session_id": session_id,
            "jti": str(uuid4()),
            "iat": now,
            "nbf": now,
            "exp": now + expires_delta,
        }
        return jwt.encode(payload, secret_key, algorithm=settings.JWT_ALGORITHM)

    @staticmethod
    def _verify_token(*, token: str, secret_key: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                secret_key,
                algorithms=[settings.JWT_ALGORITHM],
                issuer=settings.JWT_ISSUER,
            )
        except jwt.ExpiredSignatureError as exc:
            raise AuthExpiredTokenError() from exc
        except jwt.InvalidTokenError as exc:
            raise AuthInvalidTokenError() from exc


jwt_service = JWTService()
