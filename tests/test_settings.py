from __future__ import annotations

import pytest
from django.test import override_settings

from truelist_django.settings import get_setting


class TestGetSetting:
    def test_reads_api_key_from_django_settings(self) -> None:
        assert get_setting("TRUELIST_API_KEY") == "test-api-key"

    def test_falls_back_to_default_base_url(self) -> None:
        assert get_setting("TRUELIST_BASE_URL") == "https://api.truelist.io"

    def test_falls_back_to_default_timeout(self) -> None:
        assert get_setting("TRUELIST_TIMEOUT") == 10

    def test_falls_back_to_default_allow_risky(self) -> None:
        assert get_setting("TRUELIST_ALLOW_RISKY") is True

    def test_falls_back_to_default_cache_enabled(self) -> None:
        assert get_setting("TRUELIST_CACHE_ENABLED") is False

    def test_falls_back_to_default_cache_ttl(self) -> None:
        assert get_setting("TRUELIST_CACHE_TTL") == 3600

    def test_falls_back_to_default_cache_alias(self) -> None:
        assert get_setting("TRUELIST_CACHE_ALIAS") == "default"

    @override_settings(TRUELIST_BASE_URL="https://custom.api.io")
    def test_overrides_from_django_settings(self) -> None:
        assert get_setting("TRUELIST_BASE_URL") == "https://custom.api.io"

    @override_settings(TRUELIST_TIMEOUT=30)
    def test_overrides_timeout(self) -> None:
        assert get_setting("TRUELIST_TIMEOUT") == 30

    @override_settings(TRUELIST_ALLOW_RISKY=False)
    def test_overrides_allow_risky(self) -> None:
        assert get_setting("TRUELIST_ALLOW_RISKY") is False

    @override_settings(TRUELIST_CACHE_ENABLED=True)
    def test_overrides_cache_enabled(self) -> None:
        assert get_setting("TRUELIST_CACHE_ENABLED") is True

    def test_invalid_setting_raises_attribute_error(self) -> None:
        with pytest.raises(AttributeError, match="Invalid Truelist setting"):
            get_setting("TRUELIST_NONEXISTENT")
