from typing import Any
from uuid import UUID

from sqlalchemy import String, cast, or_, select
from sqlalchemy.orm import Session, selectinload

from auth_api.modules.users.user_entity import UserEntity
from auth_api.modules.users.user_queries import GetUserQuery, ListUsersQuery
from auth_api.shared.exceptions import AuthResourceNotFoundError


class UserQueryHandler:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, query: GetUserQuery) -> UserEntity:
        return self.load_user(user_id=query.user_id, include_deleted=query.include_deleted)

    def list(self, query: ListUsersQuery) -> list[UserEntity]:
        limit = max(1, min(query.limit, 100))
        offset = max(0, query.offset)
        statement = select(UserEntity).options(selectinload(UserEntity.permissions))
        statement = self._apply_soft_delete_scope(
            statement,
            include_deleted=query.include_deleted,
            only_deleted=query.only_deleted,
        )
        statement = self._apply_search(statement, query.q)
        statement = self._apply_filters(statement, query.filters)
        statement = statement.order_by(UserEntity.email).offset(offset).limit(limit)
        return list(self.session.scalars(statement).all())

    def load_user(self, *, user_id: UUID, include_deleted: bool = False) -> UserEntity:
        user = self.session.scalar(
            select(UserEntity)
            .options(selectinload(UserEntity.credential), selectinload(UserEntity.permissions))
            .where(UserEntity.id == user_id)
            .limit(1)
        )
        if user is None:
            raise AuthResourceNotFoundError(entity="auth_users", resource_id=user_id)
        if not include_deleted and user.deleted_at is not None:
            raise AuthResourceNotFoundError(entity="auth_users", resource_id=user_id)
        return user

    @staticmethod
    def _apply_soft_delete_scope(
        statement: Any,
        *,
        include_deleted: bool,
        only_deleted: bool,
    ) -> Any:
        if only_deleted:
            return statement.where(UserEntity.deleted_at.is_not(None))
        if include_deleted:
            return statement
        return statement.where(UserEntity.deleted_at.is_(None))

    @staticmethod
    def _apply_search(statement: Any, q: str | None) -> Any:
        if not q:
            return statement
        like_value = f"%{q.strip()}%"
        if like_value == "%%":
            return statement
        return statement.where(
            or_(
                cast(UserEntity.email, String).ilike(like_value),
                cast(UserEntity.full_name, String).ilike(like_value),
            ),
        )

    @staticmethod
    def _apply_filters(statement: Any, filters: dict[str, str]) -> Any:
        email = filters.get("email")
        is_active = filters.get("is_active")
        is_superuser = filters.get("is_superuser")

        if email:
            statement = statement.where(UserEntity.email == email.strip().lower())
        if is_active is not None:
            statement = statement.where(UserEntity.is_active == (is_active.lower() == "true"))
        if is_superuser is not None:
            statement = statement.where(UserEntity.is_superuser == (is_superuser.lower() == "true"))

        return statement
