from fastapi import APIRouter, Request

from observability_api.infrastructure.providers import grafana_status, loki_status, sentry_status
from shared_kernel.http import HomeAction, HomeCard, HomePage, HomeSection, render_service_home


router = APIRouter(include_in_schema=False)


def _provider_card(provider: dict, *, title: str, description: str) -> HomeCard:
    status = str(provider["status"])
    return HomeCard(
        title=title,
        description=description,
        status=status,
        available=status == "ok",
        code=provider.get("url"),
    )


@router.get("/")
def home(request: Request):
    loki = loki_status()
    grafana = grafana_status()
    sentry = sentry_status()

    return render_service_home(
        request=request,
        page=HomePage(
            service_name="AtlasCore Observability API",
            eyebrow="FastAPI - Observability - Loki - Grafana - Sentry",
            description=(
                "Observability boundary for AtlasCore. It gives the platform a small API surface for "
                "readiness, incident capture, dashboard links, log queries, alert events and release markers."
            ),
            actions=(
                HomeAction(label="Open Swagger Docs", url="/docs", primary=True),
                HomeAction(label="Open ReDoc", url="/redoc"),
                HomeAction(label="Readiness", url="/ready"),
                HomeAction(label="AtlasCore Home", url="http://localhost:8000"),
            ),
            sections=(
                HomeSection(
                    title="Observability providers",
                    description=(
                        "Loki and Grafana run locally through Docker. Sentry is an external integration "
                        "activated only when SENTRY_DSN is configured."
                    ),
                    columns=3,
                    cards=(
                        _provider_card(
                            loki,
                            title="Loki",
                            description="Log storage and query API used by /log-queries.",
                        ),
                        _provider_card(
                            grafana,
                            title="Grafana",
                            description="Dashboard UI and health endpoint exposed by the local container.",
                        ),
                        HomeCard(
                            title="Sentry",
                            description=sentry.get("reason") or "External error tracking is configured.",
                            status=str(sentry["status"]),
                            available=sentry["status"] == "configured",
                            code=str(sentry["mode"]),
                        ),
                    ),
                ),
                HomeSection(
                    title="Useful routes",
                    description="Small contracts for testing observability flows before deeper platform wiring.",
                    columns=3,
                    cards=(
                        HomeCard(
                            title="Incidents",
                            status="POST /incidents",
                            description="Captures an incident locally or forwards it to Sentry when configured.",
                            links=(HomeAction(label="Swagger", url="/docs#/incidents/capture_incidents_post"),),
                        ),
                        HomeCard(
                            title="Log queries",
                            status="Loki query helpers",
                            description="Exposes label discovery, query endpoint and examples.",
                            links=(HomeAction(label="Examples", url="/log-queries/examples"),),
                        ),
                        HomeCard(
                            title="Dashboards",
                            status="Provider links",
                            description="Centralizes links and provider health for local observability tools.",
                            links=(HomeAction(label="Providers", url="/dashboards/providers"),),
                        ),
                    ),
                ),
            ),
        ),
    )
