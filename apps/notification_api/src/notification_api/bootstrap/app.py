from fastapi import FastAPI

from notification_api.bootstrap.routes import register_routes


def create_app() -> FastAPI:
    app = FastAPI(title="AtlasCore Notification API")
    register_routes(app)
    return app
