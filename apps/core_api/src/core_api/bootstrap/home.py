from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from core_api.infrastructure.settings import settings


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(Path(__file__).with_name("templates")))

COMMON_HEALTH_PATH = "/health"
COMMON_DOCS_PATH = "/docs"
COMMON_REDOC_PATH = "/redoc"


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def _is_url_available(url: str) -> bool:
    try:
        with urlopen(url, timeout=settings.AUTH_API_CHECK_TIMEOUT_SECONDS) as response:
            return 200 <= response.status < 400
    except (HTTPError, TimeoutError, URLError, OSError):
        return False


def _api_service(
    *,
    name: str,
    port: int,
    description: str,
    base_url: str | None = None,
    current: bool = False,
) -> dict[str, object]:
    service_base_url = base_url or f"http://localhost:{port}"
    health_url = _join_url(service_base_url, COMMON_HEALTH_PATH)
    available = True if current else _is_url_available(health_url)

    return {
        "name": name,
        "port": port,
        "description": description,
        "base_url": service_base_url,
        "docs_url": _join_url(service_base_url, COMMON_DOCS_PATH),
        "redoc_url": _join_url(service_base_url, COMMON_REDOC_PATH),
        "available": available,
    }


def _documentation_site(*, name: str, port: int, description: str) -> dict[str, object]:
    base_url = f"http://localhost:{port}"

    return {
        "name": name,
        "port": port,
        "description": description,
        "base_url": base_url,
        "available": _is_url_available(base_url),
    }


@router.get("/")
def home(request: Request):
    api_services = [
        _api_service(
            name="Core API",
            port=settings.CORE_API_PORT,
            description="Business data, Postgres ownership, verticalized library CRUD and public assets.",
            base_url=f"http://localhost:{settings.CORE_API_PORT}",
            current=True,
        ),
        _api_service(
            name="Auth API",
            port=settings.AUTH_API_PORT,
            description="Identity, authentication, sessions and access-control boundary.",
            base_url=settings.AUTH_API_PUBLIC_URL,
        ),
        _api_service(
            name="Eventing API",
            port=settings.EVENTING_API_PORT,
            description="Kafka-facing platform boundary for topics, schemas, contracts, outbox and projections.",
        ),
        _api_service(
            name="Notification API",
            port=settings.NOTIFICATION_API_PORT,
            description="Notification platform for e-mail, Slack, templates, channels and delivery attempts.",
        ),
        _api_service(
            name="Observability API",
            port=settings.OBSERVABILITY_API_PORT,
            description="Observability platform for incidents, alerts, dashboards, log queries and releases.",
        ),
    ]
    documentation_sites = [
        _documentation_site(
            name="MkDocs PT-BR",
            port=settings.DOCS_PT_PORT,
            description="Portuguese project documentation, architecture notes and workflow guide.",
        ),
        _documentation_site(
            name="MkDocs EN",
            port=settings.DOCS_EN_PORT,
            description="English interview-ready documentation, ADRs and talking points.",
        ),
    ]

    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "service_name": "AtlasCore",
            "api_services": api_services,
            "documentation_sites": documentation_sites,
            "core_docs_url": COMMON_DOCS_PATH,
            "core_redoc_url": COMMON_REDOC_PATH,
            "docs_pt_url": f"http://localhost:{settings.DOCS_PT_PORT}",
            "docs_en_url": f"http://localhost:{settings.DOCS_EN_PORT}",
        },
    )
