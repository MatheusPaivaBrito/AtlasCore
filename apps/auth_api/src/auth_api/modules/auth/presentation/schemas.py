from pydantic import BaseModel, Field, field_validator

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
