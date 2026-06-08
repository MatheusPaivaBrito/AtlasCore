from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from auth_api.modules.users.presentation.schemas import PermissionPayload, UserRead


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=180)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class LoginResponse(BaseModel):
    authenticated: bool = True
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    session_id: str
    permissions: list[PermissionPayload] = Field(default_factory=list)
    user: UserRead


class RefreshResponse(BaseModel):
    refreshed: bool = True
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    session_id: str


class LogoutResponse(BaseModel):
    logged_out: bool = True


class IntrospectionRequest(BaseModel):
    required_permission: PermissionPayload | None = Field(
        default=None,
        validation_alias=AliasChoices("required_permission", "permission"),
    )

    model_config = ConfigDict(populate_by_name=True)


class IntrospectionUser(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_superuser: bool
    token_version: int


class IntrospectionResponse(BaseModel):
    active: bool = True
    allowed: bool = True
    user: IntrospectionUser
    permissions: list[PermissionPayload] = Field(default_factory=list)
    required_permission: PermissionPayload | None = None
