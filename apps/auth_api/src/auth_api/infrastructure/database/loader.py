# ------------------------------------
# Auth Domain Entities (ORM Registration)
# ------------------------------------
from auth_api.modules.access_control.domain.permission_entity import UserPermissionEntity
from auth_api.modules.users.domain.user_entity import UserCredentialEntity, UserEntity

__all__ = ["UserCredentialEntity", "UserEntity", "UserPermissionEntity"]
