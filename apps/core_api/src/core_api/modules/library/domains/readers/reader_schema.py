from pydantic import BaseModel, Field

from core_api.modules.library.domains.shared import ReadSchema


class ReaderCreate(BaseModel):
    name: str = Field(min_length=2, max_length=140)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=180)


class ReaderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=140)
    email: str | None = Field(default=None, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", max_length=180)


class ReaderRead(ReaderCreate, ReadSchema):
    pass
