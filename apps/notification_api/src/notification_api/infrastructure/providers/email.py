from notification_api.infrastructure.providers.local_ack import local_ack_delivery, local_ack_status
from notification_api.infrastructure.settings import settings


EMAIL_CHANNEL = "email"
SENDGRID_PROVIDER_NAME = "sendgrid"


def email_provider_status() -> dict:
    if settings.SENDGRID_API_KEY:
        return {
            "name": SENDGRID_PROVIDER_NAME,
            "channel": EMAIL_CHANNEL,
            "configured": True,
            "status": "configured",
            "mode": "provider_ready",
            "reason": None,
        }

    return local_ack_status(
        channel=EMAIL_CHANNEL,
        provider_name=SENDGRID_PROVIDER_NAME,
        reason="Set NOTIFICATION_SENDGRID_API_KEY to send real emails.",
    )


def accept_email_notification(payload: dict) -> dict:
    provider = email_provider_status()
    delivery = local_ack_delivery(channel=EMAIL_CHANNEL)

    if provider["configured"]:
        delivery["provider"] = provider["name"]
        delivery["provider_status"] = provider["status"]
        delivery["mode"] = provider["mode"]

    delivery.update(
        {
            "to": payload["to"],
            "from_email": payload.get("from_email") or settings.DEFAULT_EMAIL_FROM,
            "subject": payload["subject"],
        }
    )
    return delivery
