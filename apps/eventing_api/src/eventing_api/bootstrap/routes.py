from fastapi import FastAPI

from eventing_api.bootstrap.health import router as health_router
from eventing_api.modules.topics.presentation.routes import router as topics_router
from eventing_api.modules.schemas.presentation.routes import router as schemas_router
from eventing_api.modules.event_contracts.presentation.routes import router as event_contracts_router
from eventing_api.modules.outbox.presentation.routes import router as outbox_router
from eventing_api.modules.streams.presentation.routes import router as streams_router
from eventing_api.modules.projections.presentation.routes import router as projections_router


def register_routes(app: FastAPI) -> None:
    app.include_router(health_router)
    app.include_router(topics_router)
    app.include_router(schemas_router)
    app.include_router(event_contracts_router)
    app.include_router(outbox_router)
    app.include_router(streams_router)
    app.include_router(projections_router)
