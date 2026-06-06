from fastapi import FastAPI

from eventing_api.bootstrap.routes import register_routes


def create_app() -> FastAPI:
    app = FastAPI(title="AtlasCore Eventing API")
    register_routes(app)
    return app
