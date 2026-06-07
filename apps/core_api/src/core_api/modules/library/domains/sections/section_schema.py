from uuid import UUID

from pydantic import BaseModel, Field

from core_api.modules.library.domains.shared import ReadSchema


class ShelfSectionCreate(BaseModel):
    shelf_id: UUID
    name: str = Field(min_length=2, max_length=140)
    code: str = Field(min_length=2, max_length=40)


class ShelfSectionUpdate(BaseModel):
    shelf_id: UUID | None = None
    name: str | None = Field(default=None, min_length=2, max_length=140)
    code: str | None = Field(default=None, min_length=2, max_length=40)


class ShelfSectionRead(ShelfSectionCreate, ReadSchema):
    pass
