from fastapi import FastAPI

from observability_api.bootstrap.exceptions import register_api_exception_handlers
from observability_api.bootstrap.routes import register_routes
from observability_api.infrastructure.settings import settings
from observability_api.infrastructure.sentry import configure_sentry
from shared_kernel.http import apply_cors


def create_app() -> FastAPI:
    configure_sentry()
    app = FastAPI(
        title="AtlasCore Observability API",
        version="0.1.0",
        docs_url=None,
        redoc_url=None,
        swagger_ui_parameters={
            "docExpansion": "none",
            "filter": True,
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "persistAuthorization": True,
        },
    )
    apply_cors(app, settings.CORS_CONFIG)
    register_api_exception_handlers(app)
    register_routes(app)
    return app
