from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from auth_api.modules.users.user_schema import PermissionPayload


class RoleCreate(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=2, max_length=140)
    description: str | None = Field(default=None, max_length=300)
    is_active: bool = True
    permissions: list[PermissionPayload] = Field(default_factory=list)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().lower().replace(" ", "_")


class RoleUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=2, max_length=80)
    name: str | None = Field(default=None, min_length=2, max_length=140)
    description: str | None = Field(default=None, max_length=300)
    is_active: bool | None = None
    permissions: list[PermissionPayload] | None = None

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower().replace(" ", "_")


class RoleRead(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    code: str
    name: str
    description: str | None = None
    is_active: bool
    permissions: list[PermissionPayload] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class RoleSyncRequest(BaseModel):
    role_ids: list[UUID] = Field(default_factory=list)


class RolePermissionSyncRequest(BaseModel):
    permissions: list[PermissionPayload] = Field(default_factory=list)
