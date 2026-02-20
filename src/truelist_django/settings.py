from __future__ import annotations

from typing import Any

from django.conf import settings

_DEFAULTS: dict[str, Any] = {
    "TRUELIST_API_KEY": "",
    "TRUELIST_BASE_URL": "https://api.truelist.io",
    "TRUELIST_TIMEOUT": 10,
    "TRUELIST_ALLOW_RISKY": True,
    "TRUELIST_CACHE_ENABLED": False,
    "TRUELIST_CACHE_TTL": 3600,
    "TRUELIST_CACHE_ALIAS": "default",
}


def get_setting(name: str) -> Any:
    """Get a Truelist setting from Django settings, falling back to defaults.

    Args:
        name: The setting name (e.g. "TRUELIST_API_KEY").

    Returns:
        The setting value.

    Raises:
        AttributeError: If the setting name is not a valid Truelist setting.
    """
    if name not in _DEFAULTS:
        raise AttributeError(f"Invalid Truelist setting: {name!r}")
    return getattr(settings, name, _DEFAULTS[name])
