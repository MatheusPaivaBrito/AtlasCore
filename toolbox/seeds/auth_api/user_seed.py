from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from auth_api.infrastructure.database.connection import SessionLocal
from auth_api.modules.access_control.application.permissions import sync_role_permissions, sync_user_permissions, sync_user_roles
from auth_api.modules.access_control.domain.permissions import ATLAS_ADMIN_PERMISSIONS, LIBRARIAN_PERMISSIONS
from auth_api.modules.auth.application.passwords import hash_password
from auth_api.modules.roles.role_entity import RoleEntity
from auth_api.modules.users.user_entity import UserCredentialEntity, UserEntity


@dataclass
class SeedStats:
    created: int = 0
    updated: int = 0
    restored: int = 0
    roles_created: int = 0
    roles_updated: int = 0


def _restore_if_needed(user: UserEntity, stats: SeedStats) -> None:
    if user.deleted_at is not None:
        user.restore()
        stats.restored += 1


def _upsert_role(
    session: Session,
    *,
    code: str,
    name: str,
    description: str,
    permissions: list[dict[str, str]],
    stats: SeedStats,
) -> RoleEntity:
    role = session.scalar(select(RoleEntity).where(RoleEntity.code == code).limit(1))

    if role is None:
        role = RoleEntity(
            code=code,
            name=name,
            description=description,
            is_active=True,
        )
        session.add(role)
        stats.roles_created += 1
    else:
        role.name = name
        role.description = description
        role.is_active = True
        _restore_if_needed(role, stats)
        stats.roles_updated += 1

    session.flush()
    sync_role_permissions(session, role_id=role.id, permissions=permissions)
    return role


def _upsert_user(
    session: Session,
    *,
    email: str,
    full_name: str,
    password: str,
    is_active: bool,
    is_superuser: bool,
    permissions: list[dict[str, str]],
    stats: SeedStats,
    roles: list[RoleEntity] | None = None,
) -> UserEntity:
    user = session.scalar(select(UserEntity).where(UserEntity.email == email).limit(1))

    if user is None:
        user = UserEntity(
            email=email,
            full_name=full_name,
            is_active=is_active,
            is_superuser=is_superuser,
            token_version=1,
        )
        user.credential = UserCredentialEntity(password_hash=hash_password(password))
        session.add(user)
        stats.created += 1
    else:
        user.full_name = full_name
        user.is_active = is_active
        user.is_superuser = is_superuser
        _restore_if_needed(user, stats)
        stats.updated += 1

        if user.credential is None:
            user.credential = UserCredentialEntity(password_hash=hash_password(password))
        else:
            user.credential.password_hash = hash_password(password)

    session.flush()
    sync_user_permissions(session, user_id=user.id, permissions=permissions)
    sync_user_roles(session, user_id=user.id, role_ids=[role.id for role in roles or []])
    return user


def seed_auth_users(session: Session) -> SeedStats:
    stats = SeedStats()
    admin_role = _upsert_role(
        session,
        code="atlas_admin",
        name="Atlas Admin",
        description="Full Auth and Core administration role.",
        permissions=[permission.as_payload() for permission in ATLAS_ADMIN_PERMISSIONS],
        stats=stats,
    )
    librarian_role = _upsert_role(
        session,
        code="librarian",
        name="Librarian",
        description="Library catalog operation role.",
        permissions=[permission.as_payload() for permission in LIBRARIAN_PERMISSIONS],
        stats=stats,
    )

    _upsert_user(
        session,
        email="admin@atlas.local",
        full_name="Atlas Admin",
        password="AtlasAdmin123!",
        is_active=True,
        is_superuser=True,
        permissions=[],
        roles=[admin_role],
        stats=stats,
    )
    _upsert_user(
        session,
        email="librarian@atlas.local",
        full_name="Atlas Librarian",
        password="AtlasUser123!",
        is_active=True,
        is_superuser=False,
        permissions=[],
        roles=[librarian_role],
        stats=stats,
    )
    _upsert_user(
        session,
        email="blocked@atlas.local",
        full_name="Blocked Atlas User",
        password="AtlasBlocked123!",
        is_active=False,
        is_superuser=False,
        permissions=[],
        roles=[],
        stats=stats,
    )

    return stats


def main() -> None:
    session = SessionLocal()

    try:
        stats = seed_auth_users(session)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print(
        "Auth user seed completed: "
        f"created={stats.created}, updated={stats.updated}, restored={stats.restored}, "
        f"roles_created={stats.roles_created}, roles_updated={stats.roles_updated}"
    )


if __name__ == "__main__":
    main()
