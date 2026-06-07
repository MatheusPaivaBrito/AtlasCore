from uuid import UUID

from pydantic import BaseModel, Field

from core_api.modules.library.domains.shared import ReadSchema


class ShelfCreate(BaseModel):
    library_id: UUID
    name: str = Field(min_length=2, max_length=140)
    code: str = Field(min_length=2, max_length=40)


class ShelfUpdate(BaseModel):
    library_id: UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=140)
    code: str | None = Field(default=None, min_length=2, max_length=40)


class ShelfRead(ShelfCreate, ReadSchema):
    pass
