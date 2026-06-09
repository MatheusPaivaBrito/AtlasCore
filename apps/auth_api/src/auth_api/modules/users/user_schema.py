from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PermissionPayload(BaseModel):
    domain: str = Field(min_length=2, max_length=100)
    action: str = Field(min_length=2, max_length=50)

    @field_validator("domain", "action")
    @classmethod
    def normalize_permission_value(cls, value: str) -> str:
        return value.strip().lower()

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    email: str = Field(min_length=5, max_length=180)
    full_name: str = Field(min_length=2, max_length=140)
    password: str = Field(min_length=8, max_length=128)
    is_active: bool = True
    is_superuser: bool = False
    permissions: list[PermissionPayload] = Field(default_factory=list)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserUpdate(BaseModel):
    email: str | None = Field(default=None, min_length=5, max_length=180)
    full_name: str | None = Field(default=None, min_length=2, max_length=140)
    password: str | None = Field(default=None, min_length=8, max_length=128)
    is_active: bool | None = None
    is_superuser: bool | None = None
    permissions: list[PermissionPayload] | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().lower()


class UserRead(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    email: str
    full_name: str
    is_active: bool
    is_superuser: bool
    token_version: int
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    last_login_user_agent: str | None = None
    permissions: list[PermissionPayload] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
