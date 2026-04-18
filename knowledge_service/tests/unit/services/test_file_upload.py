"""Tests for file upload service and security validation."""

from unittest.mock import patch

from knowledge_service.core.security import (
    generate_secure_filename,
    sanitize_html,
    validate_file_size,
    validate_file_type,
    validate_filename,
)


class TestValidateFilename:
    """Test filename validation and sanitization."""

    def test_valid_filename(self) -> None:
        """Test valid filename is preserved."""
        result = validate_filename("document.pdf")
        assert result == "document.pdf"

    def test_filename_with_spaces(self) -> None:
        """Test spaces are replaced with underscores."""
        result = validate_filename("my document.pdf")
        assert result == "my_document.pdf"

    def test_filename_path_traversal(self) -> None:
        """Test path traversal is prevented."""
        result = validate_filename("../../../etc/passwd")
        assert ".." not in result
        assert result == "passwd"

    def test_filename_special_chars(self) -> None:
        """Test special characters are removed."""
        result = validate_filename("file<name>:with*special?chars.pdf")
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert "*" not in result
        assert "?" not in result

    def test_filename_unicode(self) -> None:
        """Test unicode filename handling."""
        result = validate_filename("\u6587\u6863.pdf")  # Chinese characters
        assert result == "\u6587\u6863.pdf"

    def test_filename_long_name(self) -> None:
        """Test very long filename is truncated."""
        long_name = "a" * 300 + ".pdf"
        result = validate_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".pdf")

    def test_filename_empty(self) -> None:
        """Test empty filename."""
        result = validate_filename("")
        assert result == ""


class TestValidateFileSize:
    """Test file size validation."""

    def test_valid_file_size(self) -> None:
        """Test file within size limit passes."""
        with patch("knowledge_service.config.settings.MAX_FILE_SIZE_MB", 10):
            result = validate_file_size(5 * 1024 * 1024)  # 5MB
            assert result is True

    def test_file_size_at_limit(self) -> None:
        """Test file at exact size limit passes."""
        with patch("knowledge_service.config.settings.MAX_FILE_SIZE_MB", 10):
            result = validate_file_size(10 * 1024 * 1024)  # 10MB
            assert result is True

    def test_file_size_over_limit(self) -> None:
        """Test oversized file fails validation."""
        with patch("knowledge_service.config.settings.MAX_FILE_SIZE_MB", 10):
            result = validate_file_size(15 * 1024 * 1024)  # 15MB
            assert result is False

    def test_zero_file_size(self) -> None:
        """Test zero byte file passes."""
        with patch("knowledge_service.config.settings.MAX_FILE_SIZE_MB", 10):
            result = validate_file_size(0)
            assert result is True


class TestValidateFileType:
    """Test file type validation."""

    def test_valid_pdf(self) -> None:
        """Test PDF extension is allowed."""
        with patch("knowledge_service.config.settings.ALLOWED_FILE_TYPES", ["pdf", "docx"]):
            result = validate_file_type("document.pdf")
            assert result is True

    def test_valid_docx(self) -> None:
        """Test DOCX extension is allowed."""
        with patch("knowledge_service.config.settings.ALLOWED_FILE_TYPES", ["pdf", "docx"]):
            result = validate_file_type("document.docx")
            assert result is True

    def test_case_insensitive(self) -> None:
        """Test file extension matching is case insensitive."""
        with patch("knowledge_service.config.settings.ALLOWED_FILE_TYPES", ["pdf"]):
            assert validate_file_type("document.PDF") is True
            assert validate_file_type("document.Pdf") is True

    def test_invalid_extension(self) -> None:
        """Test invalid extension is rejected."""
        with patch("knowledge_service.config.settings.ALLOWED_FILE_TYPES", ["pdf", "docx"]):
            result = validate_file_type("script.exe")
            assert result is False

    def test_no_extension(self) -> None:
        """Test file without extension is rejected."""
        with patch("knowledge_service.config.settings.ALLOWED_FILE_TYPES", ["pdf"]):
            result = validate_file_type("Makefile")
            assert result is False

    def test_empty_filename(self) -> None:
        """Test empty filename is rejected."""
        result = validate_file_type("")
        assert result is False

    def test_multiple_dots(self) -> None:
        """Test filename with multiple dots - only last extension is checked."""
        with patch("knowledge_service.config.settings.ALLOWED_FILE_TYPES", ["gz", "pdf"]):
            assert validate_file_type("archive.tar.gz") is True
            assert validate_file_type("document.pdf") is True


class TestGenerateSecureFilename:
    """Test secure filename generation."""

    def test_generates_unique_filename(self) -> None:
        """Test generated filename is unique with different timestamps."""
        with patch("knowledge_service.core.security.time.time") as mock_time:
            mock_time.return_value = 1000.0
            filename1 = generate_secure_filename("test.pdf", user_id=1)

            mock_time.return_value = 2000.0
            filename2 = generate_secure_filename("test.pdf", user_id=1)

        assert filename1 != filename2

    def test_includes_user_id(self) -> None:
        """Test filename includes user ID."""
        result = generate_secure_filename("document.pdf", user_id=42)
        assert result.startswith("42_")

    def test_preserves_extension(self) -> None:
        """Test file extension is preserved."""
        result = generate_secure_filename("report.pdf", user_id=1)
        assert result.endswith(".pdf")

        result = generate_secure_filename("data.docx", user_id=1)
        assert result.endswith(".docx")

    def test_different_users_different_names(self) -> None:
        """Test same filename for different users generates different results."""
        result1 = generate_secure_filename("file.pdf", user_id=1)
        result2 = generate_secure_filename("file.pdf", user_id=2)

        assert result1 != result2

    def test_same_input_different_timestamp(self) -> None:
        """Test same input at different times generates different results."""
        with patch("knowledge_service.core.security.time.time") as mock_time:
            mock_time.return_value = 1000
            result1 = generate_secure_filename("file.pdf", user_id=1)

            mock_time.return_value = 2000
            result2 = generate_secure_filename("file.pdf", user_id=1)

            assert result1 != result2


class TestSanitizeHtml:
    """Test HTML sanitization."""

    def test_removes_script_tags(self) -> None:
        """Test script tags are removed."""
        html = '<p>Hello</p><script>alert("xss")</script>'
        result = sanitize_html(html)
        assert "<script>" not in result
        assert "</script>" not in result
        assert "alert" not in result

    def test_removes_event_handlers(self) -> None:
        """Test event handlers are removed."""
        html = '<p onclick="alert(1)">Click me</p>'
        result = sanitize_html(html)
        assert "onclick" not in result.lower()

    def test_removes_javascript_urls(self) -> None:
        """Test javascript: URLs are removed."""
        html = '<a href="javascript:alert(1)">Link</a>'
        result = sanitize_html(html)
        assert "javascript:" not in result.lower()

    def test_preserves_safe_html(self) -> None:
        """Test safe HTML is preserved."""
        html = "<p><strong>Bold</strong> and <em>italic</em></p>"
        result = sanitize_html(html)
        assert "<p>" in result
        assert "<strong>" in result
        assert "<em>" in result

    def test_handles_empty_string(self) -> None:
        """Test empty string handling."""
        result = sanitize_html("")
        assert result == ""


class TestFileUploadIntegration:
    """Integration tests for file upload workflow."""

    def test_full_upload_validation_pass(self) -> None:
        """Test complete validation flow for valid file."""
        with patch("knowledge_service.config.settings.MAX_FILE_SIZE_MB", 10):
            with patch("knowledge_service.config.settings.ALLOWED_FILE_TYPES", ["pdf", "docx"]):
                filename = "report.pdf"
                file_size = 5 * 1024 * 1024

                # Step 1: Validate filename
                safe_filename = validate_filename(filename)
                assert safe_filename == "report.pdf"

                # Step 2: Validate file size
                assert validate_file_size(file_size) is True

                # Step 3: Validate file type
                assert validate_file_type(filename) is True

    def test_full_upload_validation_fail_size(self) -> None:
        """Test complete validation flow for oversized file."""
        with patch("knowledge_service.config.settings.MAX_FILE_SIZE_MB", 10):
            with patch("knowledge_service.config.settings.ALLOWED_FILE_TYPES", ["pdf"]):
                file_size = 20 * 1024 * 1024

                assert validate_file_size(file_size) is False

    def test_full_upload_validation_fail_type(self) -> None:
        """Test complete validation flow for invalid file type."""
        with patch("knowledge_service.config.settings.ALLOWED_FILE_TYPES", ["pdf", "docx"]):
            filename = "virus.exe"

            assert validate_file_type(filename) is False

    def test_malicious_filename_handling(self) -> None:
        """Test handling of malicious filenames - path traversal is sanitized."""
        malicious_names = [
            "../../../etc/passwd",
            "/etc/shadow",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "normal.txt/../../../etc/passwd",
        ]

        for name in malicious_names:
            safe_name = validate_filename(name)
            # After validation, should be just the filename without directory separators
            # Note: Path().name removes directory path, but we also need to sanitize
            assert "/" not in safe_name, f"Slash not removed from: {name}"
            assert "\\" not in safe_name, f"Backslash not removed from: {name}"
            # Result should be a single filename without path components
            assert "\n" not in safe_name
            assert "\t" not in safe_name
