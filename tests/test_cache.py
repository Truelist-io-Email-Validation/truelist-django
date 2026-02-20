from __future__ import annotations

from unittest.mock import MagicMock, patch

from django.core.cache import caches
from django.test import override_settings
from truelist import ValidationResult

from truelist_django.cache import CachedTruelistClient, _cache_key


class TestCacheKey:
    def test_generates_consistent_key(self) -> None:
        key1 = _cache_key("user@example.com")
        key2 = _cache_key("user@example.com")
        assert key1 == key2
        assert key1.startswith("truelist:validation:")

    def test_case_insensitive(self) -> None:
        key1 = _cache_key("User@Example.com")
        key2 = _cache_key("user@example.com")
        assert key1 == key2

    def test_different_emails_different_keys(self) -> None:
        key1 = _cache_key("user@example.com")
        key2 = _cache_key("other@example.com")
        assert key1 != key2


class TestCachedTruelistClient:
    @override_settings(TRUELIST_CACHE_ENABLED=True)
    @patch("truelist_django.cache.Truelist")
    def test_caches_valid_result(
        self, mock_truelist_cls: MagicMock, valid_result: ValidationResult
    ) -> None:
        mock_client = mock_truelist_cls.return_value
        mock_client.email.validate.return_value = valid_result

        cache = caches["default"]
        cache.clear()

        client = CachedTruelistClient(cache_enabled=True)
        result1 = client.validate("user@example.com")
        result2 = client.validate("user@example.com")

        assert result1.state == "valid"
        assert result2.state == "valid"
        mock_client.email.validate.assert_called_once()

    @override_settings(TRUELIST_CACHE_ENABLED=True)
    @patch("truelist_django.cache.Truelist")
    def test_cache_miss_calls_api(
        self, mock_truelist_cls: MagicMock, valid_result: ValidationResult
    ) -> None:
        mock_client = mock_truelist_cls.return_value
        mock_client.email.validate.return_value = valid_result

        cache = caches["default"]
        cache.clear()

        client = CachedTruelistClient(cache_enabled=True)
        result = client.validate("user@example.com")

        assert result.state == "valid"
        mock_client.email.validate.assert_called_once_with("user@example.com")

    @override_settings(TRUELIST_CACHE_ENABLED=True)
    @patch("truelist_django.cache.Truelist")
    def test_does_not_cache_unknown_results(
        self, mock_truelist_cls: MagicMock, unknown_result: ValidationResult
    ) -> None:
        mock_client = mock_truelist_cls.return_value
        mock_client.email.validate.return_value = unknown_result

        cache = caches["default"]
        cache.clear()

        client = CachedTruelistClient(cache_enabled=True)
        client.validate("mystery@example.com")
        client.validate("mystery@example.com")

        assert mock_client.email.validate.call_count == 2

    @patch("truelist_django.cache.Truelist")
    def test_skips_cache_when_disabled(
        self, mock_truelist_cls: MagicMock, valid_result: ValidationResult
    ) -> None:
        mock_client = mock_truelist_cls.return_value
        mock_client.email.validate.return_value = valid_result

        client = CachedTruelistClient(cache_enabled=False)
        client.validate("user@example.com")
        client.validate("user@example.com")

        assert mock_client.email.validate.call_count == 2

    @override_settings(TRUELIST_CACHE_ENABLED=True)
    @patch("truelist_django.cache.Truelist")
    def test_caches_invalid_result(
        self, mock_truelist_cls: MagicMock, invalid_result: ValidationResult
    ) -> None:
        mock_client = mock_truelist_cls.return_value
        mock_client.email.validate.return_value = invalid_result

        cache = caches["default"]
        cache.clear()

        client = CachedTruelistClient(cache_enabled=True)
        result1 = client.validate("bad@example.com")
        result2 = client.validate("bad@example.com")

        assert result1.state == "invalid"
        assert result2.state == "invalid"
        mock_client.email.validate.assert_called_once()

    @override_settings(TRUELIST_CACHE_ENABLED=True)
    @patch("truelist_django.cache.Truelist")
    def test_caches_risky_result(
        self, mock_truelist_cls: MagicMock, risky_result: ValidationResult
    ) -> None:
        mock_client = mock_truelist_cls.return_value
        mock_client.email.validate.return_value = risky_result

        cache = caches["default"]
        cache.clear()

        client = CachedTruelistClient(cache_enabled=True)
        result1 = client.validate("risky@example.com")
        result2 = client.validate("risky@example.com")

        assert result1.state == "risky"
        assert result2.state == "risky"
        mock_client.email.validate.assert_called_once()

    @patch("truelist_django.cache.Truelist")
    def test_close_closes_underlying_client(
        self, mock_truelist_cls: MagicMock, valid_result: ValidationResult
    ) -> None:
        mock_client = mock_truelist_cls.return_value
        mock_client.email.validate.return_value = valid_result

        client = CachedTruelistClient(cache_enabled=False)
        client.validate("user@example.com")
        client.close()

        mock_client.close.assert_called_once()

    @patch("truelist_django.cache.Truelist")
    def test_close_without_client_is_noop(self, mock_truelist_cls: MagicMock) -> None:
        client = CachedTruelistClient(cache_enabled=False)
        client.close()
        mock_truelist_cls.return_value.close.assert_not_called()

    def test_uses_settings_defaults(self) -> None:
        client = CachedTruelistClient()
        assert client._api_key == "test-api-key"
        assert client._base_url == "https://api.truelist.io"
        assert client._timeout == 10
        assert client._cache_enabled is False
