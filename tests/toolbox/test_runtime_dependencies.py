from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_runtime_checks() -> ModuleType:
    root = Path(__file__).resolve().parents[2]
    module_path = root / "toolbox" / "checks" / "ensure_runtime_dependencies.py"
    spec = importlib.util.spec_from_file_location("ensure_runtime_dependencies", module_path)
    assert spec
    assert spec.loader

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_service_runtime_dependency_contracts() -> None:
    checks = _load_runtime_checks()

    assert checks.SERVICE_DEPENDENCIES["core_api"] == ("core_postgres", "core_redis")
    assert checks.SERVICE_DEPENDENCIES["auth_api"] == ("auth_postgres", "auth_redis")
    assert checks.SERVICE_DEPENDENCIES["eventing_api"] == ("eventing_postgres", "kafka")
    assert checks.SERVICE_DEPENDENCIES["notification_api"] == ("notification_redis",)
    assert checks.SERVICE_DEPENDENCIES["observability_api"] == ("loki", "grafana")


def test_all_dependencies_are_deduplicated_in_stable_order() -> None:
    checks = _load_runtime_checks()

    dependencies = checks._dependencies_for("all")

    assert [dependency.key for dependency in dependencies] == [
        "core_postgres",
        "core_redis",
        "auth_postgres",
        "auth_redis",
        "eventing_postgres",
        "kafka",
        "notification_redis",
        "loki",
        "grafana",
    ]


def test_compose_services_are_deduplicated_in_stable_order() -> None:
    checks = _load_runtime_checks()
    dependencies = (
        checks.DEPENDENCIES["loki"],
        checks.DEPENDENCIES["grafana"],
        checks.DEPENDENCIES["auth_postgres"],
    )

    assert checks._compose_services_for(dependencies) == ["loki", "grafana", "postgres"]
