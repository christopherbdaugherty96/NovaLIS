# tests/adversarial/test_ledger_failure_blocks_execution.py
from __future__ import annotations

import pytest

from tests.adversarial._helpers import try_find_callable

"""
Goal:
- If ledger write fails, action execution must be denied (fail closed).
- We simulate ledger writer raising and verify search returns denial.
"""


class ExplodingLedger:
    def log_event(self, event_type: str, metadata: dict) -> None:
        raise IOError("simulated ledger failure")


def test_ledger_failure_denies_search(monkeypatch):
    monkeypatch.setattr(
        "src.governor.governor.Governor._check_network_budget",
        lambda self, cap_id: None,
    )
    from src.governor.governor_mediator import GovernorMediator
    from src.governor.governor import Governor

    # Patch ledger writer to explode
    import src.ledger.writer as ledger_mod
    monkeypatch.setattr(ledger_mod, "LedgerWriter", lambda *a, **k: ExplodingLedger(), raising=False)

    # Run a search
    user_text = "search for nova governance"
    invocation = GovernorMediator.parse_governed_invocation(user_text)
    assert invocation is not None
    capability_id = invocation.capability_id
    params = invocation.params

    gov = Governor()
    result = gov.handle_governed_invocation(capability_id, params)

    # Assert denial shape (expect a refusal message)
    s = str(result).lower()
    assert result.success is False
    assert ("can’t do" in s) or ("couldn't" in s) or ("fail" in s), f"Expected denial on ledger failure, got: {result}"