# Auth API Seeds

`auth_api` owns the identity database (`atlas_auth`).

Current executable seed:

```bash
make seed-auth
```

The seed creates demo users with bcrypt-hashed passwords in:

- `auth_users`;
- `auth_user_credentials`.

Known local credentials:

| E-mail | Password | Notes |
| --- | --- | --- |
| `admin@atlas.local` | `AtlasAdmin123!` | Superuser demo account. |
| `librarian@atlas.local` | `AtlasUser123!` | Active product user. |
| `blocked@atlas.local` | `AtlasBlocked123!` | Inactive account for login tests. |

The Auth database should not reuse the Core API reader/user model. Core readers are business actors inside the library domain; Auth users are identities that can authenticate.
