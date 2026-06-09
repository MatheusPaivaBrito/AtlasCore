from uuid import UUID

from pydantic import BaseModel, Field

from auth_api.modules.users.user_schema import PermissionPayload


class AccessProfileRead(BaseModel):
    user_id: UUID
    is_superuser: bool
    permissions: list[PermissionPayload] = Field(default_factory=list)


class PermissionCatalogItemRead(BaseModel):
    value: str
    domain: str
    action: str
    description: str


class PermissionSyncRequest(BaseModel):
    permissions: list[PermissionPayload] = Field(default_factory=list)
