from fastapi import APIRouter

from core_api.modules.public_assets.application.dtos import PublicAssetsModelDescription
from core_api.modules.public_assets.application.use_cases import describe_public_assets_model


router = APIRouter(prefix="/public-assets")


@router.get("/model", tags=["public-assets: query"], summary="Describe the public assets module")
def get_public_assets_model() -> PublicAssetsModelDescription:
    return describe_public_assets_model()
