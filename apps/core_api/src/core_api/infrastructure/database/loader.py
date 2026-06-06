# Import persistence models here so Alembic can discover metadata.
from core_api.modules.library.infrastructure.persistence.models import (
    BookModel,
    BookRentalModel,
    LibraryModel,
    ReaderModel,
    ShelfModel,
    ShelfSectionModel,
)
from core_api.modules.public_assets.infrastructure.persistence.models import PublicAssetModel

__all__ = [
    "BookModel",
    "BookRentalModel",
    "LibraryModel",
    "PublicAssetModel",
    "ReaderModel",
    "ShelfModel",
    "ShelfSectionModel",
]
