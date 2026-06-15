from dataclasses import dataclass
from typing import Any

from fastapi import Depends


def allow_anonymous() -> None:
    return None


@dataclass(frozen=True)
class CrudRouteGuards:
    create: Any | None = None
    list: Any | None = None
    get: Any | None = None
    update: Any | None = None
    delete: Any | None = None
    restore: Any | None = None


def resolve_guard(guard: Any | None) -> Any:
    if guard is not None:
        return guard
    return Depends(allow_anonymous)
