"""
S3-compatible storage client using boto3.

This module provides a reusable storage service that can be used across
multiple services for file operations with S3-compatible storage (AWS S3, MinIO, Wasabi, etc.).
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from checklists_service.config import settings

logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Base exception for storage operations."""



class StorageFileNotFoundError(StorageError):
    """Raised when a file is not found in storage."""



class StorageService:
    """
    S3-compatible storage service using boto3.

    Supports:
    - File upload/download/delete
    - Presigned URL generation for direct access
    - Bucket management
    - Automatic bucket creation on startup
    """

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region: str = "us-east-1",
        *,
        use_ssl: bool = False,
        secure_mode: bool = True,
    ) -> None:
        """
        Initialize storage service with S3 credentials.

        Args:
            endpoint: S3 endpoint URL (e.g., http://minio:9000 or https://s3.amazonaws.com)
            access_key: S3 access key
            secret_key: S3 secret key
            bucket_name: Default bucket name for operations
            region: S3 region (default: us-east-1)
            use_ssl: Whether to use SSL/TLS
            secure_mode: Whether to generate secure presigned URLs

        """
        self.bucket_name = bucket_name
        self.secure_mode = secure_mode
        self.endpoint = endpoint

        # Configure boto3 client for S3-compatible storage
        config = Config(
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=10,
            read_timeout=30,
        )

        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
            use_ssl=use_ssl,
            config=config,
        )

        # Thread pool for running sync boto3 operations
        self._executor = ThreadPoolExecutor(max_workers=4)

        # Ensure bucket exists
        self._ensure_bucket()

    def shutdown(self) -> None:
        """Shutdown the thread pool executor."""
        self._executor.shutdown(wait=True)

    def _ensure_bucket(self) -> None:
        """Create bucket if it doesn't exist (synchronous)."""
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
            logger.info("Bucket exists: %s", self.bucket_name)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code == "404":
                try:
                    self.client.create_bucket(Bucket=self.bucket_name)
                    logger.info("Created bucket: %s", self.bucket_name)
                except ClientError as create_error:
                    logger.error("Failed to create bucket %s: %s", self.bucket_name, create_error)
                    raise StorageError(f"Failed to initialize bucket: {create_error}") from create_error
            else:
                logger.error("Failed to check bucket %s: %s", self.bucket_name, e)
                raise StorageError(f"Failed to initialize bucket: {e}") from e

    async def upload_file(
        self,
        file_data: bytes | BytesIO,
        object_name: str,
        content_type: str | None = None,
        metadata: dict | None = None,
    ) -> str:
        """
        Upload a file to S3 storage.

        Args:
            file_data: File content as bytes or BytesIO
            object_name: Path/key for the object in the bucket
            content_type: MIME type of the file
            metadata: Additional metadata to store with the object

        Returns:
            The object name (key) of the uploaded file

        Raises:
            StorageError: If upload fails

        """
        try:
            if isinstance(file_data, bytes):
                file_stream = BytesIO(file_data)
            else:
                file_stream = file_data
                file_stream.seek(0)

            extra_args = {}
            if content_type:
                extra_args["ContentType"] = content_type
            if metadata:
                extra_args["Metadata"] = {k: str(v) for k, v in metadata.items()}  # type: ignore[dict-item]

            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.client.upload_fileobj(
                    file_stream, self.bucket_name, object_name, ExtraArgs=extra_args
                ),
            )

            logger.info("Uploaded file to s3://%s/%s", self.bucket_name, object_name)
            return object_name

        except ClientError as e:
            logger.error("Failed to upload file %s: %s", object_name, e)
            raise StorageError(f"Upload failed: {e}") from e

    async def download_file(self, object_name: str) -> BytesIO:
        """
        Download a file from S3 storage.

        Args:
            object_name: Path/key of the object in the bucket

        Returns:
            File content as BytesIO

        Raises:
            FileNotFoundError: If file doesn't exist
            StorageError: If download fails

        """
        try:
            buffer = BytesIO()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.client.download_fileobj(self.bucket_name, object_name, buffer),
            )
            buffer.seek(0)
            return buffer

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code in ("404", "NoSuchKey"):
                raise StorageFileNotFoundError(f"File not found: {object_name}") from e
            logger.error("Failed to download file %s: %s", object_name, e)
            raise StorageError(f"Download failed: {e}") from e

    async def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from S3 storage.

        Args:
            object_name: Path/key of the object to delete

        Returns:
            True if deleted, False if file didn't exist

        Raises:
            StorageError: If deletion fails for reasons other than not found

        """
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.client.delete_object(Bucket=self.bucket_name, Key=object_name),
            )
            logger.info("Deleted file s3://%s/%s", self.bucket_name, object_name)
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code in ("404", "NoSuchKey"):
                return False
            logger.error("Failed to delete file %s: %s", object_name, e)
            raise StorageError(f"Delete failed: {e}") from e

    async def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in storage.

        Args:
            object_name: Path/key to check

        Returns:
            True if file exists, False otherwise

        """
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.client.head_object(Bucket=self.bucket_name, Key=object_name),
            )
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            if error_code in ("404", "NoSuchKey"):
                return False
            raise

    def get_presigned_url(
        self,
        object_name: str,
        expires: int = 3600,
        method: str = "GET",
    ) -> str:
        """
        Generate a presigned URL for direct access to a file.

        Args:
            object_name: Path/key of the object
            expires: URL expiration time in seconds (default: 1 hour)
            method: HTTP method (GET for download, PUT for upload)

        Returns:
            Presigned URL string

        Raises:
            StorageError: If URL generation fails

        """
        try:
            client_method = f"{method.lower()}_object"

            url = self.client.generate_presigned_url(
                ClientMethod=client_method,
                Params={"Bucket": self.bucket_name, "Key": object_name},
                ExpiresIn=expires,
            )

            # For non-secure mode (local development), convert HTTPS to HTTP
            if not self.secure_mode and url.startswith("https://"):
                url = url.replace("https://", "http://", 1)

            return url

        except ClientError as e:
            logger.error("Failed to generate presigned URL for %s: %s", object_name, e)
            raise StorageError(f"URL generation failed: {e}") from e

    def get_public_url(self, object_name: str) -> str:
        """
        Get the public URL for an object (requires bucket to be public).

        Args:
            object_name: Path/key of the object

        Returns:
            Public URL string

        """
        # Parse endpoint to construct URL
        if self.endpoint.startswith("http://"):
            base = self.endpoint[7:]
            scheme = "http"
        elif self.endpoint.startswith("https://"):
            base = self.endpoint[8:]
            scheme = "https"
        else:
            base = self.endpoint
            scheme = "https" if self.secure_mode else "http"

        return f"{scheme}://{base}/{self.bucket_name}/{object_name}"


# Global storage instance (initialized on first use)
_storage_instance: StorageService | None = None


def get_storage_service(bucket_name: str | None = None) -> StorageService:
    """
    Get or create the storage service singleton.

    Args:
        bucket_name: Optional bucket name override (uses default from config if not provided)

    Returns:
        StorageService instance

    """
    global _storage_instance

    if _storage_instance is None:
        _storage_instance = StorageService(
            endpoint=settings.S3_ENDPOINT,
            access_key=settings.S3_ACCESS_KEY,
            secret_key=settings.S3_SECRET_KEY,
            bucket_name=bucket_name or settings.CHECKLISTS_S3_BUCKET,
            region=settings.S3_REGION,
            use_ssl=settings.S3_USE_SSL,
            secure_mode=settings.S3_SECURE_MODE,
        )

    return _storage_instance


# Dependency injection helper
async def get_storage() -> StorageService:
    """FastAPI dependency for storage service."""
    return get_storage_service()


def shutdown_storage() -> None:
    """Shutdown the global storage instance. Call this on application shutdown."""
    global _storage_instance
    if _storage_instance is not None:
        _storage_instance.shutdown()
        _storage_instance = None
