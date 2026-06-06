class GoogleCloudStorageClient:
    """Adapter placeholder for Google Cloud Storage public assets."""

    def build_public_url(self, bucket_name: str, object_key: str) -> str:
        return f"https://storage.googleapis.com/{bucket_name}/{object_key}"
