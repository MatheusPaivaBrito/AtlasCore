from uuid import uuid4

from shared_kernel.time import DateTimeService


LOCAL_ACK_PROVIDER_NAME = "local_ack"


def local_ack_status(*, channel: str, provider_name: str, reason: str) -> dict:
    return {
        "name": provider_name,
        "channel": channel,
        "configured": False,
        "status": "not_configured",
        "mode": LOCAL_ACK_PROVIDER_NAME,
        "reason": reason,
    }


def local_ack_delivery(*, channel: str) -> dict:
    return {
        "accepted": True,
        "delivery_id": str(uuid4()),
        "channel": channel,
        "provider": LOCAL_ACK_PROVIDER_NAME,
        "provider_status": "not_configured",
        "mode": LOCAL_ACK_PROVIDER_NAME,
        "received_at": DateTimeService.utc_now().isoformat(),
    }
