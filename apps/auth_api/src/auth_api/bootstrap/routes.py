from fastapi import FastAPI

from auth_api.bootstrap.docs import router as docs_router
from auth_api.bootstrap.health import router as health_router
from auth_api.bootstrap.home import router as home_router
from auth_api.modules.users.user_router import router as users_router
from auth_api.modules.auth.presentation.routes import internal_router as internal_auth_router
from auth_api.modules.auth.presentation.routes import router as auth_router
from auth_api.modules.sessions.presentation.routes import router as sessions_router
from auth_api.modules.access_control.presentation.routes import router as access_control_router


def register_routes(app: FastAPI) -> None:
    app.include_router(home_router)
    app.include_router(docs_router)
    app.include_router(health_router)
    app.include_router(users_router)
    app.include_router(auth_router)
    app.include_router(internal_auth_router)
    app.include_router(sessions_router)
    app.include_router(access_control_router)
