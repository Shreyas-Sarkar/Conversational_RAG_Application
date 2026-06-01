"""Storage service for Supabase integration."""

import logging
from typing import Optional

from supabase import create_client, Client

try:
    from config.settings import get_settings
except ModuleNotFoundError:
    from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class StorageService:
    """Service to handle document storage in Supabase."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.client: Client = create_client(
            self.settings.SUPABASE_URL,
            self.settings.SUPABASE_KEY
        )
        self.bucket_name = "documents"
        logger.info("Initialized Supabase Storage Service")

    def upload_document(self, file_bytes: bytes, filename: str, document_id: str) -> Optional[str]:
        """
        Uploads a document to Supabase Storage and returns the public URL.
        """
        path_on_supase = f"{document_id}/{filename}"
        try:
            # Upload the file
            res = self.client.storage.from_(self.bucket_name).upload(
                path=path_on_supase,
                file=file_bytes,
                file_options={"content-type": "application/pdf"}
            )
            # Get the public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(path_on_supase)
            logger.info("Uploaded %s to Supabase. URL: %s", filename, public_url)
            return public_url
        except Exception as e:
            logger.error("Failed to upload document to Supabase: %s", e)
            raise ValueError(f"Storage upload failed: {str(e)}") from e

    def delete_document(self, filename: str, document_id: str) -> bool:
        """Deletes a document from Supabase Storage."""
        path_on_supase = f"{document_id}/{filename}"
        try:
            self.client.storage.from_(self.bucket_name).remove([path_on_supase])
            logger.info("Deleted %s from Supabase", path_on_supase)
            return True
        except Exception as e:
            logger.error("Failed to delete document from Supabase: %s", e)
            return False
