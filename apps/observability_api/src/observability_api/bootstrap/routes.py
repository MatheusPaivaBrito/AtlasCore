from fastapi import FastAPI

from observability_api.bootstrap.docs import router as docs_router
from observability_api.bootstrap.home import router as home_router
from observability_api.bootstrap.health import router as health_router
from observability_api.modules.alerts.presentation.routes import router as alerts_router
from observability_api.modules.dashboards.presentation.routes import router as dashboards_router
from observability_api.modules.incidents.presentation.routes import router as incidents_router
from observability_api.modules.log_queries.presentation.routes import router as log_queries_router
from observability_api.modules.releases.presentation.routes import router as releases_router


def register_routes(app: FastAPI) -> None:
    app.include_router(docs_router)
    app.include_router(home_router)
    app.include_router(health_router)
    app.include_router(incidents_router)
    app.include_router(alerts_router)
    app.include_router(dashboards_router)
    app.include_router(log_queries_router)
    app.include_router(releases_router)
