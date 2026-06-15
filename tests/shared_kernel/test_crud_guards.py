from fastapi import Depends
from fastapi.params import Depends as DependsParam

from shared_kernel.http.crud.guards import allow_anonymous, resolve_guard


def test_resolve_guard_preserves_explicit_fastapi_dependency() -> None:
    def dependency() -> str:
        return "authorized"

    guard = Depends(dependency)

    assert resolve_guard(guard) is guard


def test_resolve_guard_defaults_to_anonymous_dependency() -> None:
    guard = resolve_guard(None)

    assert isinstance(guard, DependsParam)
    assert guard.dependency is allow_anonymous
