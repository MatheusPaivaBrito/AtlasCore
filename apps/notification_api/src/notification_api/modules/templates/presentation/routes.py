from fastapi import APIRouter


router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/examples", summary="List notification template examples")
def examples() -> dict:
    return {
        "templates": [
            {
                "key": "auth.password_recovery",
                "channel": "email",
                "subject": "Password recovery",
                "variables": ["user_name", "recovery_url", "expires_in_minutes"],
            },
            {
                "key": "library.book_reserved",
                "channel": "email",
                "subject": "Book reservation confirmed",
                "variables": ["reader_name", "book_title", "pickup_deadline"],
            },
            {
                "key": "ops.incident_created",
                "channel": "slack",
                "subject": "Incident created",
                "variables": ["service", "level", "trace_id"],
            },
        ]
    }
