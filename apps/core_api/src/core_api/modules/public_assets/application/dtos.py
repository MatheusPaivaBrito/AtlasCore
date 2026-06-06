from pydantic import BaseModel


class PublicAssetsModelDescription(BaseModel):
    capability: str
    provider: str
    description: str
    public_use_cases: list[str]
