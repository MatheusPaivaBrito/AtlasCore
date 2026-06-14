from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PermissionAction(StrEnum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"


class PermissionDomain(StrEnum):
    USERS = "users"
    ROLES = "roles"
    SESSIONS = "sessions"
    ACCESS_CONTROL = "access_control"
    LIBRARIES = "libraries"
    SHELVES = "shelves"
    SECTIONS = "sections"
    BOOKS = "books"
    READERS = "readers"
    RENTALS = "rentals"


@dataclass(frozen=True, slots=True)
class PermissionDefinition:
    domain: str
    action: str
    description: str

    @property
    def value(self) -> str:
        return f"{self.domain}:{self.action}"

    def as_payload(self) -> dict[str, str]:
        return {"domain": self.domain, "action": self.action}


def _enum_value(value: PermissionDomain | PermissionAction | str) -> str:
    if isinstance(value, PermissionDomain | PermissionAction):
        return value.value
    return value


def permission(domain: PermissionDomain | str, action: PermissionAction | str, description: str) -> PermissionDefinition:
    return PermissionDefinition(
        domain=_enum_value(domain),
        action=_enum_value(action),
        description=description,
    )


USERS_READ = permission(PermissionDomain.USERS, PermissionAction.READ, "Read Auth users.")
USERS_WRITE = permission(PermissionDomain.USERS, PermissionAction.WRITE, "Create, update or restore Auth users.")
USERS_DELETE = permission(PermissionDomain.USERS, PermissionAction.DELETE, "Soft-delete Auth users.")

ROLES_READ = permission(PermissionDomain.ROLES, PermissionAction.READ, "Read Auth roles.")
ROLES_WRITE = permission(PermissionDomain.ROLES, PermissionAction.WRITE, "Create, update or restore Auth roles.")
ROLES_DELETE = permission(PermissionDomain.ROLES, PermissionAction.DELETE, "Soft-delete Auth roles.")

SESSIONS_READ = permission(PermissionDomain.SESSIONS, PermissionAction.READ, "Read active Auth sessions.")
SESSIONS_DELETE = permission(PermissionDomain.SESSIONS, PermissionAction.DELETE, "Revoke active Auth sessions.")

ACCESS_CONTROL_READ = permission(
    PermissionDomain.ACCESS_CONTROL,
    PermissionAction.READ,
    "Read RBAC permission profiles.",
)
ACCESS_CONTROL_WRITE = permission(
    PermissionDomain.ACCESS_CONTROL,
    PermissionAction.WRITE,
    "Replace RBAC permission profiles.",
)

LIBRARIES_WRITE = permission(PermissionDomain.LIBRARIES, PermissionAction.WRITE, "Create, update or restore libraries.")
LIBRARIES_DELETE = permission(PermissionDomain.LIBRARIES, PermissionAction.DELETE, "Soft-delete libraries.")
SHELVES_WRITE = permission(PermissionDomain.SHELVES, PermissionAction.WRITE, "Create, update or restore shelves.")
SHELVES_DELETE = permission(PermissionDomain.SHELVES, PermissionAction.DELETE, "Soft-delete shelves.")
SECTIONS_WRITE = permission(PermissionDomain.SECTIONS, PermissionAction.WRITE, "Create, update or restore shelf sections.")
SECTIONS_DELETE = permission(PermissionDomain.SECTIONS, PermissionAction.DELETE, "Soft-delete shelf sections.")
BOOKS_WRITE = permission(PermissionDomain.BOOKS, PermissionAction.WRITE, "Create, update or restore books.")
BOOKS_DELETE = permission(PermissionDomain.BOOKS, PermissionAction.DELETE, "Soft-delete books.")
READERS_WRITE = permission(PermissionDomain.READERS, PermissionAction.WRITE, "Create, update or restore readers.")
READERS_DELETE = permission(PermissionDomain.READERS, PermissionAction.DELETE, "Soft-delete readers.")
RENTALS_WRITE = permission(PermissionDomain.RENTALS, PermissionAction.WRITE, "Create, update or restore rentals.")
RENTALS_DELETE = permission(PermissionDomain.RENTALS, PermissionAction.DELETE, "Soft-delete rentals.")


AUTH_ADMIN_PERMISSIONS = (
    USERS_READ,
    USERS_WRITE,
    USERS_DELETE,
    ROLES_READ,
    ROLES_WRITE,
    ROLES_DELETE,
    SESSIONS_READ,
    SESSIONS_DELETE,
    ACCESS_CONTROL_READ,
    ACCESS_CONTROL_WRITE,
)

CORE_COMMAND_PERMISSIONS = (
    LIBRARIES_WRITE,
    LIBRARIES_DELETE,
    SHELVES_WRITE,
    SHELVES_DELETE,
    SECTIONS_WRITE,
    SECTIONS_DELETE,
    BOOKS_WRITE,
    BOOKS_DELETE,
    READERS_WRITE,
    READERS_DELETE,
    RENTALS_WRITE,
    RENTALS_DELETE,
)

LIBRARIAN_PERMISSIONS = (
    BOOKS_WRITE,
    SHELVES_WRITE,
    SECTIONS_WRITE,
    READERS_WRITE,
    RENTALS_WRITE,
)

ATLAS_ADMIN_PERMISSIONS = AUTH_ADMIN_PERMISSIONS + CORE_COMMAND_PERMISSIONS

PERMISSION_CATALOG = tuple(
    sorted(
        {
            permission_definition.value: permission_definition
            for permission_definition in ATLAS_ADMIN_PERMISSIONS + LIBRARIAN_PERMISSIONS
        }.values(),
        key=lambda permission_definition: permission_definition.value,
    )
)
