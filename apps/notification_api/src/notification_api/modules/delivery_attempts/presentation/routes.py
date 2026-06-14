from fastapi import APIRouter


router = APIRouter(prefix="/delivery-attempts", tags=["delivery_attempts"])


@router.get("/examples", summary="Show delivery attempt states")
def examples() -> dict:
    return {
        "states": [
            {
                "status": "accepted",
                "meaning": "Notification API received the request and returned a delivery id.",
            },
            {
                "status": "sent",
                "meaning": "A real provider confirmed delivery handoff.",
            },
            {
                "status": "failed",
                "meaning": "The provider rejected the request or could not be reached.",
            },
        ]
    }
