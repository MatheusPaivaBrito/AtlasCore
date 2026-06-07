from fastapi import FastAPI

from core_api.bootstrap.docs import router as docs_router
from core_api.bootstrap.health import router as health_router
from core_api.bootstrap.home import router as home_router
from core_api.modules.library.presentation.routes import router as library_router
from core_api.modules.public_assets.presentation.routes import router as public_assets_router


def register_routes(app: FastAPI) -> None:
    app.include_router(home_router)
    app.include_router(docs_router)
    app.include_router(health_router)
    app.include_router(library_router)
    app.include_router(public_assets_router)
