from pathlib import Path


def test_auth_users_are_verticalized() -> None:
    users_path = Path("apps/auth_api/src/auth_api/modules/users")
    expected_files = {
        "user_command_handlers.py",
        "user_commands.py",
        "user_entity.py",
        "user_queries.py",
        "user_query_handlers.py",
        "user_router.py",
        "user_schema.py",
    }

    assert expected_files.issubset({path.name for path in users_path.iterdir()})


def test_auth_roles_are_verticalized() -> None:
    roles_path = Path("apps/auth_api/src/auth_api/modules/roles")
    expected_files = {
        "role_command_handlers.py",
        "role_commands.py",
        "role_entity.py",
        "role_queries.py",
        "role_query_handlers.py",
        "role_router.py",
        "role_schema.py",
    }

    assert expected_files.issubset({path.name for path in roles_path.iterdir()})
