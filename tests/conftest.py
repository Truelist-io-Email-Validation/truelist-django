from __future__ import annotations

import pytest
from truelist import ValidationResult


@pytest.fixture
def valid_result() -> ValidationResult:
    return ValidationResult(
        email="user@example.com",
        state="valid",
        sub_state="ok",
        free_email=False,
        role=False,
        disposable=False,
        suggestion=None,
    )


@pytest.fixture
def invalid_result() -> ValidationResult:
    return ValidationResult(
        email="bad@example.com",
        state="invalid",
        sub_state="failed_no_mailbox",
        free_email=False,
        role=False,
        disposable=False,
        suggestion=None,
    )


@pytest.fixture
def risky_result() -> ValidationResult:
    return ValidationResult(
        email="risky@example.com",
        state="risky",
        sub_state="accept_all",
        free_email=False,
        role=False,
        disposable=False,
        suggestion=None,
    )


@pytest.fixture
def unknown_result() -> ValidationResult:
    return ValidationResult(
        email="mystery@example.com",
        state="unknown",
        sub_state="unknown",
        free_email=False,
        role=False,
        disposable=False,
        suggestion=None,
    )
