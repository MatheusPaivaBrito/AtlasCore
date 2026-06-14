from uuid import uuid4

from notification_api.infrastructure.settings import settings
from shared_kernel.time import DateTimeService


def email_provider_status() -> dict:
    configured = bool(settings.SENDGRID_API_KEY)
    return {
        "name": "sendgrid",
        "channel": "email",
        "configured": configured,
        "status": "configured" if configured else "not_configured",
        "mode": "provider_ready" if configured else "local_ack",
        "reason": None if configured else "Set NOTIFICATION_SENDGRID_API_KEY to send real emails.",
    }


def slack_provider_status() -> dict:
    configured = bool(settings.SLACK_WEBHOOK_URL)
    return {
        "name": "slack",
        "channel": "slack",
        "configured": configured,
        "status": "configured" if configured else "not_configured",
        "mode": "provider_ready" if configured else "local_ack",
        "reason": None if configured else "Set NOTIFICATION_SLACK_WEBHOOK_URL to send real Slack messages.",
    }


def notification_channels() -> list[dict]:
    return [email_provider_status(), slack_provider_status()]


def accept_email_notification(payload: dict) -> dict:
    provider = email_provider_status()
    return {
        "accepted": True,
        "delivery_id": str(uuid4()),
        "channel": "email",
        "provider": provider["name"] if provider["configured"] else "local_ack",
        "provider_status": provider["status"],
        "mode": provider["mode"],
        "to": payload["to"],
        "from_email": payload.get("from_email") or settings.DEFAULT_EMAIL_FROM,
        "subject": payload["subject"],
        "received_at": DateTimeService.utc_now().isoformat(),
    }


def accept_slack_notification(payload: dict) -> dict:
    provider = slack_provider_status()
    return {
        "accepted": True,
        "delivery_id": str(uuid4()),
        "channel": "slack",
        "provider": provider["name"] if provider["configured"] else "local_ack",
        "provider_status": provider["status"],
        "mode": provider["mode"],
        "target": payload.get("channel") or settings.SLACK_DEFAULT_CHANNEL or "default",
        "received_at": DateTimeService.utc_now().isoformat(),
    }
