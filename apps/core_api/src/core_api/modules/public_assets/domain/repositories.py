from typing import Protocol
from uuid import UUID

from core_api.modules.public_assets.domain.entities import PublicAsset


class PublicAssetRepository(Protocol):
    def get(self, asset_id: UUID) -> PublicAsset | None:
        raise NotImplementedError

    def save(self, asset: PublicAsset) -> PublicAsset:
        raise NotImplementedError
