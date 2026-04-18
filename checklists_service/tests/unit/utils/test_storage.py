"""Unit tests for S3 storage service."""

from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from checklists_service.utils.storage import (
    FileNotFoundError,
    StorageError,
    StorageService,
    get_storage_service,
)


class TestStorageServiceInit:
    """Test storage service initialization."""

    def test_init_creates_client(self) -> None:
        """Test initialization creates boto3 client."""
        with patch("boto3.client") as mock_boto_client, \
             patch("checklists_service.utils.storage.ThreadPoolExecutor"):

            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            mock_client.head_bucket.return_value = None  # Bucket exists

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
            )

            assert service.bucket_name == "test-bucket"
            assert service.endpoint == "http://minio:9000"
            mock_boto_client.assert_called_once()

    def test_init_creates_bucket_if_not_exists(self) -> None:
        """Test bucket is created if it doesn't exist."""
        with patch("boto3.client") as mock_boto_client, \
             patch("checklists_service.utils.storage.ThreadPoolExecutor"):

            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client

            # First call (head_bucket) returns 404, second call (create_bucket) succeeds
            error_response = {"Error": {"Code": "404"}}
            mock_client.head_bucket.side_effect = ClientError(error_response, "HeadBucket")
            mock_client.create_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
            )

            mock_client.create_bucket.assert_called_once_with(Bucket="test-bucket")

    def test_init_raises_on_bucket_create_failure(self) -> None:
        """Test StorageError is raised when bucket creation fails."""
        with patch("boto3.client") as mock_boto_client, \
             patch("checklists_service.utils.storage.ThreadPoolExecutor"):

            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client

            # head_bucket returns 404
            head_error = {"Error": {"Code": "404"}}
            mock_client.head_bucket.side_effect = ClientError(head_error, "HeadBucket")

            # create_bucket fails with different error
            create_error = {"Error": {"Code": "500", "Message": "Internal error"}}
            mock_client.create_bucket.side_effect = ClientError(create_error, "CreateBucket")

            with pytest.raises(StorageError, match="Failed to initialize bucket"):
                StorageService(
                    endpoint="http://minio:9000",
                    access_key="test-key",
                    secret_key="test-secret",
                    bucket_name="test-bucket",
                )

    def test_init_raises_on_head_bucket_failure(self) -> None:
        """Test StorageError is raised when head_bucket fails with non-404 error."""
        with patch("boto3.client") as mock_boto_client, \
             patch("checklists_service.utils.storage.ThreadPoolExecutor"):

            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client

            error_response = {"Error": {"Code": "403", "Message": "Access denied"}}
            mock_client.head_bucket.side_effect = ClientError(error_response, "HeadBucket")

            with pytest.raises(StorageError, match="Failed to initialize bucket"):
                StorageService(
                    endpoint="http://minio:9000",
                    access_key="test-key",
                    secret_key="test-secret",
                    bucket_name="test-bucket",
                )


class TestStorageServiceUpload:
    """Test file upload."""

    @pytest.fixture
    def mock_service(self):
        """Create a storage service with mocked boto3 client."""
        with patch("boto3.client") as mock_boto_client, \
             patch("checklists_service.utils.storage.ThreadPoolExecutor"):

            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
                region="us-east-1",
            )
            service.client = mock_client

            yield service

    async def test_upload_file_bytes(self, mock_service: StorageService) -> None:
        """Test uploading bytes (lines 130-149)."""
        mock_service.client.upload_fileobj = MagicMock()

        # Mock the executor to run synchronously using async mock
        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            result = await mock_service.upload_file(
                file_data=b"test content",
                object_name="test/file.txt",
                content_type="text/plain",
                metadata={"key": "value"},
            )

        assert result == "test/file.txt"

    async def test_upload_file_bytesio(self, mock_service: StorageService) -> None:
        """Test uploading BytesIO (lines 130-149)."""
        mock_service.client.upload_fileobj = MagicMock()
        buffer = BytesIO(b"test content")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            result = await mock_service.upload_file(
                file_data=buffer,
                object_name="test/file.txt",
                content_type="text/plain",
            )

        assert result == "test/file.txt"

    async def test_upload_file_raises_on_error(self, mock_service: StorageService) -> None:
        """Test StorageError is raised on upload failure (lines 154-156)."""
        error_response = {"Error": {"Code": "500", "Message": "Internal error"}}
        mock_service.client.upload_fileobj.side_effect = ClientError(error_response, "Upload")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            with pytest.raises(StorageError, match="Upload failed"):
                await mock_service.upload_file(
                    file_data=b"test content",
                    object_name="test/file.txt",
                )


class TestStorageServiceDownload:
    """Test file download."""

    @pytest.fixture
    def mock_service(self):
        """Create a storage service with mocked boto3 client."""
        with patch("boto3.client") as mock_boto_client, \
             patch("checklists_service.utils.storage.ThreadPoolExecutor"):

            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
            )
            service.client = mock_client

            yield service

    async def test_download_file_success(self, mock_service: StorageService) -> None:
        """Test successful download (lines 171-178)."""
        def mock_download(bucket, key, buffer):
            buffer.write(b"file content")

        mock_service.client.download_fileobj = mock_download

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            result = await mock_service.download_file("test/file.txt")

        content = result.read()
        assert content == b"file content"

    async def test_download_file_not_found_404(self, mock_service: StorageService) -> None:
        """Test FileNotFoundError on 404 (lines 181-184)."""
        error_response = {"Error": {"Code": "404"}}
        mock_service.client.download_fileobj.side_effect = ClientError(error_response, "Download")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            with pytest.raises(FileNotFoundError, match="File not found"):
                await mock_service.download_file("test/file.txt")

    async def test_download_file_not_found_nosuchkey(self, mock_service: StorageService) -> None:
        """Test FileNotFoundError on NoSuchKey (lines 181-184)."""
        error_response = {"Error": {"Code": "NoSuchKey"}}
        mock_service.client.download_fileobj.side_effect = ClientError(error_response, "Download")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            with pytest.raises(FileNotFoundError, match="File not found"):
                await mock_service.download_file("test/file.txt")

    async def test_download_file_storage_error(self, mock_service: StorageService) -> None:
        """Test StorageError on other errors (lines 185-186)."""
        error_response = {"Error": {"Code": "500", "Message": "Internal error"}}
        mock_service.client.download_fileobj.side_effect = ClientError(error_response, "Download")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            with pytest.raises(StorageError, match="Download failed"):
                await mock_service.download_file("test/file.txt")


class TestStorageServiceDelete:
    """Test file deletion."""

    @pytest.fixture
    def mock_service(self):
        """Create a storage service with mocked boto3 client."""
        with patch("boto3.client") as mock_boto_client, \
             patch("checklists_service.utils.storage.ThreadPoolExecutor"):

            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
            )
            service.client = mock_client

            yield service

    async def test_delete_file_success(self, mock_service: StorageService) -> None:
        """Test successful deletion (lines 200-207)."""
        mock_service.client.delete_object = MagicMock()

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            result = await mock_service.delete_file("test/file.txt")

        assert result is True
        mock_service.client.delete_object.assert_called_once_with(Bucket="test-bucket", Key="test/file.txt")

    async def test_delete_file_not_found_returns_false(self, mock_service: StorageService) -> None:
        """Test False returned when file not found 404 (lines 209-212)."""
        error_response = {"Error": {"Code": "404"}}
        mock_service.client.delete_object.side_effect = ClientError(error_response, "Delete")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            result = await mock_service.delete_file("test/file.txt")

        assert result is False

    async def test_delete_file_not_found_nosuchkey(self, mock_service: StorageService) -> None:
        """Test False returned when file not found NoSuchKey (lines 209-212)."""
        error_response = {"Error": {"Code": "NoSuchKey"}}
        mock_service.client.delete_object.side_effect = ClientError(error_response, "Delete")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            result = await mock_service.delete_file("test/file.txt")

        assert result is False

    async def test_delete_file_raises_on_error(self, mock_service: StorageService) -> None:
        """Test StorageError raised on other errors (lines 213-214)."""
        error_response = {"Error": {"Code": "500", "Message": "Internal error"}}
        mock_service.client.delete_object.side_effect = ClientError(error_response, "Delete")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            with pytest.raises(StorageError, match="Delete failed"):
                await mock_service.delete_file("test/file.txt")


class TestStorageServiceFileExists:
    """Test file existence check."""

    @pytest.fixture
    def mock_service(self):
        """Create a storage service with mocked boto3 client."""
        with patch("boto3.client") as mock_boto_client, \
             patch("checklists_service.utils.storage.ThreadPoolExecutor"):

            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
            )
            service.client = mock_client

            yield service

    async def test_file_exists_true(self, mock_service: StorageService) -> None:
        """Test True when file exists (lines 225-226)."""
        mock_service.client.head_object = MagicMock()

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            result = await mock_service.file_exists("test/file.txt")

        assert result is True

    async def test_file_exists_false_404(self, mock_service: StorageService) -> None:
        """Test False when file not found 404 (lines 232-235)."""
        error_response = {"Error": {"Code": "404"}}
        mock_service.client.head_object.side_effect = ClientError(error_response, "HeadObject")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            result = await mock_service.file_exists("test/file.txt")

        assert result is False

    async def test_file_exists_false_nosuchkey(self, mock_service: StorageService) -> None:
        """Test False when file not found NoSuchKey (lines 232-235)."""
        error_response = {"Error": {"Code": "NoSuchKey"}}
        mock_service.client.head_object.side_effect = ClientError(error_response, "HeadObject")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            result = await mock_service.file_exists("test/file.txt")

        assert result is False

    async def test_file_exists_raises_on_other_error(self, mock_service: StorageService) -> None:
        """Test exception is raised for other errors (lines 236)."""
        error_response = {"Error": {"Code": "500", "Message": "Internal error"}}
        mock_service.client.head_object.side_effect = ClientError(error_response, "HeadObject")

        async def mock_run_in_executor(executor, func, *args):
            return func(*args)

        with patch("asyncio.get_event_loop") as mock_loop:
            mock_loop.return_value.run_in_executor = mock_run_in_executor

            with pytest.raises(ClientError):
                await mock_service.file_exists("test/file.txt")


class TestStorageServicePresignedUrl:
    """Test presigned URL generation."""

    @pytest.fixture
    def mock_service(self):
        """Create a storage service with mocked boto3 client."""
        with patch("boto3.client") as mock_boto_client, \
             patch("checklists_service.utils.storage.ThreadPoolExecutor"):

            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
            )
            service.client = mock_client

            yield service

    def test_get_presigned_url_success(self, mock_service: StorageService) -> None:
        """Test successful URL generation (lines 257-270)."""
        mock_service.client.generate_presigned_url.return_value = "http://minio:9000/test/file.txt?token=abc"

        result = mock_service.get_presigned_url("test/file.txt", expires=3600)

        assert "test/file.txt" in result
        mock_service.client.generate_presigned_url.assert_called_once()

    def test_get_presigned_url_converts_https_to_http_in_non_secure_mode(self, mock_service: StorageService) -> None:
        """Test HTTPS is converted to HTTP in non-secure mode (lines 267-269)."""
        mock_service.secure_mode = False
        mock_service.client.generate_presigned_url.return_value = "https://minio:9000/test/file.txt?token=abc"

        result = mock_service.get_presigned_url("test/file.txt")

        assert result.startswith("http://")
        assert not result.startswith("https://")

    def test_get_presigned_url_raises_on_error(self, mock_service: StorageService) -> None:
        """Test StorageError raised on failure (lines 272-274)."""
        error_response = {"Error": {"Code": "500", "Message": "Internal error"}}
        mock_service.client.generate_presigned_url.side_effect = ClientError(error_response, "GenerateURL")

        with pytest.raises(StorageError, match="URL generation failed"):
            mock_service.get_presigned_url("test/file.txt")

    def test_get_presigned_url_with_put_method(self, mock_service: StorageService) -> None:
        """Test URL generation with PUT method."""
        mock_service.client.generate_presigned_url.return_value = "http://minio:9000/test/file.txt?token=abc"

        result = mock_service.get_presigned_url("test/file.txt", method="PUT")

        call_args = mock_service.client.generate_presigned_url.call_args
        assert call_args.kwargs["ClientMethod"] == "put_object"


class TestStorageServicePublicUrl:
    """Test public URL generation."""

    @pytest.fixture
    def mock_service(self):
        """Create a storage service with mocked boto3 client."""
        with patch("boto3.client") as mock_boto_client, \
             patch("checklists_service.utils.storage.ThreadPoolExecutor"):

            mock_client = MagicMock()
            mock_boto_client.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
            )

            yield service

    def test_get_public_url_http_endpoint(self, mock_service: StorageService) -> None:
        """Test public URL with HTTP endpoint (lines 286-296)."""
        result = mock_service.get_public_url("test/file.txt")

        assert result == "http://minio:9000/test-bucket/test/file.txt"

    def test_get_public_url_https_endpoint(self, mock_service: StorageService) -> None:
        """Test public URL with HTTPS endpoint (lines 290-296)."""
        mock_service.endpoint = "https://s3.amazonaws.com"
        mock_service.secure_mode = True

        result = mock_service.get_public_url("test/file.txt")

        assert result == "https://s3.amazonaws.com/test-bucket/test/file.txt"

    def test_get_public_url_no_scheme(self, mock_service: StorageService) -> None:
        """Test public URL with endpoint without scheme (lines 292-296)."""
        mock_service.endpoint = "s3.amazonaws.com"
        mock_service.secure_mode = True

        result = mock_service.get_public_url("test/file.txt")

        assert result == "https://s3.amazonaws.com/test-bucket/test/file.txt"

    def test_get_public_url_non_secure_mode_no_scheme(self, mock_service: StorageService) -> None:
        """Test public URL with non-secure mode and no scheme (lines 293-296)."""
        mock_service.endpoint = "minio:9000"
        mock_service.secure_mode = False

        result = mock_service.get_public_url("test/file.txt")

        assert result == "http://minio:9000/test-bucket/test/file.txt"


class TestGetStorageService:
    """Test get_storage_service singleton."""

    def test_get_storage_service_singleton(self) -> None:
        """Test that get_storage_service returns a singleton."""
        with patch("checklists_service.utils.storage.StorageService") as mock_storage_class:
            mock_instance = MagicMock()
            mock_storage_class.return_value = mock_instance

            # Reset the singleton
            import checklists_service.utils.storage as storage_module
            storage_module._storage_instance = None

            with patch("checklists_service.config.settings") as mock_settings:
                mock_settings.S3_ENDPOINT = "http://minio:9000"
                mock_settings.S3_ACCESS_KEY = "key"
                mock_settings.S3_SECRET_KEY = "secret"
                mock_settings.S3_REGION = "us-east-1"
                mock_settings.S3_USE_SSL = False
                mock_settings.CHECKLISTS_S3_BUCKET = "checklists"
                mock_settings.S3_PRESIGNED_URL_EXPIRY = 3600

                result1 = get_storage_service()
                result2 = get_storage_service()

                assert result1 is result2
                mock_storage_class.assert_called_once()

    def test_get_storage_service_with_custom_bucket(self) -> None:
        """Test get_storage_service with custom bucket."""
        with patch("checklists_service.utils.storage.StorageService") as mock_storage_class:
            mock_instance = MagicMock()
            mock_storage_class.return_value = mock_instance

            # Reset the singleton
            import checklists_service.utils.storage as storage_module
            storage_module._storage_instance = None

            with patch("checklists_service.config.settings") as mock_settings:
                mock_settings.S3_ENDPOINT = "http://minio:9000"
                mock_settings.S3_ACCESS_KEY = "key"
                mock_settings.S3_SECRET_KEY = "secret"
                mock_settings.S3_REGION = "us-east-1"
                mock_settings.S3_USE_SSL = False
                mock_settings.CHECKLISTS_S3_BUCKET = "checklists"

                result = get_storage_service(bucket_name="custom-bucket")

                assert result is mock_instance
                # Should use the provided bucket name
                call_kwargs = mock_storage_class.call_args.kwargs
                assert call_kwargs["bucket_name"] == "custom-bucket"


class TestStorageExceptions:
    """Test storage exception classes."""

    def test_storage_error_inheritance(self) -> None:
        """Test StorageError is an Exception."""
        error = StorageError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"

    def test_file_not_found_error_inheritance(self) -> None:
        """Test FileNotFoundError is a StorageError."""
        error = FileNotFoundError("file not found")
        assert isinstance(error, StorageError)
        assert str(error) == "file not found"


class TestGetStorageDependency:
    """Test get_storage dependency function (line 333)."""

    async def test_get_storage_returns_storage_service(self) -> None:
        """Test get_storage returns a StorageService instance."""
        from checklists_service.utils.storage import get_storage

        with patch("checklists_service.utils.storage.get_storage_service") as mock_get_service:
            mock_service = MagicMock(spec=StorageService)
            mock_get_service.return_value = mock_service

            result = await get_storage()

            assert result is mock_service
            mock_get_service.assert_called_once()
