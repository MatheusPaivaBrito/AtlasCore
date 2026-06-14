from fastapi import APIRouter
from pydantic import BaseModel, Field

from notification_api.infrastructure.providers import accept_email_notification, accept_slack_notification
from notification_api.shared.service_auth import require_notification_sender
from shared_kernel.security import ServiceToken


router = APIRouter(prefix="/notifications", tags=["notifications"])


class EmailNotificationCreate(BaseModel):
    to: str = Field(min_length=3, max_length=320)
    subject: str = Field(min_length=2, max_length=180)
    body: str = Field(min_length=1, max_length=10_000)
    from_email: str | None = Field(default=None, max_length=320)
    metadata: dict = Field(default_factory=dict)


class SlackNotificationCreate(BaseModel):
    message: str = Field(min_length=1, max_length=4_000)
    channel: str | None = Field(default=None, max_length=120)
    metadata: dict = Field(default_factory=dict)


class NotificationAccepted(BaseModel):
    accepted: bool = True
    delivery_id: str
    channel: str
    provider: str
    provider_status: str
    mode: str
    received_at: str


class EmailNotificationAccepted(NotificationAccepted):
    to: str
    from_email: str
    subject: str


class SlackNotificationAccepted(NotificationAccepted):
    target: str


@router.post("/email", response_model=EmailNotificationAccepted, summary="Send or accept an email notification")
def send_email(payload: EmailNotificationCreate, service_token: ServiceToken = require_notification_sender) -> dict:
    return accept_email_notification(payload.model_dump())


@router.post("/slack", response_model=SlackNotificationAccepted, summary="Send or accept a Slack notification")
def send_slack(payload: SlackNotificationCreate, service_token: ServiceToken = require_notification_sender) -> dict:
    return accept_slack_notification(payload.model_dump())
