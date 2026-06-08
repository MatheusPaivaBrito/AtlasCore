from uuid import UUID

from pydantic import BaseModel, Field


class RequiredPermission(BaseModel):
    domain: str
    action: str


class AuthorizedUser(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_superuser: bool
    token_version: int


class AuthIntrospectionResponse(BaseModel):
    active: bool
    allowed: bool
    user: AuthorizedUser
    permissions: list[RequiredPermission] = Field(default_factory=list)
    required_permission: RequiredPermission | None = None
