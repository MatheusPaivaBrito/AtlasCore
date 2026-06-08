from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from auth_api.infrastructure.database.connection import SessionLocal
from auth_api.modules.access_control.application.permissions import sync_user_permissions
from auth_api.modules.auth.application.passwords import hash_password
from auth_api.modules.users.domain.user_entity import UserCredentialEntity, UserEntity


@dataclass
class SeedStats:
    created: int = 0
    updated: int = 0
    restored: int = 0


def _restore_if_needed(user: UserEntity, stats: SeedStats) -> None:
    if user.deleted_at is not None:
        user.restore()
        stats.restored += 1


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
    return user


def seed_auth_users(session: Session) -> SeedStats:
    stats = SeedStats()

    _upsert_user(
        session,
        email="admin@atlas.local",
        full_name="Atlas Admin",
        password="AtlasAdmin123!",
        is_active=True,
        is_superuser=True,
        permissions=[
            {"domain": "users", "action": "read"},
            {"domain": "users", "action": "write"},
            {"domain": "users", "action": "delete"},
            {"domain": "sessions", "action": "read"},
            {"domain": "sessions", "action": "delete"},
            {"domain": "access_control", "action": "read"},
            {"domain": "access_control", "action": "write"},
        ],
        stats=stats,
    )
    _upsert_user(
        session,
        email="librarian@atlas.local",
        full_name="Atlas Librarian",
        password="AtlasUser123!",
        is_active=True,
        is_superuser=False,
        permissions=[
            {"domain": "users", "action": "read"},
            {"domain": "sessions", "action": "read"},
        ],
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
        f"created={stats.created}, updated={stats.updated}, restored={stats.restored}"
    )


if __name__ == "__main__":
    main()
