from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any
from uuid import uuid4

import jwt
from starlette import status

from shared_kernel.errors import ApplicationError, ErrorTarget
from shared_kernel.time import DateTimeService


@dataclass(frozen=True, slots=True)
class ServiceToken:
    issuer: str
    subject: str
    audience: str
    scopes: tuple[str, ...]
    jwt_id: str
    claims: dict[str, Any]


class ServiceTokenMissingError(ApplicationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "service_auth.missing_token"
    message = "Service authentication token was not provided."


class ServiceTokenExpiredError(ApplicationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "service_auth.expired_token"
    message = "Service authentication token has expired."


class ServiceTokenInvalidError(ApplicationError):
    status_code = status.HTTP_401_UNAUTHORIZED
    code = "service_auth.invalid_token"
    message = "Service authentication token is invalid."


class ServiceTokenInvalidAudienceError(ApplicationError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "service_auth.invalid_audience"
    message = "Service authentication token was not issued for this service."


class ServiceTokenPermissionDeniedError(ApplicationError):
    status_code = status.HTTP_403_FORBIDDEN
    code = "service_auth.permission_denied"
    message = "Calling service does not have the required service scope."

    def __init__(self, *, required_scopes: tuple[str, ...], token_scopes: tuple[str, ...]) -> None:
        super().__init__(
            target=ErrorTarget(
                entity="service_token",
                payload={
                    "required_scopes": list(required_scopes),
                    "token_scopes": list(token_scopes),
                },
            ),
        )


class ServiceTokenManager:
    def __init__(
        self,
        *,
        secret_key: str,
        issuer: str = "atlascore",
        algorithm: str = "HS256",
        default_ttl_seconds: int = 300,
    ) -> None:
        self.secret_key = secret_key
        self.issuer = issuer
        self.algorithm = algorithm
        self.default_ttl_seconds = default_ttl_seconds

    def create_token(
        self,
        *,
        subject: str,
        audience: str,
        scopes: tuple[str, ...] | list[str],
        ttl_seconds: int | None = None,
        extra_claims: dict[str, Any] | None = None,
    ) -> str:
        now = DateTimeService.utc_now()
        payload: dict[str, Any] = {
            "iss": self.issuer,
            "sub": subject,
            "aud": audience,
            "scope": list(scopes),
            "type": "service",
            "jti": str(uuid4()),
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(seconds=ttl_seconds or self.default_ttl_seconds),
        }
        payload.update(extra_claims or {})

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(
        self,
        *,
        token: str,
        audience: str,
        required_scopes: tuple[str, ...] = (),
        allowed_subjects: tuple[str, ...] = (),
    ) -> ServiceToken:
        try:
            claims = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=audience,
            )
        except jwt.ExpiredSignatureError as exc:
            raise ServiceTokenExpiredError() from exc
        except jwt.InvalidAudienceError as exc:
            raise ServiceTokenInvalidAudienceError() from exc
        except jwt.InvalidTokenError as exc:
            raise ServiceTokenInvalidError() from exc

        if claims.get("type") != "service":
            raise ServiceTokenInvalidError()

        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise ServiceTokenInvalidError()

        token_scopes = _normalize_scopes(claims.get("scope", claims.get("scopes", ())))

        if allowed_subjects and subject not in allowed_subjects:
            raise ServiceTokenPermissionDeniedError(
                required_scopes=tuple(f"service:{service}" for service in allowed_subjects),
                token_scopes=(f"service:{subject}",),
            )

        missing_scopes = tuple(scope for scope in required_scopes if scope not in token_scopes)
        if missing_scopes:
            raise ServiceTokenPermissionDeniedError(
                required_scopes=missing_scopes,
                token_scopes=token_scopes,
            )

        audience_claim = claims.get("aud")
        if isinstance(audience_claim, list):
            normalized_audience = audience
        elif isinstance(audience_claim, str):
            normalized_audience = audience_claim
        else:
            raise ServiceTokenInvalidAudienceError()

        jwt_id = claims.get("jti")
        if not isinstance(jwt_id, str) or not jwt_id:
            raise ServiceTokenInvalidError()

        return ServiceToken(
            issuer=str(claims["iss"]),
            subject=subject,
            audience=normalized_audience,
            scopes=token_scopes,
            jwt_id=jwt_id,
            claims=claims,
        )


def _normalize_scopes(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        return tuple(scope for scope in value.split() if scope)

    if isinstance(value, list | tuple | set):
        return tuple(item for item in value if isinstance(item, str) and item)

    return ()
