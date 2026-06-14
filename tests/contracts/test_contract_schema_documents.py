from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest

ROOT_DIR = Path(__file__).resolve().parents[2]
SCHEMA_FILES = sorted((ROOT_DIR / "contracts").glob("**/*.schema.json"))


def iter_refs(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        ref = value.get("$ref")
        if isinstance(ref, str):
            yield ref

        for nested_value in value.values():
            yield from iter_refs(nested_value)

    if isinstance(value, list):
        for item in value:
            yield from iter_refs(item)


@pytest.mark.parametrize(
    "schema_path",
    SCHEMA_FILES,
    ids=lambda path: str(path.relative_to(ROOT_DIR)),
)
def test_contract_schema_documents_are_valid_json(schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"].startswith("https://atlascore.local/contracts/")
    assert schema["title"]
    assert schema["type"] == "object"


@pytest.mark.parametrize(
    "schema_path",
    SCHEMA_FILES,
    ids=lambda path: str(path.relative_to(ROOT_DIR)),
)
def test_contract_schema_local_refs_are_resolvable(schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    definitions = schema.get("$defs", {})

    for ref in iter_refs(schema):
        assert ref.startswith("#/$defs/")
        assert ref.removeprefix("#/$defs/") in definitions
