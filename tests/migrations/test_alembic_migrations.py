from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
CORE_PYTHONPATH = "apps/core_api/src:packages/shared_kernel/src"
AUTH_PYTHONPATH = "apps/auth_api/src:packages/shared_kernel/src"


def run_alembic(
    *args: str,
    pythonpath: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    process = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=ROOT_DIR,
        env={
            **os.environ,
            "PYTHONPATH": pythonpath,
            **(env or {}),
        },
        text=True,
        capture_output=True,
        check=False,
    )

    assert process.returncode == 0, process.stdout + process.stderr
    return process


def test_auth_migrations_upgrade_to_head_on_sqlite(tmp_path: Path) -> None:
    db_path = tmp_path / "atlas_auth.db"

    run_alembic(
        "-c",
        "apps/auth_api/alembic.ini",
        "upgrade",
        "head",
        pythonpath=AUTH_PYTHONPATH,
        env={"AUTH_DATABASE_URL": f"sqlite+pysqlite:///{db_path}"},
    )

    assert db_path.exists()


def test_core_migrations_generate_postgres_offline_sql() -> None:
    result = run_alembic(
        "-c",
        "apps/core_api/alembic.ini",
        "upgrade",
        "head",
        "--sql",
        pythonpath=CORE_PYTHONPATH,
        env={"CORE_DATABASE_URL": "postgresql+psycopg://atlas:atlas@localhost:5432/atlas_core"},
    )

    assert "CREATE TABLE library_libraries" in result.stdout
    assert "library_sections" in result.stdout
    assert "fk_library_books_section_id_library_sections" in result.stdout


def test_core_alembic_history_has_single_head() -> None:
    result = run_alembic(
        "-c",
        "apps/core_api/alembic.ini",
        "heads",
        pythonpath=CORE_PYTHONPATH,
    )

    assert result.stdout.count("(head)") == 1
    assert "20260606_0002" in result.stdout


def test_auth_alembic_history_has_single_head() -> None:
    result = run_alembic(
        "-c",
        "apps/auth_api/alembic.ini",
        "heads",
        pythonpath=AUTH_PYTHONPATH,
    )

    assert result.stdout.count("(head)") == 1
    assert "20260607_0003" in result.stdout
