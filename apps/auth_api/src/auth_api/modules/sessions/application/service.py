from __future__ import annotations

from hashlib import sha256
from typing import Any
from uuid import UUID

from auth_api.infrastructure.settings import settings
from auth_api.modules.sessions.application.stores import RedisSessionStore, SessionStore
from auth_api.modules.users.domain.user_entity import UserEntity
from shared_kernel.time import DateTimeService


class SessionService:
    def __init__(self, store: SessionStore) -> None:
        self.store = store

    @staticmethod
    def generate_device_id(*, user_id: UUID, user_agent: str | None, ip: str | None) -> str:
        raw_value = f"{user_id}:{user_agent or 'unknown-agent'}:{ip or 'unknown-ip'}"
        return sha256(raw_value.encode()).hexdigest()

    def register_session(
        self,
        *,
        user: UserEntity,
        session_id: str,
        refresh_token: str,
        user_agent: str | None,
        ip: str | None,
    ) -> dict[str, Any]:
        existing = self.get_session(user_id=user.id, session_id=session_id) or {}
        now = DateTimeService.utc_now().isoformat()
        payload = {
            "session_id": session_id,
            "user_id": str(user.id),
            "refresh_token": refresh_token,
            "user_agent": user_agent,
            "ip": ip,
            "token_version": user.token_version,
            "created_at": existing.get("created_at") or now,
            "last_seen_at": now,
        }

        self.store.set(
            self._session_key(user_id=user.id, session_id=session_id),
            payload,
            ttl=settings.AUTH_SESSION_TTL_SECONDS,
        )
        self._add_user_session(user_id=user.id, session_id=session_id)
        self._enforce_device_limit(user_id=user.id)
        return payload

    def get_session(self, *, user_id: UUID, session_id: str) -> dict[str, Any] | None:
        return self.store.get(self._session_key(user_id=user_id, session_id=session_id))

    def list_sessions(self, *, user_id: UUID) -> list[dict[str, Any]]:
        sessions = []
        for session_id in self._list_user_session_ids(user_id=user_id):
            session = self.get_session(user_id=user_id, session_id=session_id)
            if session is not None:
                sessions.append(session)
        return sessions

    def delete_session(self, *, user_id: UUID, session_id: str) -> None:
        self.store.delete(self._session_key(user_id=user_id, session_id=session_id))
        sessions = [value for value in self._list_user_session_ids(user_id=user_id) if value != session_id]
        self.store.set(
            self._user_sessions_key(user_id=user_id),
            sessions,
            ttl=settings.AUTH_SESSION_TTL_SECONDS,
        )

    def delete_all_sessions(self, *, user_id: UUID) -> None:
        for session_id in self._list_user_session_ids(user_id=user_id):
            self.store.delete(self._session_key(user_id=user_id, session_id=session_id))
        self.store.delete(self._user_sessions_key(user_id=user_id))

    @staticmethod
    def _session_key(*, user_id: UUID, session_id: str) -> str:
        return f"{settings.REDIS_KEY_PREFIX}:{user_id}:session:{session_id}"

    @staticmethod
    def _user_sessions_key(*, user_id: UUID) -> str:
        return f"{settings.REDIS_KEY_PREFIX}:{user_id}:sessions"

    def _list_user_session_ids(self, *, user_id: UUID) -> list[str]:
        value = self.store.get(self._user_sessions_key(user_id=user_id))
        return list(value or [])

    def _add_user_session(self, *, user_id: UUID, session_id: str) -> None:
        sessions = self._list_user_session_ids(user_id=user_id)
        if session_id in sessions:
            sessions.remove(session_id)
        sessions.append(session_id)
        self.store.set(
            self._user_sessions_key(user_id=user_id),
            sessions,
            ttl=settings.AUTH_SESSION_TTL_SECONDS,
        )

    def _enforce_device_limit(self, *, user_id: UUID) -> None:
        sessions = self._list_user_session_ids(user_id=user_id)
        while len(sessions) > settings.AUTH_MAX_DEVICES:
            oldest_session_id = sessions.pop(0)
            self.store.delete(self._session_key(user_id=user_id, session_id=oldest_session_id))
        self.store.set(
            self._user_sessions_key(user_id=user_id),
            sessions,
            ttl=settings.AUTH_SESSION_TTL_SECONDS,
        )


def get_session_service() -> SessionService:
    return SessionService(RedisSessionStore())
