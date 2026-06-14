from uuid import UUID

from pydantic import BaseModel, Field

from auth_api.modules.users.user_schema import PermissionPayload, UserRoleRead


class AccessProfileRead(BaseModel):
    user_id: UUID
    is_superuser: bool
    roles: list[UserRoleRead] = Field(default_factory=list)
    direct_permissions: list[PermissionPayload] = Field(default_factory=list)
    permissions: list[PermissionPayload] = Field(default_factory=list)


class PermissionCatalogItemRead(BaseModel):
    value: str
    domain: str
    action: str
    description: str


class PermissionSyncRequest(BaseModel):
    permissions: list[PermissionPayload] = Field(default_factory=list)
