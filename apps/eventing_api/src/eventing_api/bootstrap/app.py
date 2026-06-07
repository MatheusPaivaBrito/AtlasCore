from fastapi import FastAPI

from eventing_api.bootstrap.exceptions import register_api_exception_handlers
from eventing_api.bootstrap.routes import register_routes
from eventing_api.infrastructure.settings import settings
from shared_kernel.http import apply_cors


def create_app() -> FastAPI:
    app = FastAPI(title="AtlasCore Eventing API")
    apply_cors(app, settings.CORS_CONFIG)
    register_api_exception_handlers(app)
    register_routes(app)
    return app
