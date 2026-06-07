# Auth API Seeds

Auth API seeds will live here when `auth_api` starts owning its own database.

The future auth database should not reuse the Core API reader/user model. It should own identity and access-control data such as:

- users;
- credentials;
- sessions;
- roles;
- permissions;
- role assignments;
- refresh-token state;
- `token_version` for token invalidation;
- audit-safe metadata for security events.

This folder exists with documentation because the boundary is already known, but the executable seed should be added only when the Auth API has real persistence code.
