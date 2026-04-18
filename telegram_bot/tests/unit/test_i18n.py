"""Unit tests for telegram_bot/i18n/__init__.py."""

from telegram_bot.i18n import DEFAULT_LOCALE, t


class TestI18n:
    """Test cases for internationalization."""

    def test_default_locale_constant(self):
        """Test DEFAULT_LOCALE constant."""
        assert DEFAULT_LOCALE == "en"

    def test_t_function_basic(self):
        """Test t() function with basic key - verifies key is in result."""
        result = t("common.back_button", locale="en")

        assert isinstance(result, str)
        # Test translations include key name in brackets
        assert "[common.back_button]" in result

    def test_t_function_russian_locale(self):
        """Test t() function with Russian locale."""
        result = t("common.back_button", locale="ru")

        assert isinstance(result, str)
        assert "[common.back_button]" in result

    def test_t_function_with_kwargs(self):
        """Test t() function with format kwargs (covers lines 35-38)."""
        # Use a translation key that has a placeholder
        result = t("feedback.pulse_thanks", locale="en", rating=5)

        assert isinstance(result, str)
        assert "5" in result
        assert "[feedback.pulse_thanks]" in result

    def test_t_function_with_multiple_kwargs(self):
        """Test t() function with multiple format kwargs."""
        result = t("feedback.pulse_invalid", locale="en", min=1, max=10)

        assert isinstance(result, str)
        assert "1" in result
        assert "10" in result
        assert "[feedback.pulse_invalid]" in result

    def test_t_function_fallback_to_en(self):
        """Test t() function falls back to English for unknown locale."""
        result = t("common.back_button", locale="unknown")

        assert isinstance(result, str)
        assert "[common.back_button]" in result

    def test_t_function_empty_kwargs(self):
        """Test t() function with empty kwargs (no formatting branch)."""
        result = t("common.back_button", locale="en", **{})

        assert isinstance(result, str)
        assert "[common.back_button]" in result

    def test_t_function_direct_coverage(self):
        """Test that directly calls t() to ensure coverage of all branches."""
        # Call t() multiple ways to cover all branches
        r1 = t("common.back_button", locale="en")
        assert "[common.back_button]" in r1

        r2 = t("feedback.pulse_thanks", locale="en", rating=8)
        assert isinstance(r2, str)
        assert "8" in r2
        assert "[feedback.pulse_thanks]" in r2

        r3 = t("common.back_button", locale="en", **{})
        assert "[common.back_button]" in r3

    def test_t_function_no_kwargs_branch(self):
        """Test t() function when kwargs is empty (covers line 35-36, 38)."""
        result = t("common.back_button", locale="en")

        assert "[common.back_button]" in result

    def test_t_function_with_kwargs_branch(self):
        """Test t() function when kwargs is not empty (covers lines 35-38)."""
        # Key with placeholder - format branch executes
        result = t("feedback.pulse_thanks", locale="en", rating=7)
        assert "7" in result
        assert "[feedback.pulse_thanks]" in result

    def test_t_function_string_formatting(self):
        """Test that string formatting with kwargs works correctly."""
        # Test with {min} and {max} placeholders
        result = t("meetings.title_too_short", locale="en", min=3)
        assert isinstance(result, str)
        assert "3" in result
        assert "[meetings.title_too_short]" in result
