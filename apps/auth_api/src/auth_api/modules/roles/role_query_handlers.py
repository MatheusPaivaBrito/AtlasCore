from typing import Any
from uuid import UUID

from sqlalchemy import String, cast, or_, select
from sqlalchemy.orm import Session, selectinload

from auth_api.modules.roles.role_entity import RoleEntity
from auth_api.modules.roles.role_queries import GetRoleQuery, ListRolesQuery
from auth_api.shared.exceptions import AuthResourceNotFoundError


class RoleQueryHandler:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, query: GetRoleQuery) -> RoleEntity:
        return self.load_role(role_id=query.role_id, include_deleted=query.include_deleted)

    def list(self, query: ListRolesQuery) -> list[RoleEntity]:
        limit = max(1, min(query.limit, 100))
        offset = max(0, query.offset)
        statement = select(RoleEntity).options(selectinload(RoleEntity.permissions))
        statement = self._apply_soft_delete_scope(
            statement,
            include_deleted=query.include_deleted,
            only_deleted=query.only_deleted,
        )
        statement = self._apply_search(statement, query.q)
        statement = self._apply_filters(statement, query.filters)
        statement = statement.order_by(RoleEntity.code).offset(offset).limit(limit)
        return list(self.session.scalars(statement).all())

    def load_role(self, *, role_id: UUID, include_deleted: bool = False) -> RoleEntity:
        role = self.session.scalar(
            select(RoleEntity)
            .options(selectinload(RoleEntity.permissions))
            .where(RoleEntity.id == role_id)
            .limit(1)
        )
        if role is None:
            raise AuthResourceNotFoundError(entity="auth_roles", resource_id=role_id)
        if not include_deleted and role.deleted_at is not None:
            raise AuthResourceNotFoundError(entity="auth_roles", resource_id=role_id)
        return role

    @staticmethod
    def _apply_soft_delete_scope(
        statement: Any,
        *,
        include_deleted: bool,
        only_deleted: bool,
    ) -> Any:
        if only_deleted:
            return statement.where(RoleEntity.deleted_at.is_not(None))
        if include_deleted:
            return statement
        return statement.where(RoleEntity.deleted_at.is_(None))

    @staticmethod
    def _apply_search(statement: Any, q: str | None) -> Any:
        if not q:
            return statement
        like_value = f"%{q.strip()}%"
        if like_value == "%%":
            return statement
        return statement.where(
            or_(
                cast(RoleEntity.code, String).ilike(like_value),
                cast(RoleEntity.name, String).ilike(like_value),
            ),
        )

    @staticmethod
    def _apply_filters(statement: Any, filters: dict[str, str]) -> Any:
        code = filters.get("code")
        is_active = filters.get("is_active")

        if code:
            statement = statement.where(RoleEntity.code == code.strip().lower())
        if is_active is not None:
            statement = statement.where(RoleEntity.is_active == (is_active.lower() == "true"))

        return statement
