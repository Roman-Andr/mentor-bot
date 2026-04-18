"""Unit tests for telegram_bot/utils/validators.py."""


from telegram_bot.utils.validators import (
    MAX_TOKEN_LENGTH,
    MIN_TOKEN_LENGTH,
    validate_invitation_token,
)


class TestValidateInvitationToken:
    """Test cases for validate_invitation_token function."""

    def test_valid_token_at_min_length(self):
        """Token at minimum length (8 chars) should be valid."""
        token = "a" * MIN_TOKEN_LENGTH
        assert validate_invitation_token(token) is True

    def test_valid_token_at_max_length(self):
        """Token at maximum length (64 chars) should be valid."""
        token = "a" * MAX_TOKEN_LENGTH
        assert validate_invitation_token(token) is True

    def test_valid_token_with_allowed_chars(self):
        """Token with allowed characters (alphanumeric, underscore, hyphen) should be valid."""
        valid_tokens = [
            "abc12345",  # alphanumeric
            "ABC12345",  # uppercase
            "abc-1234",  # with hyphen
            "abc_1234",  # with underscore
            "ABC-abc_123",  # mixed
        ]
        for token in valid_tokens:
            assert validate_invitation_token(token) is True, f"Token '{token}' should be valid"

    def test_invalid_token_below_min_length(self):
        """Token below minimum length (7 chars) should be invalid."""
        token = "a" * (MIN_TOKEN_LENGTH - 1)
        assert validate_invitation_token(token) is False

    def test_invalid_token_above_max_length(self):
        """Token above maximum length (65 chars) should be invalid."""
        token = "a" * (MAX_TOKEN_LENGTH + 1)
        assert validate_invitation_token(token) is False

    def test_invalid_token_with_forbidden_chars(self):
        """Token with forbidden characters should be invalid."""
        forbidden_tokens = [
            "abc 1234",   # space
            "abc!1234",   # exclamation
            "abc@1234",   # at symbol
            "abc#1234",   # hash
            "abc$1234",   # dollar
            "abc%1234",   # percent
            "abc^1234",   # caret
            "abc&1234",   # ampersand
            "abc*1234",   # asterisk
            "abc(1234",   # parenthesis
            "abc.1234",   # period
            "abc/1234",   # slash
        ]
        for token in forbidden_tokens:
            assert validate_invitation_token(token) is False, f"Token '{token}' should be invalid"

    def test_invalid_empty_string(self):
        """Empty string should be invalid."""
        assert validate_invitation_token("") is False

    def test_invalid_none(self):
        """None should be invalid."""
        assert validate_invitation_token(None) is False

    def test_boundary_length_7(self):
        """Exactly 7 characters should be invalid (boundary test)."""
        token = "a" * 7
        assert validate_invitation_token(token) is False

    def test_boundary_length_8(self):
        """Exactly 8 characters should be valid (boundary test)."""
        token = "a" * 8
        assert validate_invitation_token(token) is True

    def test_boundary_length_64(self):
        """Exactly 64 characters should be valid (boundary test)."""
        token = "a" * 64
        assert validate_invitation_token(token) is True

    def test_boundary_length_65(self):
        """Exactly 65 characters should be invalid (boundary test)."""
        token = "a" * 65
        assert validate_invitation_token(token) is False
