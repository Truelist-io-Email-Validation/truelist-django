from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from rest_framework import serializers
from truelist import AuthenticationError, ConnectionError, ValidationResult

from truelist_django.fields import TruelistEmailField


class SimpleSerializer(serializers.Serializer):  # type: ignore[type-arg]
    email = TruelistEmailField()


class FailLoudSerializer(serializers.Serializer):  # type: ignore[type-arg]
    email = TruelistEmailField(fail_silently=False)


class NoRiskySerializer(serializers.Serializer):  # type: ignore[type-arg]
    email = TruelistEmailField(allow_risky=False)


class TestTruelistEmailField:
    @patch("truelist_django.fields.CachedTruelistClient")
    def test_valid_email_passes(
        self, mock_client_cls: MagicMock, valid_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = valid_result

        s = SimpleSerializer(data={"email": "user@example.com"})
        assert s.is_valid(), s.errors

        mock_client.validate.assert_called_once_with("user@example.com")
        mock_client.close.assert_called_once()

    @patch("truelist_django.fields.CachedTruelistClient")
    def test_invalid_email_fails(
        self, mock_client_cls: MagicMock, invalid_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = invalid_result

        s = SimpleSerializer(data={"email": "bad@example.com"})
        assert not s.is_valid()
        assert "email" in s.errors

    @patch("truelist_django.fields.CachedTruelistClient")
    def test_risky_email_passes_by_default(
        self, mock_client_cls: MagicMock, risky_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = risky_result

        s = SimpleSerializer(data={"email": "risky@example.com"})
        assert s.is_valid(), s.errors

    @patch("truelist_django.fields.CachedTruelistClient")
    def test_risky_email_fails_when_disallowed(
        self, mock_client_cls: MagicMock, risky_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = risky_result

        s = NoRiskySerializer(data={"email": "risky@example.com"})
        assert not s.is_valid()
        assert "email" in s.errors

    @patch("truelist_django.fields.CachedTruelistClient")
    def test_api_error_passes_when_fail_silently(self, mock_client_cls: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.side_effect = ConnectionError("timeout")

        s = SimpleSerializer(data={"email": "user@example.com"})
        assert s.is_valid(), s.errors

    @patch("truelist_django.fields.CachedTruelistClient")
    def test_api_error_fails_when_not_fail_silently(self, mock_client_cls: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.side_effect = ConnectionError("timeout")

        s = FailLoudSerializer(data={"email": "user@example.com"})
        assert not s.is_valid()
        assert "email" in s.errors

    @patch("truelist_django.fields.CachedTruelistClient")
    def test_auth_error_always_raises(self, mock_client_cls: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.side_effect = AuthenticationError("Invalid API key", status_code=401)

        s = SimpleSerializer(data={"email": "user@example.com"})
        with pytest.raises(AuthenticationError):
            s.is_valid(raise_exception=True)

    @patch("truelist_django.fields.CachedTruelistClient")
    def test_unknown_email_passes_when_fail_silently(
        self, mock_client_cls: MagicMock, unknown_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = unknown_result

        s = SimpleSerializer(data={"email": "mystery@example.com"})
        assert s.is_valid(), s.errors

    @patch("truelist_django.fields.CachedTruelistClient")
    def test_unknown_email_fails_when_not_fail_silently(
        self, mock_client_cls: MagicMock, unknown_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = unknown_result

        s = FailLoudSerializer(data={"email": "mystery@example.com"})
        assert not s.is_valid()
        assert "email" in s.errors

    def test_invalid_format_rejected(self) -> None:
        s = SimpleSerializer(data={"email": "not-an-email"})
        assert not s.is_valid()
        assert "email" in s.errors
