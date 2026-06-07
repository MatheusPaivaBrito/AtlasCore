from fastapi import FastAPI

from core_api.bootstrap.exceptions import register_api_exception_handlers
from core_api.bootstrap.routes import register_routes
from core_api.infrastructure.settings import settings
from shared_kernel.http import apply_cors

OPENAPI_TAGS = [
    {
        "name": "system",
        "description": "Runtime health, database checks and operational endpoints.",
    },
    {
        "name": "library - query",
        "description": "Read-side metadata for the library bounded context.",
    },
    {
        "name": "libraries - query",
        "description": "Read-side routes for library aggregate records.",
    },
    {
        "name": "libraries - command",
        "description": "Write-side routes for library aggregate records.",
    },
    {
        "name": "shelves - query",
        "description": "Read-side routes for shelves.",
    },
    {
        "name": "shelves - command",
        "description": "Write-side routes for shelves.",
    },
    {
        "name": "sections - query",
        "description": "Read-side routes for shelf sections.",
    },
    {
        "name": "sections - command",
        "description": "Write-side routes for shelf sections.",
    },
    {
        "name": "books - query",
        "description": "Read-side routes for books.",
    },
    {
        "name": "books - command",
        "description": "Write-side routes for books.",
    },
    {
        "name": "readers - query",
        "description": "Read-side routes for readers.",
    },
    {
        "name": "readers - command",
        "description": "Write-side routes for readers.",
    },
    {
        "name": "rentals - query",
        "description": "Read-side routes for rentals.",
    },
    {
        "name": "rentals - command",
        "description": "Write-side routes for rentals.",
    },
    {
        "name": "public-assets: query",
        "description": "Read-side routes describing public image and document assets.",
    },
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="AtlasCore Core API",
        description=(
            "Core business API for AtlasCore. It owns the relational domain model, "
            "starts with a complete library CRUD, and keeps documentation grouped by query and command flows."
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
