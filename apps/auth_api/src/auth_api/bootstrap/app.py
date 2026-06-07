from fastapi import FastAPI

from auth_api.bootstrap.exceptions import register_api_exception_handlers
from auth_api.bootstrap.routes import register_routes
from auth_api.infrastructure.settings import settings
from shared_kernel.http import apply_cors


def create_app() -> FastAPI:
    app = FastAPI(title="AtlasCore Auth API")
    apply_cors(app, settings.CORS_CONFIG)
    register_api_exception_handlers(app)
    register_routes(app)
    return app
