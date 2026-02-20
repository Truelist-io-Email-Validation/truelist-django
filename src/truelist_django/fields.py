from __future__ import annotations

import logging
from typing import Any

from truelist import AuthenticationError, TruelistError, ValidationResult

from truelist_django.cache import CachedTruelistClient
from truelist_django.settings import get_setting

logger = logging.getLogger(__name__)

try:
    from rest_framework import serializers

    class TruelistEmailField(serializers.EmailField):
        """DRF serializer field that validates email deliverability via the Truelist API.

        Usage::

            from rest_framework import serializers
            from truelist_django.fields import TruelistEmailField

            class SignupSerializer(serializers.Serializer):
                email = TruelistEmailField()

        Args:
            allow_risky: Accept emails with "risky" state (default: from settings, or True).
            fail_silently: If True, don't raise on API/network errors (default: True).
                Auth errors (401) always raise regardless of this setting.
            **kwargs: Additional keyword arguments passed to EmailField.
        """

        def __init__(
            self,
            *,
            allow_risky: bool | None = None,
            fail_silently: bool = True,
            **kwargs: Any,
        ) -> None:
            self.allow_risky = (
                allow_risky if allow_risky is not None else get_setting("TRUELIST_ALLOW_RISKY")
            )
            self.fail_silently = fail_silently
            super().__init__(**kwargs)

        def run_validation(self, data: Any = serializers.empty) -> Any:
            value = super().run_validation(data)

            if value is None or value == "":
                return value

            client = CachedTruelistClient()
            try:
                result: ValidationResult = client.validate(str(value))
            except AuthenticationError:
                raise
            except TruelistError:
                logger.warning("Truelist API error while validating %s", value, exc_info=True)
                if not self.fail_silently:
                    raise serializers.ValidationError(
                        "Email validation service is temporarily unavailable."
                    ) from None
                return value
            finally:
                client.close()

            if result.is_valid:
                return value

            if result.is_risky and self.allow_risky:
                return value

            if result.is_unknown:
                if self.fail_silently:
                    return value
                raise serializers.ValidationError(
                    "Email validation returned an inconclusive result."
                )

            raise serializers.ValidationError(
                "This email address could not be verified as deliverable."
            )

except ImportError:

    class TruelistEmailField:  # type: ignore[no-redef]
        """Placeholder that raises when DRF is not installed."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError(
                "djangorestframework is required to use TruelistEmailField. "
                'Install it with: pip install "truelist-django[drf]"'
            )
