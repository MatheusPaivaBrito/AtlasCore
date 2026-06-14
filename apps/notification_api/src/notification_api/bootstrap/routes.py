from fastapi import FastAPI

from notification_api.bootstrap.docs import router as docs_router
from notification_api.bootstrap.home import router as home_router
from notification_api.bootstrap.health import router as health_router
from notification_api.modules.channels.presentation.routes import router as channels_router
from notification_api.modules.delivery_attempts.presentation.routes import router as delivery_attempts_router
from notification_api.modules.notifications.presentation.routes import router as notifications_router
from notification_api.modules.templates.presentation.routes import router as templates_router


def register_routes(app: FastAPI) -> None:
    app.include_router(docs_router)
    app.include_router(home_router)
    app.include_router(health_router)
    app.include_router(notifications_router)
    app.include_router(templates_router)
    app.include_router(channels_router)
    app.include_router(delivery_attempts_router)
