# Toolbox

`toolbox/` is the place for scripts that help local development, demos and manual maintenance.

It is separate from `tests/`.

- `tests/` should be deterministic and CI-safe.
- `toolbox/` may mutate local data, inspect running containers or prepare demo state.

## Structure

```text
toolbox/
  checks/
  security/
  scripts/
  seeds/
    auth_api/
    core_api/
```

## Seeds

Seeds are grouped by service because each service can own a different database.

Current executable seeds:

```bash
make seed-core
make seed-auth
make seed-all
```

Core seed:

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

Auth seed:

```text
toolbox/seeds/auth_api/user_seed.py
```

- users;
- credentials;
- `token_version`;
- permissions.

The seed creates:

| E-mail | State | Permissions |
| --- | --- | --- |
| `admin@atlas.local` | Active, superuser | `users:*`, `sessions:*`, `access_control:*`. |
| `librarian@atlas.local` | Active | `users:read`, `sessions:read`. |
| `blocked@atlas.local` | Inactive | None. |

Sessions and refresh tokens are not seeded because they are runtime state. They are created in Redis when a user logs in.

Auth data should not be mixed with Core reader data. The Auth API will own identity; Core will own business reader/customer concepts when needed.

## Service Tokens

`toolbox/security/create_service_token.py` creates short-lived service JWTs for manual local testing.

Default command:

```bash
make service-token
```

This generates a token with:

```text
sub = core_api
aud = notification_api
scope = notifications:send
```

Override the caller:

```bash
make service-token SUBJECT=auth_api
```

Paste the generated token into Insomnia/Postman as:

```http
Authorization: Bearer <token>
```
