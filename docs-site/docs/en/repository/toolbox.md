# Toolbox

`toolbox/` is the place for scripts that help local development, demos and manual maintenance.

It is separate from `tests/`.

- `tests/` should be deterministic and CI-safe.
- `toolbox/` may mutate local data, inspect running containers or prepare demo state.

## Structure

```text
toolbox/
  checks/
  scripts/
  seeds/
    auth_api/
    core_api/
```

## Seeds

Seeds are grouped by service because each service can own a different database.

Current executable seed:

```bash
make seed-core
```

This runs:

```text
toolbox/seeds/core_api/library_seed.py
```

It creates mocked data for:

- libraries;
- shelves;
- sections;
- books;
- readers;
- rental history.

The seed is idempotent and uses natural keys such as `library.code`, `book.isbn` and `reader.email`.

## Auth API Direction

`toolbox/seeds/auth_api/` documents the future Auth seed boundary.

When Auth persistence exists, it should seed identity and access-control data such as:

- users;
- credentials;
- roles;
- permissions;
- role assignments;
- sessions;
- refresh-token state;
- `token_version`.

Auth data should not be mixed with Core reader data. The Auth API will own identity; Core will own business reader/customer concepts when needed.
