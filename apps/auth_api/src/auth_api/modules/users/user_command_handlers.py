from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth_api.modules.access_control.application.permissions import sync_user_permissions
from auth_api.modules.auth.application.password_policy import password_policy
from auth_api.modules.auth.application.passwords import hash_password
from auth_api.modules.sessions.application.service import SessionService
from auth_api.modules.users.user_commands import (
    CreateUserCommand,
    DeleteUserCommand,
    RestoreUserCommand,
    UpdateUserCommand,
)
from auth_api.modules.users.user_entity import UserCredentialEntity, UserEntity
from auth_api.modules.users.user_query_handlers import UserQueryHandler
from auth_api.modules.users.user_schema import UserCreate, UserUpdate
from auth_api.shared.exceptions import AuthResourceConflictError


class UserCommandHandler:
    def __init__(self, session: Session, session_service: SessionService | None = None) -> None:
        self.session = session
        self.session_service = session_service
        self.queries = UserQueryHandler(session)

    def create(self, command: CreateUserCommand) -> UserEntity:
        payload = command.payload
        password_policy.validate(payload.password)
        user = UserEntity(
            email=payload.email,
            full_name=payload.full_name,
            is_active=payload.is_active,
            is_superuser=payload.is_superuser,
            token_version=1,
        )
        user.credential = UserCredentialEntity(password_hash=hash_password(payload.password))
        self._persist_user(user)
        sync_user_permissions(
            self.session,
            user_id=user.id,
            permissions=self._permissions_payload(payload) or [],
        )
        return self.queries.load_user(user_id=user.id)

    def update(self, command: UpdateUserCommand) -> UserEntity:
        user = self.queries.load_user(user_id=command.user_id)
        values = command.payload.model_dump(exclude_unset=True)
        password = values.pop("password", None)
        permissions = values.pop("permissions", None)

        for field_name, value in values.items():
            setattr(user, field_name, value)

        if password is not None:
            password_policy.validate(password)
            if user.credential is None:
                user.credential = UserCredentialEntity(password_hash=hash_password(password))
            else:
                user.credential.password_hash = hash_password(password)
            user.token_version += 1
            self._delete_user_sessions(user)

        self._persist_user(user)
        if permissions is not None:
            sync_user_permissions(self.session, user_id=user.id, permissions=permissions)
        return self.queries.load_user(user_id=user.id)

    def delete(self, command: DeleteUserCommand) -> None:
        user = self.queries.load_user(user_id=command.user_id)
        user.soft_delete()
        user.token_version += 1
        self._persist_user(user)
        self._delete_user_sessions(user)

    def restore(self, command: RestoreUserCommand) -> UserEntity:
        user = self.queries.load_user(user_id=command.user_id, include_deleted=True)
        user.restore()
        return self._persist_user(user)

    def _persist_user(self, user: UserEntity) -> UserEntity:
        try:
            self.session.add(user)
            self.session.flush()
            self.session.refresh(user)
        except IntegrityError as exc:
            self.session.rollback()
            raise AuthResourceConflictError(entity="auth_users", field="email") from exc
        return user

    def _delete_user_sessions(self, user: UserEntity) -> None:
        if self.session_service is not None:
            self.session_service.delete_all_sessions(user_id=user.id)

    @staticmethod
    def _permissions_payload(payload: UserCreate | UserUpdate) -> list[dict[str, str]] | None:
        permissions = getattr(payload, "permissions", None)
        if permissions is None:
            return None
        return [permission.model_dump() for permission in permissions]
