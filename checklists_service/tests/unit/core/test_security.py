"""Unit tests for core/security.py file validation functions."""

from unittest.mock import patch

from checklists_service.core.security import (
    generate_secure_filename,
    validate_file_size,
    validate_file_type,
    validate_filename,
)


class TestValidateFilename:
    """Test filename validation and sanitization."""

    def test_validate_filename_simple(self) -> None:
        """Test simple filename validation."""
        result = validate_filename("document.pdf")
        assert result == "document.pdf"

    def test_validate_filename_with_spaces(self) -> None:
        """Test filename with spaces is sanitized."""
        result = validate_filename("my document.pdf")
        assert result == "my_document.pdf"

    def test_validate_filename_with_special_chars(self) -> None:
        """Test filename with special characters is sanitized."""
        result = validate_filename("file@#$%^&*()name.pdf")
        assert result == "filename.pdf"

    def test_validate_filename_path_traversal_attempt(self) -> None:
        """Test path traversal attempt is blocked."""
        result = validate_filename("../../../etc/passwd.pdf")
        assert result == "passwd.pdf"
        assert "/" not in result

    def test_validate_filename_empty(self) -> None:
        """Test empty filename handling."""
        result = validate_filename("")
        assert result == ""

    def test_validate_filename_very_long(self) -> None:
        """Test very long filename is truncated."""
        long_name = "a" * 300 + ".pdf"
        result = validate_filename(long_name)
        assert len(result) <= 255

    def test_validate_filename_preserve_extension(self) -> None:
        """Test that file extension is preserved during truncation."""
        long_name = "a" * 300 + ".verylongextension"
        result = validate_filename(long_name)
        assert result.endswith(".verylongextension")
        assert len(result) <= 255

    def test_validate_filename_multiple_dots(self) -> None:
        """Test filename with multiple dots."""
        result = validate_filename("my.file.name.pdf")
        assert result == "my.file.name.pdf"

    def test_validate_filename_unicode(self) -> None:
        """Test filename with unicode characters is sanitized."""
        result = validate_filename("ドキュメント.pdf")
        # Unicode word characters are kept by \w in Python 3, only extension should remain
        # depending on regex behavior with unicode
        assert result.endswith(".pdf")


class TestValidateFileSize:
    """Test file size validation."""

    def test_validate_file_size_under_limit(self) -> None:
        """Test file size under limit passes."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.MAX_FILE_SIZE_MB = 10

            # 5 MB in bytes
            size = 5 * 1024 * 1024
            result = validate_file_size(size)
            assert result is True

    def test_validate_file_size_at_limit(self) -> None:
        """Test file size at limit passes."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.MAX_FILE_SIZE_MB = 10

            # Exactly 10 MB
            size = 10 * 1024 * 1024
            result = validate_file_size(size)
            assert result is True

    def test_validate_file_size_over_limit(self) -> None:
        """Test file size over limit fails."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.MAX_FILE_SIZE_MB = 10

            # 15 MB in bytes
            size = 15 * 1024 * 1024
            result = validate_file_size(size)
            assert result is False

    def test_validate_file_size_zero(self) -> None:
        """Test zero file size passes."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.MAX_FILE_SIZE_MB = 10

            result = validate_file_size(0)
            assert result is True

    def test_validate_file_size_different_limits(self) -> None:
        """Test with different configured limits."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.MAX_FILE_SIZE_MB = 1

            # 500 KB should pass with 1 MB limit
            size = 500 * 1024
            result = validate_file_size(size)
            assert result is True

            # 2 MB should fail with 1 MB limit
            size = 2 * 1024 * 1024
            result = validate_file_size(size)
            assert result is False


class TestValidateFileType:
    """Test file type validation."""

    def test_validate_allowed_types(self) -> None:
        """Test all allowed file types pass."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.ALLOWED_FILE_TYPES = [
                ".pdf", ".doc", ".docx", ".xls", ".xlsx",
                ".txt", ".png", ".jpg", ".jpeg"
            ]

            assert validate_file_type("document.pdf") is True
            assert validate_file_type("document.doc") is True
            assert validate_file_type("document.docx") is True
            assert validate_file_type("spreadsheet.xls") is True
            assert validate_file_type("spreadsheet.xlsx") is True
            assert validate_file_type("notes.txt") is True
            assert validate_file_type("image.png") is True
            assert validate_file_type("image.jpg") is True
            assert validate_file_type("image.jpeg") is True

    def test_validate_disallowed_types(self) -> None:
        """Test disallowed file types fail."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.ALLOWED_FILE_TYPES = [".pdf", ".doc"]

            assert validate_file_type("script.exe") is False
            assert validate_file_type("archive.zip") is False
            assert validate_file_type("code.py") is False
            assert validate_file_type("web.html") is False

    def test_validate_file_type_case_insensitive(self) -> None:
        """Test file type validation is case insensitive."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.ALLOWED_FILE_TYPES = [".pdf", ".doc"]

            assert validate_file_type("document.PDF") is True
            assert validate_file_type("document.Pdf") is True
            assert validate_file_type("document.DOC") is True

    def test_validate_file_type_empty_filename(self) -> None:
        """Test empty filename fails validation."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.ALLOWED_FILE_TYPES = [".pdf"]

            assert validate_file_type("") is False

    def test_validate_file_type_no_extension(self) -> None:
        """Test filename without extension fails."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.ALLOWED_FILE_TYPES = [".pdf"]

            assert validate_file_type("document") is False

    def test_validate_file_type_multiple_dots(self) -> None:
        """Test file with multiple dots - uses last extension."""
        with patch("checklists_service.core.security.settings") as mock_settings:
            mock_settings.ALLOWED_FILE_TYPES = [".pdf"]

            # Should check last extension
            assert validate_file_type("archive.tar.gz") is False
            assert validate_file_type("document.backup.pdf") is True


class TestGenerateSecureFilename:
    """Test secure filename generation."""

    def test_generate_secure_filename_format(self) -> None:
        """Test secure filename has correct format."""
        result = generate_secure_filename("document.pdf", user_id=123)

        # Format should be: {user_id}_{timestamp}_{hash}.ext
        parts = result.replace(".pdf", "").split("_")
        assert len(parts) == 3
        assert parts[0] == "123"  # user_id
        assert parts[1].isdigit()  # timestamp
        assert len(parts[2]) == 8  # 8 char hash

    def test_generate_secure_filename_different_users(self) -> None:
        """Test different users get different filenames."""
        result1 = generate_secure_filename("file.pdf", user_id=1)
        result2 = generate_secure_filename("file.pdf", user_id=2)

        assert result1 != result2

    def test_generate_secure_filename_same_user_different_time(self) -> None:
        """Test same user at different times gets different filenames."""
        with patch("checklists_service.core.security.time") as mock_time:
            mock_time.time.side_effect = [1000, 2000]

            result1 = generate_secure_filename("file.pdf", user_id=1)
            result2 = generate_secure_filename("file.pdf", user_id=1)

            assert result1 != result2

    def test_generate_secure_filename_preserves_extension(self) -> None:
        """Test that file extension is preserved."""
        result = generate_secure_filename("document.pdf", user_id=1)
        assert result.endswith(".pdf")

        result = generate_secure_filename("spreadsheet.xlsx", user_id=1)
        assert result.endswith(".xlsx")

        result = generate_secure_filename("image.jpeg", user_id=1)
        assert result.endswith(".jpeg")

    def test_generate_secure_filename_multiple_dots(self) -> None:
        """Test handling of filenames with multiple dots."""
        result = generate_secure_filename("my.backup.file.pdf", user_id=1)

        # Should preserve the last extension only
        assert result.endswith(".pdf")
        assert "my.backup.file" not in result  # Original stem replaced

    def test_generate_secure_filename_no_extension(self) -> None:
        """Test handling of filename without extension."""
        result = generate_secure_filename("document", user_id=1)

        parts = result.split("_")
        assert len(parts) == 3
        # No extension at the end
        assert "." not in result.split("_")[-1]
