# tests/certification/cap_16_governed_web_search/conftest.py
"""
Shared fixtures for Cap 16 certification tests.

The P3 integration tests invoke the full Governor spine including the budget
gate in governor.py.  The gate reads live runtime state from
provider_usage_store, which can exhaust during a long development session and
cause integration tests to fail even though the code is correct.

This conftest patches the budget snapshot to "normal" for all tests in this
directory so they are deterministic regardless of session token usage.
"""
from __future__ import annotations

from unittest.mock import patch

import pytest

# Import the singleton directly — patch.object targets the live instance.
from src.usage.provider_usage_store import provider_usage_store as _budget_store

_NORMAL_BUDGET = {
    "budget_state": "normal",
    "budget_remaining_tokens": 10_000,
    "budget_state_label": "Normal",
    "budget_tokens": 12_000,
    "estimated_total_tokens": 2_000,
    "event_count": 0,
    "summary": "Budget normal (test fixture).",
}


@pytest.fixture(autouse=True)
def _bypass_token_budget():
    """Patch the provider_usage_store singleton so budget state is always 'normal'."""
    with patch.object(_budget_store, "snapshot", return_value=_NORMAL_BUDGET):
        yield
