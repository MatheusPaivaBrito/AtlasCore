from uuid import UUID

from pydantic import BaseModel, Field

from auth_api.modules.users.presentation.schemas import PermissionPayload


class AccessProfileRead(BaseModel):
    user_id: UUID
    is_superuser: bool
    permissions: list[PermissionPayload] = Field(default_factory=list)


class PermissionSyncRequest(BaseModel):
    permissions: list[PermissionPayload] = Field(default_factory=list)
