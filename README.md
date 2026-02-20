# truelist-django

Django integration for the [Truelist](https://truelist.io) email validation API. Provides a Django model field validator, a DRF serializer field, and caching via Django's cache framework.

Built on top of the [truelist](https://github.com/truelist/truelist-python) Python SDK.

## Installation

```bash
pip install truelist-django
```

With DRF support:

```bash
pip install "truelist-django[drf]"
```

## Quick Start

Add your API key to Django settings:

```python
# settings.py
TRUELIST_API_KEY = "your-api-key"
```

### Django Validator

Use `TruelistEmailValidator` on any model field:

```python
from django.db import models
from truelist_django.validators import TruelistEmailValidator

class User(models.Model):
    email = models.EmailField(
        validators=[TruelistEmailValidator()]
    )
```

With options:

```python
class User(models.Model):
    email = models.EmailField(
        validators=[TruelistEmailValidator(
            allow_risky=True,      # Accept accept-all domains (default: True)
            fail_silently=True,    # Don't block on API errors (default: True)
        )]
    )
```

The validator is `@deconstructible`, so it works in Django migrations.

### DRF Serializer Field

Use `TruelistEmailField` in any DRF serializer:

```python
from rest_framework import serializers
from truelist_django.fields import TruelistEmailField

class SignupSerializer(serializers.Serializer):
    email = TruelistEmailField()
```

With options:

```python
class SignupSerializer(serializers.Serializer):
    email = TruelistEmailField(
        allow_risky=False,
        fail_silently=True,
    )
```

## Settings Reference

All settings are optional except `TRUELIST_API_KEY`.

| Setting | Default | Description |
|---------|---------|-------------|
| `TRUELIST_API_KEY` | `""` | Your Truelist API key (required) |
| `TRUELIST_BASE_URL` | `"https://api.truelist.io"` | API base URL |
| `TRUELIST_TIMEOUT` | `10` | Request timeout in seconds |
| `TRUELIST_ALLOW_RISKY` | `True` | Accept emails with "risky" state by default |
| `TRUELIST_CACHE_ENABLED` | `False` | Enable caching of validation results |
| `TRUELIST_CACHE_TTL` | `3600` | Cache duration in seconds |
| `TRUELIST_CACHE_ALIAS` | `"default"` | Which Django cache backend to use |

## Caching

Enable caching to reduce API calls for repeated validations:

```python
# settings.py
TRUELIST_CACHE_ENABLED = True
TRUELIST_CACHE_TTL = 3600  # 1 hour
TRUELIST_CACHE_ALIAS = "default"
```

When caching is enabled, validation results are stored in Django's cache framework. Results with `unknown` state are never cached, so they are always re-validated.

You can also use the cached client directly:

```python
from truelist_django.cache import CachedTruelistClient

client = CachedTruelistClient()
result = client.validate("user@example.com")
print(result.state)  # "valid", "invalid", "risky", or "unknown"
```

## Validation States

The Truelist API returns one of four states:

| State | Description | Default Behavior |
|-------|-------------|-----------------|
| `valid` | Email is deliverable | Passes validation |
| `invalid` | Email is not deliverable | Fails validation |
| `risky` | Email may be deliverable (accept-all domain) | Passes when `allow_risky=True` (default) |
| `unknown` | Could not determine deliverability | Passes when `fail_silently=True` (default) |

Authentication errors (401) always raise, regardless of `fail_silently`.

## Error Handling

By default (`fail_silently=True`), API errors and network issues are logged and the email passes validation. This prevents your forms from breaking when the Truelist API is unavailable.

Set `fail_silently=False` to reject emails when the API cannot be reached.

Authentication errors (invalid API key) always raise immediately, regardless of `fail_silently`.

## Testing

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
```

## Compatibility

- Python 3.9+
- Django 4.2, 5.0, 5.1
- DRF 3.14+ (optional)

## License

MIT
