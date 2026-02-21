from __future__ import annotations

import pytest
from truelist import ValidationResult


@pytest.fixture
def valid_result() -> ValidationResult:
    return ValidationResult(
        email="user@example.com",
        domain="example.com",
        canonical="user",
        mx_record=None,
        first_name=None,
        last_name=None,
        state="ok",
        sub_state="email_ok",
        verified_at=None,
        suggestion=None,
    )


@pytest.fixture
def invalid_result() -> ValidationResult:
    return ValidationResult(
        email="bad@example.com",
        domain="example.com",
        canonical="bad",
        mx_record=None,
        first_name=None,
        last_name=None,
        state="email_invalid",
        sub_state="failed_no_mailbox",
        verified_at=None,
        suggestion=None,
    )


@pytest.fixture
def risky_result() -> ValidationResult:
    return ValidationResult(
        email="risky@example.com",
        domain="example.com",
        canonical="risky",
        mx_record=None,
        first_name=None,
        last_name=None,
        state="risky",
        sub_state="accept_all",
        verified_at=None,
        suggestion=None,
    )


@pytest.fixture
def unknown_result() -> ValidationResult:
    return ValidationResult(
        email="mystery@example.com",
        domain="example.com",
        canonical="mystery",
        mx_record=None,
        first_name=None,
        last_name=None,
        state="unknown",
        sub_state="unknown",
        verified_at=None,
        suggestion=None,
    )
