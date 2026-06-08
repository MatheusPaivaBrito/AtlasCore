from fastapi import FastAPI

from auth_api.bootstrap.exceptions import register_api_exception_handlers
from auth_api.bootstrap.routes import register_routes
from auth_api.infrastructure.settings import settings
from shared_kernel.http import apply_cors

OPENAPI_TAGS = [
    {
        "name": "health",
        "description": "Runtime health checks for Auth API.",
    },
    {
        "name": "auth",
        "description": "Login, refresh token rotation and logout flows.",
    },
    {
        "name": "internal-auth",
        "description": "Service-to-service authorization endpoints consumed by other AtlasCore APIs.",
    },
    {
        "name": "users - query",
        "description": "Read-side user identity routes.",
    },
    {
        "name": "users - command",
        "description": "Write-side user identity routes.",
    },
    {
        "name": "sessions - query",
        "description": "Read-side routes for active Auth sessions.",
    },
    {
        "name": "sessions - command",
        "description": "Write-side routes for session revocation.",
    },
    {
        "name": "access-control - query",
        "description": "Read-side RBAC profile and permission routes.",
    },
    {
        "name": "access-control - command",
        "description": "Write-side RBAC permission management routes.",
    },
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="AtlasCore Auth API",
        description=(
            "Identity and security API for AtlasCore. It owns user credentials, JWT issuance, "
            "Redis-backed sessions, device limits and RBAC permissions."
        ),
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
        openapi_tags=OPENAPI_TAGS,
    )
    apply_cors(app, settings.CORS_CONFIG)
    register_api_exception_handlers(app)
    register_routes(app)
    return app
