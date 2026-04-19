"""Internationalization support using python-i18n."""

from pathlib import Path

import i18n

# Configure i18n
i18n.set("file_format", "json")
i18n.set("filename_format", "{locale}.{format}")
i18n.set("fallback", "en")
i18n.set("available_locales", ["en", "ru"])
i18n.set("skip_locale_root_data", True)

# Load from relative path
_locale_dir = Path(__file__).resolve().parent.parent / "locales"
if _locale_dir.is_dir() and str(_locale_dir) not in i18n.load_path:
    i18n.load_path.append(str(_locale_dir))

DEFAULT_LOCALE = "en"


def t(key: str, locale: str = DEFAULT_LOCALE, **kwargs: object) -> str:
    """Translate a key to the given locale.

    Args:
        key: Translation key (dot-separated namespace).
        locale: Target locale (``"en"`` or ``"ru"``).
        **kwargs: Interpolation variables.

    Returns:
        Translated string with variables interpolated.

    """
    result: str = i18n.t(key, locale=locale)
    if kwargs:
        result = result.format(**kwargs)
    return result


__all__ = ["DEFAULT_LOCALE", "t"]
