from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.templating import _TemplateResponse


@dataclass(frozen=True)
class HomeAction:
    label: str
    url: str
    primary: bool = False
    available: bool = True


@dataclass(frozen=True)
class HomeCard:
    title: str
    description: str
    status: str
    available: bool = True
    code: str | None = None
    links: tuple[HomeAction, ...] = ()
    compact: bool = False


@dataclass(frozen=True)
class HomeSection:
    title: str
    description: str
    cards: tuple[HomeCard, ...]
    columns: int = 3


@dataclass(frozen=True)
class HomePage:
    service_name: str
    eyebrow: str
    description: str
    actions: tuple[HomeAction, ...]
    sections: tuple[HomeSection, ...] = field(default_factory=tuple)


templates = Jinja2Templates(directory=str(Path(__file__).with_name("templates")))


def join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def is_url_available(url: str, *, timeout_seconds: float = 0.2) -> bool:
    try:
        with urlopen(url, timeout=timeout_seconds) as response:
            return 200 <= response.status < 400
    except (HTTPError, TimeoutError, URLError, OSError):
        return False


def render_service_home(request: Request, page: HomePage) -> _TemplateResponse:
    return templates.TemplateResponse(
        request=request,
        name="service_home.html",
        context={"page": page},
    )
