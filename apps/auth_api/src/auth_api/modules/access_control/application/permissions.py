from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from auth_api.modules.access_control.domain.permission_entity import UserPermissionEntity
from auth_api.modules.access_control.domain.permissions import PermissionDefinition
from auth_api.modules.roles.role_entity import RoleEntity, RolePermissionEntity, UserRoleEntity
from auth_api.modules.users.user_entity import UserEntity
from auth_api.shared.exceptions import AuthResourceNotFoundError


PermissionInput = dict[str, str] | PermissionDefinition


def normalize_permission(permission: PermissionInput) -> dict[str, str]:
    if isinstance(permission, PermissionDefinition):
        permission = permission.as_payload()

    return {
        "domain": permission["domain"].strip().lower(),
        "action": permission["action"].strip().lower(),
    }


def serialize_user_permissions(user: UserEntity) -> list[dict[str, str]]:
    permissions = {
        (permission.domain, permission.action)
        for permission in (user.permissions or [])
        if permission.deleted_at is None
    }

    for role_link in user.role_links or []:
        role = role_link.role
        if (
            role_link.deleted_at is not None
            or role is None
            or role.deleted_at is not None
            or not role.is_active
        ):
            continue

        permissions.update(
            (permission.domain, permission.action)
            for permission in (role.permissions or [])
            if permission.deleted_at is None
        )

    return [
        {"domain": domain, "action": action}
        for domain, action in sorted(permissions)
    ]


def serialize_user_direct_permissions(user: UserEntity) -> list[dict[str, str]]:
    permissions = [
        {"domain": permission.domain, "action": permission.action}
        for permission in (user.permissions or [])
        if permission.deleted_at is None
    ]
    return sorted(permissions, key=lambda item: (item["domain"], item["action"]))


def serialize_role_permissions(role: RoleEntity) -> list[dict[str, str]]:
    permissions = [
        {"domain": permission.domain, "action": permission.action}
        for permission in (role.permissions or [])
        if permission.deleted_at is None
    ]
    return sorted(permissions, key=lambda item: (item["domain"], item["action"]))


def serialize_user_roles(user: UserEntity) -> list[dict[str, str]]:
    roles = [
        {
            "id": role_link.role.id,
            "code": role_link.role.code,
            "name": role_link.role.name,
        }
        for role_link in (user.role_links or [])
        if role_link.deleted_at is None
        and role_link.role is not None
        and role_link.role.deleted_at is None
        and role_link.role.is_active
    ]
    return sorted(roles, key=lambda item: item["code"])


def user_has_permission(user: UserEntity, *, domain: str, action: str) -> bool:
    if user.is_superuser:
        return True

    expected = normalize_permission({"domain": domain, "action": action})
    return expected in serialize_user_permissions(user)


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
    user = session.get(UserEntity, user_id)
    if user is not None:
        session.expire(user, ["permissions"])


def sync_role_permissions(
    session: Session,
    *,
    role_id: UUID,
    permissions: Iterable[PermissionInput],
) -> None:
    session.execute(delete(RolePermissionEntity).where(RolePermissionEntity.role_id == role_id))

    normalized_permissions = {
        (permission["domain"], permission["action"])
        for permission in (normalize_permission(permission) for permission in permissions)
    }

    for domain, action in sorted(normalized_permissions):
        session.add(
            RolePermissionEntity(
                role_id=role_id,
                domain=domain,
                action=action,
            )
        )

    session.flush()
    role = session.get(RoleEntity, role_id)
    if role is not None:
        session.expire(role, ["permissions"])


def sync_user_roles(
    session: Session,
    *,
    user_id: UUID,
    role_ids: Iterable[UUID],
) -> None:
    unique_role_ids = set(role_ids)

    if unique_role_ids:
        existing_role_ids = set(
            session.scalars(
                select(RoleEntity.id).where(
                    RoleEntity.id.in_(unique_role_ids),
                    RoleEntity.deleted_at.is_(None),
                )
            ).all()
        )
        missing_role_ids = unique_role_ids - existing_role_ids
        if missing_role_ids:
            raise AuthResourceNotFoundError(entity="auth_roles", resource_id=sorted(missing_role_ids, key=str)[0])

    session.execute(delete(UserRoleEntity).where(UserRoleEntity.user_id == user_id))

    for role_id in sorted(unique_role_ids, key=str):
        session.add(UserRoleEntity(user_id=user_id, role_id=role_id))

    session.flush()
    user = session.get(UserEntity, user_id)
    if user is not None:
        session.expire(user, ["role_links"])


def load_user_permissions(session: Session, *, user_id: UUID) -> list[UserPermissionEntity]:
    statement = (
        select(UserEntity)
        .options(
            selectinload(UserEntity.permissions),
            selectinload(UserEntity.role_links).selectinload(UserRoleEntity.role).selectinload(RoleEntity.permissions),
        )
        .where(UserEntity.id == user_id)
        .limit(1)
    )
    user = session.scalar(statement)
    if user is None:
        return []
    return [permission for permission in user.permissions if permission.deleted_at is None]
