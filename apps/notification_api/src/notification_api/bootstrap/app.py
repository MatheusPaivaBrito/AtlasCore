from fastapi import FastAPI

from notification_api.bootstrap.exceptions import register_api_exception_handlers
from notification_api.bootstrap.routes import register_routes
from notification_api.infrastructure.settings import settings
from shared_kernel.http import apply_cors


def create_app() -> FastAPI:
    app = FastAPI(
        title="AtlasCore Notification API",
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
