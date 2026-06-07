from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from core_api.modules.library.domains.shared import ReadSchema


class BookRentalCreate(BaseModel):
    reader_id: UUID
    book_id: UUID
    rented_at: datetime
    returned_at: datetime | None = None


class BookRentalUpdate(BaseModel):
    reader_id: UUID | None = None
    book_id: UUID | None = None
    rented_at: datetime | None = None
    returned_at: datetime | None = None


class BookRentalRead(BookRentalCreate, ReadSchema):
    pass
