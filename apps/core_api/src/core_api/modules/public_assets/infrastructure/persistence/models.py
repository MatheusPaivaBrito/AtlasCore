from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from core_api.infrastructure.database.base import BaseModel


class PublicAssetModel(BaseModel):
    __tablename__ = "public_assets"

    filename: Mapped[str] = mapped_column(String(180), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    public_url: Mapped[str] = mapped_column(String(600), nullable=False)
    provider: Mapped[str] = mapped_column(String(80), nullable=False, default="google_cloud_storage")
    object_key: Mapped[str] = mapped_column(String(400), unique=True, index=True, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
