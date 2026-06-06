from uuid import UUID

from sqlalchemy.orm import Session

from core_api.modules.public_assets.domain.entities import PublicAsset
from core_api.modules.public_assets.domain.repositories import PublicAssetRepository


class SqlAlchemyPublicAssetRepository(PublicAssetRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, asset_id: UUID) -> PublicAsset | None:
        raise NotImplementedError

    def save(self, asset: PublicAsset) -> PublicAsset:
        raise NotImplementedError
