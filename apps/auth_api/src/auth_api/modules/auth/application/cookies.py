from fastapi import Response

from auth_api.infrastructure.settings import settings


ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"


def set_auth_cookies(*, response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE,
        value=access_token,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path=settings.JWT_COOKIE_PATH,
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE,
        value=refresh_token,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path=settings.JWT_COOKIE_PATH,
        max_age=settings.AUTH_SESSION_TTL_SECONDS,
    )


def clear_auth_cookies(*, response: Response) -> None:
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE, path=settings.JWT_COOKIE_PATH)
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE, path=settings.JWT_COOKIE_PATH)
