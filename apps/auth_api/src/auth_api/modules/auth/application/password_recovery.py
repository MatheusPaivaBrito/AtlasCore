from __future__ import annotations

from hashlib import sha256
from secrets import token_urlsafe
from uuid import UUID

from auth_api.infrastructure.settings import settings
from auth_api.modules.sessions.application.stores import SessionStore
from auth_api.modules.users.user_entity import UserEntity
from auth_api.shared.exceptions import AuthInvalidPasswordResetTokenError
from shared_kernel.time import DateTimeService


class PasswordRecoveryService:
    def __init__(self, store: SessionStore) -> None:
        self.store = store

    def create_reset_token(self, *, user: UserEntity) -> str:
        token = token_urlsafe(48)
        token_hash = self._hash_token(token)
        self.store.set(
            self._reset_key(token_hash=token_hash),
            {
                "user_id": str(user.id),
                "email": user.email,
                "created_at": DateTimeService.utc_now().isoformat(),
            },
            ttl=settings.AUTH_PASSWORD_RESET_TOKEN_TTL_SECONDS,
        )
        return token

    def consume_reset_token(self, *, token: str) -> UUID:
        token_hash = self._hash_token(token)
        key = self._reset_key(token_hash=token_hash)
        payload = self.store.get(key)
        self.store.delete(key)

        if not payload or not payload.get("user_id"):
            raise AuthInvalidPasswordResetTokenError()

        return UUID(str(payload["user_id"]))

    @staticmethod
    def _hash_token(token: str) -> str:
        return sha256(token.encode()).hexdigest()

    @staticmethod
    def _reset_key(*, token_hash: str) -> str:
        return f"{settings.REDIS_KEY_PREFIX}:password_reset:{token_hash}"
