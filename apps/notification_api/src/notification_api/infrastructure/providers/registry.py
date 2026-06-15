from notification_api.infrastructure.providers.email import email_provider_status
from notification_api.infrastructure.providers.slack import slack_provider_status


def notification_channels() -> list[dict]:
    return [email_provider_status(), slack_provider_status()]
