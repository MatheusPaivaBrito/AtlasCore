from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(Path(__file__).with_name("templates")))


@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={
            "service_name": "AtlasCore Auth API",
            "swagger_url": "/docs",
            "redoc_url": "/redoc",
            "health_url": "/health",
            "login_url": "/auth/login",
            "introspection_url": "/internal/auth/introspect",
            "core_home_url": "http://localhost:8000",
            "core_docs_url": "http://localhost:8000/docs",
            "docs_pt_url": "http://localhost:8080",
            "docs_en_url": "http://localhost:8081",
        },
    )
