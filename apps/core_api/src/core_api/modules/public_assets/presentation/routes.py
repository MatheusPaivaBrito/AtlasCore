from fastapi import APIRouter

from core_api.modules.public_assets.application.dtos import PublicAssetsModelDescription
from core_api.modules.public_assets.application.use_cases import describe_public_assets_model


router = APIRouter(prefix="/public-assets", tags=["public-assets"])


@router.get("/model")
def get_public_assets_model() -> PublicAssetsModelDescription:
    return describe_public_assets_model()
