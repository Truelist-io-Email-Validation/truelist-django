from __future__ import annotations

from django.apps import AppConfig


class TruelistDjangoConfig(AppConfig):
    """Django app configuration for truelist_django."""

    name = "truelist_django"
    verbose_name = "Truelist Email Validation"
    default_auto_field = "django.db.models.BigAutoField"
