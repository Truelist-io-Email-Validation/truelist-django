from __future__ import annotations

import logging
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from truelist import AuthenticationError, TruelistError, ValidationResult

from truelist_django.cache import CachedTruelistClient
from truelist_django.settings import get_setting

logger = logging.getLogger(__name__)


@deconstructible
class TruelistEmailValidator:
    """Django validator that checks email deliverability via the Truelist API.

    Usage::

        from django.db import models
        from truelist_django.validators import TruelistEmailValidator

        class User(models.Model):
            email = models.EmailField(validators=[TruelistEmailValidator()])

    Args:
        allow_risky: Accept emails with "risky" state (default: from settings, or True).
        fail_silently: If True, don't raise on API/network errors (default: True).
            Auth errors (401) always raise regardless of this setting.
        message: Custom error message for invalid emails.
        code: Error code for the ValidationError (default: "invalid_email").
    """

    message = "This email address could not be verified as deliverable."
    code = "invalid_email"

    def __init__(
        self,
        *,
        allow_risky: bool | None = None,
        fail_silently: bool = True,
        message: str | None = None,
        code: str | None = None,
    ) -> None:
        self.allow_risky = (
            allow_risky if allow_risky is not None else get_setting("TRUELIST_ALLOW_RISKY")
        )
        self.fail_silently = fail_silently
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value: Any) -> None:
        client = CachedTruelistClient()
        try:
            result: ValidationResult = client.validate(str(value))
        except AuthenticationError:
            raise
        except TruelistError:
            logger.warning("Truelist API error while validating %s", value, exc_info=True)
            if not self.fail_silently:
                raise ValidationError(
                    "Email validation service is temporarily unavailable.",
                    code="service_unavailable",
                ) from None
            return
        finally:
            client.close()

        if result.is_valid:
            return

        if result.is_risky and self.allow_risky:
            return

        if result.is_unknown:
            if self.fail_silently:
                return
            raise ValidationError(
                "Email validation returned an inconclusive result.",
                code="unknown_email",
            )

        raise ValidationError(self.message, code=self.code)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TruelistEmailValidator):
            return NotImplemented
        return (
            self.allow_risky == other.allow_risky
            and self.fail_silently == other.fail_silently
            and self.message == other.message
            and self.code == other.code
        )
