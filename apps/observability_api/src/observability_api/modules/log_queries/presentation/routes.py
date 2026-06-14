from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from observability_api.infrastructure.providers import list_loki_labels, query_loki


router = APIRouter(prefix="/log-queries", tags=["log_queries"])


class LokiQueryResponse(BaseModel):
    query: str
    limit: int
    result: dict


@router.get("/labels", summary="List Loki labels")
def list_labels() -> dict:
    return {
        "provider": "loki",
        "result": list_loki_labels(),
    }


@router.get("/query", response_model=LokiQueryResponse, summary="Run an instant Loki query")
def run_query(
    query: str = Query(default='{service=~".+"}', min_length=1, max_length=500),
    limit: int = Query(default=20, ge=1, le=100),
) -> LokiQueryResponse:
    return LokiQueryResponse(
        query=query,
        limit=limit,
        result=query_loki(query, limit=limit),
    )


class LogQueryExample(BaseModel):
    description: str
    query: str = Field(min_length=1)


@router.get("/examples", response_model=list[LogQueryExample], summary="List useful Loki query examples")
def list_examples() -> list[LogQueryExample]:
    return [
        LogQueryExample(description="All logs carrying a service label.", query='{service=~".+"}'),
        LogQueryExample(description="Core API logs.", query='{service="core_api"}'),
        LogQueryExample(description="Auth API logs.", query='{service="auth_api"}'),
        LogQueryExample(description="Errors by level label.", query='{level=~"error|critical"}'),
    ]
