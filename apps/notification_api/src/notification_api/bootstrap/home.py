from fastapi import APIRouter, Request

from notification_api.infrastructure.providers import email_provider_status, slack_provider_status
from shared_kernel.http import HomeAction, HomeCard, HomePage, HomeSection, render_service_home


router = APIRouter(include_in_schema=False)


def _provider_card(provider: dict) -> HomeCard:
    configured = bool(provider["configured"])
    return HomeCard(
        title=f"{provider['channel'].title()} provider",
        description=provider["reason"] or f"{provider['name']} is configured for real delivery.",
        status=f"{provider['name']} {'configured' if configured else 'local ack'}",
        available=configured,
        code=provider["mode"],
    )


@router.get("/")
def home(request: Request):
    email_provider = email_provider_status()
    slack_provider = slack_provider_status()

    return render_service_home(
        request=request,
        page=HomePage(
            service_name="AtlasCore Notification API",
            eyebrow="FastAPI - Notifications - Email - Slack",
            description=(
                "Notification boundary for AtlasCore. It accepts e-mail and Slack delivery requests, "
                "keeps provider configuration isolated, and can run in local acknowledgement mode while "
                "real providers are not configured."
            ),
            actions=(
                HomeAction(label="Open Swagger Docs", url="/docs", primary=True),
                HomeAction(label="Open ReDoc", url="/redoc"),
                HomeAction(label="Channels", url="/channels"),
                HomeAction(label="AtlasCore Home", url="http://localhost:8000"),
            ),
            sections=(
                HomeSection(
                    title="Notification channels",
                    description=(
                        "The API exposes channel readiness separately from delivery endpoints so clients can "
                        "see whether calls will use a real provider or local acknowledgement."
                    ),
                    columns=2,
                    cards=(
                        _provider_card(email_provider),
                        _provider_card(slack_provider),
                    ),
                ),
                HomeSection(
                    title="Useful routes",
                    description="Small contracts for testing notification flows before real provider wiring.",
                    columns=3,
                    cards=(
                        HomeCard(
                            title="Email delivery",
                            status="POST /notifications/email",
                            description="Accepts recipient, subject, body and optional metadata.",
                            links=(HomeAction(label="Swagger", url="/docs#/notifications/send_email_notifications_email_post"),),
                        ),
                        HomeCard(
                            title="Slack delivery",
                            status="POST /notifications/slack",
                            description="Accepts message, optional channel and metadata.",
                            links=(HomeAction(label="Swagger", url="/docs#/notifications/send_slack_notifications_slack_post"),),
                        ),
                        HomeCard(
                            title="Templates",
                            status="Examples available",
                            description="Lists template examples for auth, library and operational notifications.",
                            links=(HomeAction(label="Examples", url="/templates/examples"),),
                        ),
                    ),
                ),
            ),
        ),
    )
