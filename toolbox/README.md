# AtlasCore Toolbox

`toolbox/` stores operational and development scripts that are useful during local work, demos and manual maintenance.

This folder is intentionally separate from `tests/`.

- `tests/` contains automated assertions that should run in CI.
- `toolbox/` contains scripts that mutate local state, inspect the project or help prepare demos.

## Current Structure

```text
toolbox/
  checks/
  scripts/
  seeds/
    auth_api/
    core_api/
```

## Seeds

Seeds are grouped by API because each API can own a different database.

Current seed:

```bash
make seed-core
```

This populates the Core API library schema with mocked libraries, shelves, sections, books, readers and rentals.

Future Auth API seeds should live under:

```text
toolbox/seeds/auth_api/
```

The Auth API will eventually own identity data such as users, roles, permissions, sessions, refresh-token state and `token_version`.
