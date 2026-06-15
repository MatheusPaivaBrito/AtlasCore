from notification_api.infrastructure.providers.local_ack import local_ack_delivery, local_ack_status
from notification_api.infrastructure.settings import settings


SLACK_CHANNEL = "slack"
SLACK_PROVIDER_NAME = "slack"


def slack_provider_status() -> dict:
    if settings.SLACK_WEBHOOK_URL:
        return {
            "name": SLACK_PROVIDER_NAME,
            "channel": SLACK_CHANNEL,
            "configured": True,
            "status": "configured",
            "mode": "provider_ready",
            "reason": None,
        }

    return local_ack_status(
        channel=SLACK_CHANNEL,
        provider_name=SLACK_PROVIDER_NAME,
        reason="Set NOTIFICATION_SLACK_WEBHOOK_URL to send real Slack messages.",
    )


def accept_slack_notification(payload: dict) -> dict:
    provider = slack_provider_status()
    delivery = local_ack_delivery(channel=SLACK_CHANNEL)

    if provider["configured"]:
        delivery["provider"] = provider["name"]
        delivery["provider_status"] = provider["status"]
        delivery["mode"] = provider["mode"]

    delivery["target"] = payload.get("channel") or settings.SLACK_DEFAULT_CHANNEL or "default"
    return delivery
