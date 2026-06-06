from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True)
class PublicAsset:
    filename: str
    content_type: str
    public_url: str
    provider: str
    object_key: str
    size_bytes: int
    id: UUID | None = None
