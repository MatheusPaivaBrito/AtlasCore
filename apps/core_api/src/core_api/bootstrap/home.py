from fastapi import APIRouter, Request

from core_api.infrastructure.platform_discovery import platform_discovery_settings
from shared_kernel.http import (
    HomeAction,
    HomeCard,
    HomePage,
    HomeSection,
    is_url_available,
    join_url,
    render_service_home,
)


router = APIRouter(include_in_schema=False)

def _join_url(base_url: str, path: str) -> str:
    return join_url(base_url, path)


def _is_url_available(url: str) -> bool:
    return is_url_available(
        url,
        timeout_seconds=platform_discovery_settings.SERVICE_CHECK_TIMEOUT_SECONDS,
    )


def _api_service(
    *,
    name: str,
    port: int,
    description: str,
    base_url: str | None = None,
    current: bool = False,
) -> dict[str, object]:
    service_base_url = base_url or f"http://localhost:{port}"
    health_url = _join_url(service_base_url, platform_discovery_settings.SERVICE_HEALTH_PATH)
    available = True if current else _is_url_available(health_url)

    return HomeCard(
        title=name,
        description=description,
        status=f"{name} {'online' if available else 'offline'}",
        available=available,
        code=f"localhost:{port}",
        links=(
            HomeAction(
                label="Swagger",
                url=_join_url(service_base_url, platform_discovery_settings.SERVICE_DOCS_PATH),
                available=available,
            ),
            HomeAction(
                label="ReDoc",
                url=_join_url(service_base_url, platform_discovery_settings.SERVICE_REDOC_PATH),
                available=available,
            ),
        ),
    )


def _documentation_site(*, name: str, port: int, description: str) -> HomeCard:
    if port == platform_discovery_settings.DOCS_PT_PORT:
        base_url = platform_discovery_settings.DOCS_PT_PUBLIC_URL
    elif port == platform_discovery_settings.DOCS_EN_PORT:
        base_url = platform_discovery_settings.DOCS_EN_PUBLIC_URL
    else:
        base_url = f"http://localhost:{port}"
    available = _is_url_available(base_url)

    return HomeCard(
        title=name,
        description=description,
        status=f"{name} {'online' if available else 'offline'}",
        available=available,
        code=f"localhost:{port}",
        compact=True,
        links=(
            HomeAction(
                label="Open docs",
                url=base_url,
                available=available,
            ),
        ),
    )


@router.get("/")
def home(request: Request):
    api_services = [
        _api_service(
            name="Core API",
            port=platform_discovery_settings.CORE_API_PORT,
            description="Business data, Postgres ownership, verticalized library CRUD and public assets.",
            base_url=platform_discovery_settings.CORE_API_PUBLIC_URL,
            current=True,
        ),
        _api_service(
            name="Auth API",
            port=platform_discovery_settings.AUTH_API_PORT,
            description="Identity, authentication, sessions and access-control boundary.",
            base_url=platform_discovery_settings.AUTH_API_PUBLIC_URL,
        ),
        _api_service(
            name="Eventing API",
            port=platform_discovery_settings.EVENTING_API_PORT,
            description="Kafka-facing platform boundary for topics, schemas, contracts, outbox and projections.",
            base_url=platform_discovery_settings.EVENTING_API_PUBLIC_URL,
        ),
        _api_service(
            name="Notification API",
            port=platform_discovery_settings.NOTIFICATION_API_PORT,
            description="Notification platform for e-mail, Slack, templates, channels and delivery attempts.",
            base_url=platform_discovery_settings.NOTIFICATION_API_PUBLIC_URL,
        ),
        _api_service(
            name="Observability API",
            port=platform_discovery_settings.OBSERVABILITY_API_PORT,
            description="Observability platform for incidents, alerts, dashboards, log queries and releases.",
            base_url=platform_discovery_settings.OBSERVABILITY_API_PUBLIC_URL,
        ),
    ]
    documentation_sites = [
        _documentation_site(
            name="MkDocs PT-BR",
            port=platform_discovery_settings.DOCS_PT_PORT,
            description="Portuguese project documentation, architecture notes and workflow guide.",
        ),
        _documentation_site(
            name="MkDocs EN",
            port=platform_discovery_settings.DOCS_EN_PORT,
            description="English project documentation, ADRs and architecture talking points.",
        ),
    ]

    return render_service_home(
        request=request,
        page=HomePage(
            service_name=platform_discovery_settings.APP_NAME,
            eyebrow="FastAPI - DDD - Clean Architecture",
            description=(
                "AtlasCore is a backend foundation with product APIs, platform APIs, local infrastructure, "
                "MkDocs documentation and a Core API that already exposes a verticalized library domain."
            ),
            actions=(
                HomeAction(
                    label="Core Swagger",
                    url=platform_discovery_settings.SERVICE_DOCS_PATH,
                    primary=True,
                ),
                HomeAction(
                    label="Core ReDoc",
                    url=platform_discovery_settings.SERVICE_REDOC_PATH,
                ),
                HomeAction(
                    label="MkDocs PT-BR",
                    url=platform_discovery_settings.DOCS_PT_PUBLIC_URL,
                ),
                HomeAction(
                    label="MkDocs EN",
                    url=platform_discovery_settings.DOCS_EN_PUBLIC_URL,
                ),
            ),
            sections=(
                HomeSection(
                    title="API runtimes",
                    description=(
                        "Each backend has its own port. Online services expose Swagger/ReDoc links; "
                        "offline services still show the expected local address."
                    ),
                    cards=tuple(api_services),
                    columns=5,
                ),
                HomeSection(
                    title="Project documentation",
                    description=(
                        "MkDocs runs separately from the APIs so the architecture guide can be served "
                        "while backends are started and stopped independently."
                    ),
                    cards=tuple(documentation_sites),
                    columns=2,
                ),
            ),
        ),
    )
