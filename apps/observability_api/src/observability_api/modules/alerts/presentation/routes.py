from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertRule(BaseModel):
    code: str
    description: str
    provider: str
    enabled: bool = True


class AlertEvent(BaseModel):
    service: str = Field(min_length=2, max_length=80)
    rule_code: str = Field(min_length=2, max_length=80)
    severity: str = Field(default="warning", pattern="^(info|warning|error|critical)$")
    message: str = Field(min_length=3, max_length=300)


@router.get("/rules", response_model=list[AlertRule], summary="List default alert rules")
def list_rules() -> list[AlertRule]:
    return [
        AlertRule(
            code="api_error_rate",
            description="Error rate increased for one API.",
            provider="grafana",
        ),
        AlertRule(
            code="provider_unavailable",
            description="An observability provider is unavailable.",
            provider="observability_api",
        ),
    ]


@router.post("/events", summary="Accept an alert event")
def accept_alert_event(payload: AlertEvent) -> dict:
    return {
        "accepted": True,
        "service": payload.service,
        "rule_code": payload.rule_code,
        "severity": payload.severity,
    }
