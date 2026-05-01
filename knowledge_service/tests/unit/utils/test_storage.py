"""Tests for S3 storage service."""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from knowledge_service.utils.storage import (
    FileNotFoundError,
    StorageError,
    StorageService,
    get_storage_service,
)


class TestStorageServiceInit:
    """Test StorageService initialization."""

    def test_init_creates_client(self):
        """Test that initialization creates boto3 client."""
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client
            mock_client.head_bucket.return_value = None  # Bucket exists

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
                region="us-east-1",
                use_ssl=False,
                secure_mode=False,
            )

            assert service.bucket_name == "test-bucket"
            assert service.endpoint == "http://minio:9000"
            mock_boto.assert_called_once()
            mock_client.head_bucket.assert_called_once_with(Bucket="test-bucket")

    def test_init_creates_bucket_if_not_exists(self):
        """Test that bucket is created if it doesn't exist."""
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client

            # First call (head_bucket) raises 404, second call (create_bucket) succeeds
            error_response = {"Error": {"Code": "404"}}
            mock_client.head_bucket.side_effect = ClientError(error_response, "HeadBucket")
            mock_client.create_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="new-bucket",
                region="us-east-1",
                use_ssl=False,
                secure_mode=False,
            )

            mock_client.create_bucket.assert_called_once_with(Bucket="new-bucket")

    def test_init_raises_on_bucket_creation_failure(self):
        """Test that StorageError is raised when bucket creation fails."""
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client

            error_response = {"Error": {"Code": "404"}}
            mock_client.head_bucket.side_effect = ClientError(error_response, "HeadBucket")
            mock_client.create_bucket.side_effect = ClientError(
                {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}},
                "CreateBucket",
            )

            with pytest.raises(StorageError, match="Failed to initialize bucket"):
                StorageService(
                    endpoint="http://minio:9000",
                    access_key="test-key",
                    secret_key="test-secret",
                    bucket_name="protected-bucket",
                    region="us-east-1",
                    use_ssl=False,
                    secure_mode=False,
                )


class TestUploadFile:
    """Test file upload functionality."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock storage service."""
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
                region="us-east-1",
                use_ssl=False,
                secure_mode=False,
            )
            service.client = mock_client
            yield service

    @pytest.mark.asyncio
    async def test_upload_file_bytes(self, mock_service):
        """Test uploading file from bytes."""
        mock_service.client.upload_fileobj.return_value = None

        result = await mock_service.upload_file(
            file_data=b"test content",
            object_name="test/file.txt",
            content_type="text/plain",
            metadata={"key": "value"},
        )

        assert result == "test/file.txt"
        mock_service.client.upload_fileobj.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file_bytesio(self, mock_service):
        """Test uploading file from BytesIO."""
        mock_service.client.upload_fileobj.return_value = None

        file_stream = BytesIO(b"test content")
        result = await mock_service.upload_file(
            file_data=file_stream,
            object_name="test/file.txt",
            content_type="text/plain",
        )

        assert result == "test/file.txt"
        mock_service.client.upload_fileobj.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file_without_content_type(self, mock_service):
        """Test uploading file without content type."""
        mock_service.client.upload_fileobj.return_value = None

        result = await mock_service.upload_file(
            file_data=b"test content",
            object_name="test/file.txt",
        )

        assert result == "test/file.txt"
        mock_service.client.upload_fileobj.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_file_error(self, mock_service):
        """Test that StorageError is raised on upload failure."""
        mock_service.client.upload_fileobj.side_effect = ClientError(
            {"Error": {"Code": "InternalError", "Message": "Internal error"}},
            "UploadFile",
        )

        with pytest.raises(StorageError, match="Upload failed"):
            await mock_service.upload_file(
                file_data=b"test content",
                object_name="test/file.txt",
            )


class TestDownloadFile:
    """Test file download functionality."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock storage service."""
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
                region="us-east-1",
                use_ssl=False,
                secure_mode=False,
            )
            service.client = mock_client
            yield service

    @pytest.mark.asyncio
    async def test_download_file_success(self, mock_service):
        """Test successful file download."""

        def mock_download(bucket, key, buf):
            buf.write(b"downloaded content")

        mock_service.client.download_fileobj.side_effect = mock_download

        result = await mock_service.download_file("test/file.txt")

        assert result.read() == b"downloaded content"
        mock_service.client.download_fileobj.assert_called_once()

    @pytest.mark.asyncio
    async def test_download_file_not_found(self, mock_service):
        """Test downloading non-existent file raises FileNotFoundError."""
        mock_service.client.download_fileobj.side_effect = ClientError(
            {"Error": {"Code": "404"}},
            "DownloadFile",
        )

        with pytest.raises(FileNotFoundError, match="File not found"):
            await mock_service.download_file("test/nonexistent.txt")

    @pytest.mark.asyncio
    async def test_download_file_no_such_key(self, mock_service):
        """Test downloading with NoSuchKey error raises FileNotFoundError."""
        mock_service.client.download_fileobj.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey"}},
            "DownloadFile",
        )

        with pytest.raises(FileNotFoundError, match="File not found"):
            await mock_service.download_file("test/missing.txt")

    @pytest.mark.asyncio
    async def test_download_file_storage_error(self, mock_service):
        """Test that StorageError is raised on other download failures."""
        mock_service.client.download_fileobj.side_effect = ClientError(
            {"Error": {"Code": "InternalError", "Message": "Server error"}},
            "DownloadFile",
        )

        with pytest.raises(StorageError, match="Download failed"):
            await mock_service.download_file("test/file.txt")


class TestDeleteFile:
    """Test file deletion functionality."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock storage service."""
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
                region="us-east-1",
                use_ssl=False,
                secure_mode=False,
            )
            service.client = mock_client
            yield service

    @pytest.mark.asyncio
    async def test_delete_file_success(self, mock_service):
        """Test successful file deletion."""
        mock_service.client.delete_object.return_value = None

        result = await mock_service.delete_file("test/file.txt")

        assert result is True
        mock_service.client.delete_object.assert_called_once_with(Bucket="test-bucket", Key="test/file.txt")

    @pytest.mark.asyncio
    async def test_delete_file_not_found_returns_false(self, mock_service):
        """Test that deleting non-existent file returns False."""
        mock_service.client.delete_object.side_effect = ClientError(
            {"Error": {"Code": "404"}},
            "DeleteObject",
        )

        result = await mock_service.delete_file("test/nonexistent.txt")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_file_storage_error(self, mock_service):
        """Test that StorageError is raised on deletion failure."""
        mock_service.client.delete_object.side_effect = ClientError(
            {"Error": {"Code": "InternalError", "Message": "Server error"}},
            "DeleteObject",
        )

        with pytest.raises(StorageError, match="Delete failed"):
            await mock_service.delete_file("test/file.txt")


class TestFileExists:
    """Test file existence check."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock storage service."""
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
                region="us-east-1",
                use_ssl=False,
                secure_mode=False,
            )
            service.client = mock_client
            yield service

    @pytest.mark.asyncio
    async def test_file_exists_true(self, mock_service):
        """Test checking existing file returns True."""
        mock_service.client.head_object.return_value = {"ContentLength": 100}

        result = await mock_service.file_exists("test/file.txt")

        assert result is True
        mock_service.client.head_object.assert_called_once_with(Bucket="test-bucket", Key="test/file.txt")

    @pytest.mark.asyncio
    async def test_file_exists_false_404(self, mock_service):
        """Test checking non-existent file returns False (404)."""
        mock_service.client.head_object.side_effect = ClientError(
            {"Error": {"Code": "404"}},
            "HeadObject",
        )

        result = await mock_service.file_exists("test/nonexistent.txt")

        assert result is False

    @pytest.mark.asyncio
    async def test_file_exists_false_no_such_key(self, mock_service):
        """Test checking non-existent file returns False (NoSuchKey)."""
        mock_service.client.head_object.side_effect = ClientError(
            {"Error": {"Code": "NoSuchKey"}},
            "HeadObject",
        )

        result = await mock_service.file_exists("test/missing.txt")

        assert result is False

    @pytest.mark.asyncio
    async def test_file_exists_raises_other_errors(self, mock_service):
        """Test that other errors are raised."""
        mock_service.client.head_object.side_effect = ClientError(
            {"Error": {"Code": "InternalError"}},
            "HeadObject",
        )

        with pytest.raises(ClientError):
            await mock_service.file_exists("test/file.txt")


class TestPresignedUrl:
    """Test presigned URL generation."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock storage service."""
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
                region="us-east-1",
                use_ssl=False,
                secure_mode=False,
            )
            service.client = mock_client
            yield service

    def test_get_presigned_url_get(self, mock_service):
        """Test generating GET presigned URL."""
        mock_service.client.generate_presigned_url.return_value = (
            "http://minio:9000/test-bucket/file.txt?signature=abc123"
        )

        result = mock_service.get_presigned_url("file.txt", expires=3600, method="GET")

        assert "test-bucket/file.txt" in result
        mock_service.client.generate_presigned_url.assert_called_once_with(
            ClientMethod="get_object",
            Params={"Bucket": "test-bucket", "Key": "file.txt"},
            ExpiresIn=3600,
        )

    def test_get_presigned_url_put(self, mock_service):
        """Test generating PUT presigned URL."""
        mock_service.client.generate_presigned_url.return_value = (
            "http://minio:9000/test-bucket/file.txt?signature=abc123"
        )

        result = mock_service.get_presigned_url("file.txt", expires=1800, method="PUT")

        mock_service.client.generate_presigned_url.assert_called_once_with(
            ClientMethod="put_object",
            Params={"Bucket": "test-bucket", "Key": "file.txt"},
            ExpiresIn=1800,
        )

    def test_get_presigned_url_converts_to_http_in_non_secure_mode(self, mock_service):
        """Test that HTTPS URLs are converted to HTTP in non-secure mode."""
        mock_service.client.generate_presigned_url.return_value = (
            "https://minio:9000/test-bucket/file.txt?signature=abc123"
        )
        mock_service.secure_mode = False

        result = mock_service.get_presigned_url("file.txt")

        assert result.startswith("http://")
        assert not result.startswith("https://")

    def test_get_presigned_url_error(self, mock_service):
        """Test that StorageError is raised on URL generation failure."""
        mock_service.client.generate_presigned_url.side_effect = ClientError(
            {"Error": {"Code": "InternalError"}},
            "GeneratePresignedUrl",
        )

        with pytest.raises(StorageError, match="URL generation failed"):
            mock_service.get_presigned_url("file.txt")


class TestPublicUrl:
    """Test public URL generation."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock storage service."""
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client
            mock_client.head_bucket.return_value = None

            service = StorageService(
                endpoint="http://minio:9000",
                access_key="test-key",
                secret_key="test-secret",
                bucket_name="test-bucket",
                region="us-east-1",
                use_ssl=False,
                secure_mode=False,
            )
            yield service

    def test_get_public_url_http_endpoint(self, mock_service):
        """Test public URL with HTTP endpoint."""
        result = mock_service.get_public_url("articles/1/file.pdf")

        assert result == "http://minio:9000/test-bucket/articles/1/file.pdf"

    def test_get_public_url_https_endpoint(self, mock_service):
        """Test public URL with HTTPS endpoint."""
        mock_service.endpoint = "https://s3.amazonaws.com"
        mock_service.secure_mode = True

        result = mock_service.get_public_url("articles/1/file.pdf")

        assert result == "https://s3.amazonaws.com/test-bucket/articles/1/file.pdf"

    def test_get_public_url_no_scheme_uses_secure_mode(self, mock_service):
        """Test public URL with no scheme uses secure_mode."""
        mock_service.endpoint = "minio:9000"

        # With secure_mode=False
        mock_service.secure_mode = False
        result = mock_service.get_public_url("file.txt")
        assert result.startswith("http://")

        # With secure_mode=True
        mock_service.secure_mode = True
        result = mock_service.get_public_url("file.txt")
        assert result.startswith("https://")


class TestStorageServiceInitOtherErrors:
    """Test StorageService initialization with non-404 errors - covers lines 106-107."""

    def test_init_raises_on_non_404_bucket_error(self):
        """
        Test that StorageError is raised for non-404 bucket errors - covers lines 106-107.

        When head_bucket raises a ClientError with code other than 404,
        the error should be re-raised as StorageError.
        """
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client

            # Simulate a 500 InternalError (not 404)
            error_response = {"Error": {"Code": "InternalError", "Message": "Internal Server Error"}}
            mock_client.head_bucket.side_effect = ClientError(error_response, "HeadBucket")

            with pytest.raises(StorageError, match="Failed to initialize bucket"):
                StorageService(
                    endpoint="http://minio:9000",
                    access_key="test-key",
                    secret_key="test-secret",
                    bucket_name="test-bucket",
                    region="us-east-1",
                    use_ssl=False,
                    secure_mode=False,
                )

    def test_init_raises_on_access_denied_bucket_error(self):
        """Test that StorageError is raised for AccessDenied bucket errors - covers lines 106-107."""
        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client

            # Simulate AccessDenied error (not 404)
            error_response = {"Error": {"Code": "AccessDenied", "Message": "Access Denied"}}
            mock_client.head_bucket.side_effect = ClientError(error_response, "HeadBucket")

            with pytest.raises(StorageError, match="Failed to initialize bucket"):
                StorageService(
                    endpoint="http://minio:9000",
                    access_key="test-key",
                    secret_key="test-secret",
                    bucket_name="test-bucket",
                    region="us-east-1",
                    use_ssl=False,
                    secure_mode=False,
                )


class TestGetStorageDependency:
    """Test get_storage dependency injection helper - covers line 333."""

    @pytest.mark.asyncio
    async def test_get_storage_returns_storage_service(self):
        """Test that get_storage returns a StorageService instance - covers line 333."""
        # Clear any existing instance
        import knowledge_service.utils.storage as storage_module
        from knowledge_service.utils.storage import get_storage

        storage_module._storage_instance = None

        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client
            mock_client.head_bucket.return_value = None

            with patch("knowledge_service.utils.storage.settings") as mock_settings:
                mock_settings.S3_ENDPOINT = "http://minio:9000"
                mock_settings.S3_ACCESS_KEY = "test-key"
                mock_settings.S3_SECRET_KEY = "test-secret"
                mock_settings.S3_REGION = "us-east-1"
                mock_settings.S3_USE_SSL = False
                mock_settings.KNOWLEDGE_S3_BUCKET = "test-bucket"

                result = await get_storage()

                assert isinstance(result, StorageService)
                assert result.bucket_name == "test-bucket"


class TestGetStorageService:
    """Test get_storage_service singleton function."""

    def test_get_storage_service_singleton(self):
        """Test that get_storage_service returns a singleton."""
        # Clear any existing instance
        import knowledge_service.utils.storage as storage_module

        storage_module._storage_instance = None

        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client
            mock_client.head_bucket.return_value = None

            with patch("knowledge_service.utils.storage.settings") as mock_settings:
                mock_settings.S3_ENDPOINT = "http://minio:9000"
                mock_settings.S3_ACCESS_KEY = "test-key"
                mock_settings.S3_SECRET_KEY = "test-secret"
                mock_settings.S3_REGION = "us-east-1"
                mock_settings.S3_USE_SSL = False
                mock_settings.KNOWLEDGE_S3_BUCKET = "test-bucket"

                service1 = get_storage_service()
                service2 = get_storage_service()

                assert service1 is service2  # Same instance

    def test_get_storage_service_with_custom_bucket(self):
        """Test getting service with custom bucket name."""
        import knowledge_service.utils.storage as storage_module

        storage_module._storage_instance = None

        with patch("knowledge_service.utils.storage.boto3.client") as mock_boto:
            mock_client = MagicMock()
            mock_boto.return_value = mock_client
            mock_client.head_bucket.return_value = None

            with patch("knowledge_service.utils.storage.settings") as mock_settings:
                mock_settings.S3_ENDPOINT = "http://minio:9000"
                mock_settings.S3_ACCESS_KEY = "test-key"
                mock_settings.S3_SECRET_KEY = "test-secret"
                mock_settings.S3_REGION = "us-east-1"
                mock_settings.S3_USE_SSL = False
                mock_settings.KNOWLEDGE_S3_BUCKET = "default-bucket"

                service = get_storage_service(bucket_name="custom-bucket")

                assert service.bucket_name == "custom-bucket"
