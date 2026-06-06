from fastapi import FastAPI

from core_api.bootstrap.routes import register_routes


def create_app() -> FastAPI:
    app = FastAPI(title="AtlasCore Core API")
    register_routes(app)
    return app
