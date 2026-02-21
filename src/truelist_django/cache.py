from __future__ import annotations

import hashlib
from typing import Any

from django.core.cache import caches
from truelist import Truelist, ValidationResult

from truelist_django.settings import get_setting


def _cache_key(email: str) -> str:
    """Generate a cache key for an email address."""
    email_hash = hashlib.sha256(email.lower().strip().encode()).hexdigest()
    return f"truelist:validation:{email_hash}"


class CachedTruelistClient:
    """Truelist client wrapper that caches validation results using Django's cache framework.

    Caching is controlled by Django settings:
        - TRUELIST_CACHE_ENABLED: Whether caching is active (default: False)
        - TRUELIST_CACHE_TTL: Cache duration in seconds (default: 3600)
        - TRUELIST_CACHE_ALIAS: Which Django cache backend to use (default: "default")

    Results with state "unknown" are never cached.

    Usage::

        client = CachedTruelistClient()
        result = client.validate("user@example.com")
    """

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
        cache_enabled: bool | None = None,
        cache_ttl: int | None = None,
        cache_alias: str | None = None,
    ) -> None:
        self._api_key = api_key or get_setting("TRUELIST_API_KEY")
        self._base_url = base_url or get_setting("TRUELIST_BASE_URL")
        self._timeout: int = timeout if timeout is not None else get_setting("TRUELIST_TIMEOUT")
        self._cache_enabled = (
            cache_enabled if cache_enabled is not None else get_setting("TRUELIST_CACHE_ENABLED")
        )
        self._cache_ttl: int = (
            cache_ttl if cache_ttl is not None else get_setting("TRUELIST_CACHE_TTL")
        )
        self._cache_alias: str = cache_alias or get_setting("TRUELIST_CACHE_ALIAS")
        self._client: Truelist | None = None

    def _get_client(self) -> Truelist:
        if self._client is None:
            self._client = Truelist(
                self._api_key,
                base_url=self._base_url,
                timeout=float(self._timeout),
            )
        return self._client

    def _get_cache(self) -> Any:
        return caches[self._cache_alias]

    def validate(self, email: str) -> ValidationResult:
        """Validate an email address, using cache if enabled.

        Args:
            email: The email address to validate.

        Returns:
            A ValidationResult from the Truelist API or cache.
        """
        if self._cache_enabled:
            key = _cache_key(email)
            cache = self._get_cache()
            cached: dict[str, Any] | None = cache.get(key)
            if cached is not None:
                return ValidationResult(**cached)

        result = self._get_client().email.validate(email)

        if self._cache_enabled and not result.is_unknown:
            key = _cache_key(email)
            cache = self._get_cache()
            cache.set(
                key,
                {
                    "email": result.email,
                    "domain": result.domain,
                    "canonical": result.canonical,
                    "mx_record": result.mx_record,
                    "first_name": result.first_name,
                    "last_name": result.last_name,
                    "state": result.state,
                    "sub_state": result.sub_state,
                    "verified_at": result.verified_at,
                    "suggestion": result.suggestion,
                },
                self._cache_ttl,
            )

        return result

    def close(self) -> None:
        """Close the underlying HTTP client."""
        if self._client is not None:
            self._client.close()
            self._client = None
