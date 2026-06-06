from core_api.modules.public_assets.application.dtos import PublicAssetsModelDescription


def describe_public_assets_model() -> PublicAssetsModelDescription:
    return PublicAssetsModelDescription(
        capability="public_assets",
        provider="google_cloud_storage",
        description="Public images and documents are modeled as core assets; Google Cloud Storage is only an infrastructure provider.",
        public_use_cases=[
            "store public image metadata",
            "store public document metadata",
            "resolve public asset URLs",
            "hide bucket/provider details behind an adapter",
        ],
    )
