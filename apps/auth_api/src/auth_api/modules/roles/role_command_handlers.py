from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth_api.modules.access_control.application.permissions import sync_role_permissions
from auth_api.modules.roles.role_commands import CreateRoleCommand, DeleteRoleCommand, RestoreRoleCommand, UpdateRoleCommand
from auth_api.modules.roles.role_entity import RoleEntity
from auth_api.modules.roles.role_query_handlers import RoleQueryHandler
from auth_api.shared.exceptions import AuthResourceConflictError


class RoleCommandHandler:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.queries = RoleQueryHandler(session)

    def create(self, command: CreateRoleCommand) -> RoleEntity:
        payload = command.payload
        role = RoleEntity(
            code=payload.code,
            name=payload.name,
            description=payload.description,
            is_active=payload.is_active,
        )
        self._persist_role(role)
        sync_role_permissions(
            self.session,
            role_id=role.id,
            permissions=[permission.model_dump() for permission in payload.permissions],
        )
        return self.queries.load_role(role_id=role.id)

    def update(self, command: UpdateRoleCommand) -> RoleEntity:
        role = self.queries.load_role(role_id=command.role_id)
        values = command.payload.model_dump(exclude_unset=True)
        permissions = values.pop("permissions", None)

        for field_name, value in values.items():
            setattr(role, field_name, value)

        self._persist_role(role)
        if permissions is not None:
            sync_role_permissions(self.session, role_id=role.id, permissions=permissions)
        return self.queries.load_role(role_id=role.id)

    def delete(self, command: DeleteRoleCommand) -> None:
        role = self.queries.load_role(role_id=command.role_id)
        role.soft_delete()
        self._persist_role(role)

    def restore(self, command: RestoreRoleCommand) -> RoleEntity:
        role = self.queries.load_role(role_id=command.role_id, include_deleted=True)
        role.restore()
        return self._persist_role(role)

    def _persist_role(self, role: RoleEntity) -> RoleEntity:
        try:
            self.session.add(role)
            self.session.flush()
            self.session.refresh(role)
        except IntegrityError as exc:
            self.session.rollback()
            raise AuthResourceConflictError(entity="auth_roles", field="code") from exc
        return role
