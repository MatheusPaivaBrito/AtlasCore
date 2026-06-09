from __future__ import annotations

from hashlib import sha256

from auth_api.infrastructure.settings import settings
from auth_api.modules.sessions.application.stores import SessionStore
from auth_api.shared.exceptions import AuthTooManyLoginAttemptsError
from shared_kernel.time import DateTimeService


class LoginAttemptService:
    def __init__(self, store: SessionStore) -> None:
        self.store = store

    def ensure_not_blocked(self, *, email: str, ip: str | None) -> None:
        state = self.store.get(self._attempt_key(email=email, ip=ip)) or {}
        blocked_until = state.get("blocked_until")
        if not blocked_until:
            return

        if DateTimeService.is_future(DateTimeService.from_iso(blocked_until)):
            raise AuthTooManyLoginAttemptsError()

    def record_failure(self, *, email: str, ip: str | None) -> None:
        key = self._attempt_key(email=email, ip=ip)
        state = self.store.get(key) or {}
        attempts = int(state.get("attempts") or 0) + 1
        payload = {
            "attempts": attempts,
            "last_failed_at": DateTimeService.utc_now().isoformat(),
        }

        if attempts >= settings.AUTH_LOGIN_MAX_ATTEMPTS:
            payload["blocked_until"] = DateTimeService.add_seconds(
                DateTimeService.utc_now(),
                settings.AUTH_LOGIN_BLOCK_SECONDS,
            ).isoformat()

        self.store.set(
            key,
            payload,
            ttl=max(settings.AUTH_LOGIN_WINDOW_SECONDS, settings.AUTH_LOGIN_BLOCK_SECONDS),
        )

    def clear(self, *, email: str, ip: str | None) -> None:
        self.store.delete(self._attempt_key(email=email, ip=ip))

    @staticmethod
    def _attempt_key(*, email: str, ip: str | None) -> str:
        raw_value = f"{email.strip().lower()}:{ip or 'unknown-ip'}"
        digest = sha256(raw_value.encode()).hexdigest()
        return f"{settings.REDIS_KEY_PREFIX}:login_attempt:{digest}"
