from fastapi import APIRouter, Request

from shared_kernel.http import HomeAction, HomeCard, HomePage, HomeSection, render_service_home


router = APIRouter(include_in_schema=False)

@router.get("/")
def home(request: Request):
    return render_service_home(
        request=request,
        page=HomePage(
            service_name="AtlasCore Auth API",
            eyebrow="FastAPI - Auth - JWT - Redis Sessions - RBAC",
            description=(
                "Identity and security boundary for AtlasCore. This API owns users, bcrypt credentials, "
                "access and refresh tokens, Redis-backed sessions, device limits and permission checks used by Core."
            ),
            actions=(
                HomeAction(label="Open Swagger Docs", url="/docs", primary=True),
                HomeAction(label="Open ReDoc", url="/redoc"),
                HomeAction(label="Open AtlasCore Home", url="http://localhost:8000"),
            ),
            sections=(
                HomeSection(
                    title="Auth API capabilities",
                    description=(
                        "Auth stays independent from Core while exposing security contracts that other APIs can consume."
                    ),
                    columns=3,
                    cards=(
                        HomeCard(
                            title="Security boundary",
                            status="Auth API online",
                            description=(
                                "Login starts at /auth/login. The response returns access/refresh tokens "
                                "and sets HTTP-only cookies for browser flows."
                            ),
                            links=(
                                HomeAction(label="Health", url="/health"),
                                HomeAction(label="Swagger", url="/docs"),
                            ),
                        ),
                        HomeCard(
                            title="Core authorization",
                            status="Internal contract ready",
                            description=(
                                "Core command routes call /internal/auth/introspect to validate bearer tokens "
                                "and permissions such as books:write."
                            ),
                            links=(HomeAction(label="Core Swagger", url="http://localhost:8000/docs"),),
                        ),
                        HomeCard(
                            title="Project context",
                            status="Docs available",
                            description=(
                                "Architecture notes explain why Auth owns identity while Core owns business data "
                                "and only consumes authorization decisions."
                            ),
                            links=(
                                HomeAction(label="MkDocs PT-BR", url="http://localhost:8080"),
                                HomeAction(label="MkDocs EN", url="http://localhost:8081"),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )
