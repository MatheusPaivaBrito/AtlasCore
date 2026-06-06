from fastapi import FastAPI

from observability_api.bootstrap.routes import register_routes


def create_app() -> FastAPI:
    app = FastAPI(title="AtlasCore Observability API")
    register_routes(app)
    return app
