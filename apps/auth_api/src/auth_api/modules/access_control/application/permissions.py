from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from auth_api.modules.access_control.domain.permission_entity import UserPermissionEntity
from auth_api.modules.access_control.domain.permissions import PermissionDefinition
from auth_api.modules.users.user_entity import UserEntity


PermissionInput = dict[str, str] | PermissionDefinition


def normalize_permission(permission: PermissionInput) -> dict[str, str]:
    if isinstance(permission, PermissionDefinition):
        permission = permission.as_payload()

    return {
        "domain": permission["domain"].strip().lower(),
        "action": permission["action"].strip().lower(),
    }


def serialize_user_permissions(user: UserEntity) -> list[dict[str, str]]:
    permissions = [
        {"domain": permission.domain, "action": permission.action}
        for permission in (user.permissions or [])
        if permission.deleted_at is None
    ]
    return sorted(permissions, key=lambda item: (item["domain"], item["action"]))


def user_has_permission(user: UserEntity, *, domain: str, action: str) -> bool:
    if user.is_superuser:
        return True

    expected = normalize_permission({"domain": domain, "action": action})
    return any(
        permission.deleted_at is None
        and permission.domain == expected["domain"]
        and permission.action == expected["action"]
        for permission in (user.permissions or [])
    )


def sync_user_permissions(
    session: Session,
    *,
    user_id: UUID,
    permissions: Iterable[PermissionInput],
) -> None:
    session.execute(delete(UserPermissionEntity).where(UserPermissionEntity.user_id == user_id))

    normalized_permissions = {
        (permission["domain"], permission["action"])
        for permission in (normalize_permission(permission) for permission in permissions)
    }

    for domain, action in sorted(normalized_permissions):
        session.add(
            UserPermissionEntity(
                user_id=user_id,
                domain=domain,
                action=action,
            )
        )

    session.flush()


def load_user_permissions(session: Session, *, user_id: UUID) -> list[UserPermissionEntity]:
    statement = (
        select(UserEntity)
        .options(selectinload(UserEntity.permissions))
        .where(UserEntity.id == user_id)
        .limit(1)
    )
    user = session.scalar(statement)
    if user is None:
        return []
    return [permission for permission in user.permissions if permission.deleted_at is None]
