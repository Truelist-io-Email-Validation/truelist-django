from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from django.core.exceptions import ValidationError
from truelist import AuthenticationError, ConnectionError, ValidationResult

from truelist_django.validators import TruelistEmailValidator


class TestTruelistEmailValidator:
    @patch("truelist_django.validators.CachedTruelistClient")
    def test_valid_email_passes(
        self, mock_client_cls: MagicMock, valid_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = valid_result

        validator = TruelistEmailValidator()
        validator("user@example.com")

        mock_client.validate.assert_called_once_with("user@example.com")
        mock_client.close.assert_called_once()

    @patch("truelist_django.validators.CachedTruelistClient")
    def test_invalid_email_raises(
        self, mock_client_cls: MagicMock, invalid_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = invalid_result

        validator = TruelistEmailValidator()
        with pytest.raises(ValidationError) as exc_info:
            validator("bad@example.com")

        assert exc_info.value.code == "invalid_email"
        mock_client.close.assert_called_once()

    @patch("truelist_django.validators.CachedTruelistClient")
    def test_risky_email_passes_when_allow_risky_true(
        self, mock_client_cls: MagicMock, risky_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = risky_result

        validator = TruelistEmailValidator(allow_risky=True)
        validator("risky@example.com")

        mock_client.validate.assert_called_once_with("risky@example.com")

    @patch("truelist_django.validators.CachedTruelistClient")
    def test_risky_email_raises_when_allow_risky_false(
        self, mock_client_cls: MagicMock, risky_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = risky_result

        validator = TruelistEmailValidator(allow_risky=False)
        with pytest.raises(ValidationError) as exc_info:
            validator("risky@example.com")

        assert exc_info.value.code == "invalid_email"

    @patch("truelist_django.validators.CachedTruelistClient")
    def test_unknown_email_passes_when_fail_silently_true(
        self, mock_client_cls: MagicMock, unknown_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = unknown_result

        validator = TruelistEmailValidator(fail_silently=True)
        validator("mystery@example.com")

    @patch("truelist_django.validators.CachedTruelistClient")
    def test_unknown_email_raises_when_fail_silently_false(
        self, mock_client_cls: MagicMock, unknown_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = unknown_result

        validator = TruelistEmailValidator(fail_silently=False)
        with pytest.raises(ValidationError) as exc_info:
            validator("mystery@example.com")

        assert exc_info.value.code == "unknown_email"

    @patch("truelist_django.validators.CachedTruelistClient")
    def test_api_error_passes_when_fail_silently_true(self, mock_client_cls: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.side_effect = ConnectionError("timeout")

        validator = TruelistEmailValidator(fail_silently=True)
        validator("user@example.com")

    @patch("truelist_django.validators.CachedTruelistClient")
    def test_api_error_raises_when_fail_silently_false(self, mock_client_cls: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.side_effect = ConnectionError("timeout")

        validator = TruelistEmailValidator(fail_silently=False)
        with pytest.raises(ValidationError) as exc_info:
            validator("user@example.com")

        assert exc_info.value.code == "service_unavailable"

    @patch("truelist_django.validators.CachedTruelistClient")
    def test_auth_error_always_raises(self, mock_client_cls: MagicMock) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.side_effect = AuthenticationError("Invalid API key", status_code=401)

        validator = TruelistEmailValidator(fail_silently=True)
        with pytest.raises(AuthenticationError):
            validator("user@example.com")

    @patch("truelist_django.validators.CachedTruelistClient")
    def test_custom_message_and_code(
        self, mock_client_cls: MagicMock, invalid_result: ValidationResult
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.validate.return_value = invalid_result

        validator = TruelistEmailValidator(message="Bad email!", code="bad_email")
        with pytest.raises(ValidationError) as exc_info:
            validator("bad@example.com")

        assert exc_info.value.code == "bad_email"
        assert "Bad email!" in str(exc_info.value.message)

    def test_equality(self) -> None:
        v1 = TruelistEmailValidator(allow_risky=True, fail_silently=True)
        v2 = TruelistEmailValidator(allow_risky=True, fail_silently=True)
        v3 = TruelistEmailValidator(allow_risky=False, fail_silently=True)

        assert v1 == v2
        assert v1 != v3

    def test_deconstructible(self) -> None:
        validator = TruelistEmailValidator(allow_risky=False, fail_silently=False)
        path, args, kwargs = validator.deconstruct()

        assert "TruelistEmailValidator" in path
        assert args == ()
        assert kwargs["allow_risky"] is False
        assert kwargs["fail_silently"] is False
