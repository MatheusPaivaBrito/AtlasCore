from starlette import status

from shared_kernel.errors import ApplicationError, ErrorTarget


class PublicAssetError(ApplicationError):
    code = "public_assets.error"
    message = "A public assets domain error occurred."


class UnsupportedAssetTypeError(PublicAssetError):
    status_code = status.HTTP_422_UNPROCESSABLE_CONTENT
    code = "public_assets.unsupported_asset_type"

    def __init__(self, *, asset_type: str) -> None:
        super().__init__(
            "Unsupported public asset type.",
            target=ErrorTarget(
                location="body",
                entity="public_assets",
                field="asset_type",
                payload={"asset_type": asset_type},
            ),
        )
