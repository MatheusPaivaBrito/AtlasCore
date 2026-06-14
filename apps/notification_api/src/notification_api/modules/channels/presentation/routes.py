from fastapi import APIRouter

from notification_api.infrastructure.providers import notification_channels


router = APIRouter(prefix="/channels", tags=["channels"])


@router.get("", summary="List notification channels")
def list_channels() -> dict:
    return {"channels": notification_channels()}


@router.get("/providers", summary="Show notification provider status")
def providers() -> dict:
    return {"providers": {channel["channel"]: channel for channel in notification_channels()}}
