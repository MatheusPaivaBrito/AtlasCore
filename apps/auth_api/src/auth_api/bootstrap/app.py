from fastapi import FastAPI

from auth_api.bootstrap.exceptions import register_api_exception_handlers
from auth_api.bootstrap.routes import register_routes


def create_app() -> FastAPI:
    app = FastAPI(title="AtlasCore Auth API")
    register_api_exception_handlers(app)
    register_routes(app)
    return app
