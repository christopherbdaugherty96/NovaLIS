# tests/adversarial/test_execute_boundary_timeouts_fail_closed.py
from __future__ import annotations

import time
import pytest

from tests.adversarial._helpers import try_find_callable

"""
Goal:
- NetworkMediator timeout (or ExecuteBoundary timeout) causes fail-closed behavior.
- No retries, no partial execution, no crash.
"""


class SlowNetworkMediator:
    def __init__(self):
        self.calls = 0

    def request(self, capability_id: int | None, method: str, url: str, json_payload: dict | None = None, **kwargs) -> dict:
        self.calls += 1
        time.sleep(10.0)  # exceed your 5s network cap
        return {"status_code": 200, "data": {"results": [], "source": "online_search"}}


def test_timeout_causes_denial(monkeypatch):
    from src.governor.governor_mediator import GovernorMediator
    from src.governor.governor import Governor

    slow = SlowNetworkMediator()

    # Patch NetworkMediator
    import src.governor.network_mediator as nm_mod
    monkeypatch.setattr(nm_mod, "NetworkMediator", lambda *a, **k: slow, raising=False)

    user_text = "search for current weather"
    invocation = GovernorMediator.parse_governed_invocation(user_text)
    assert invocation is not None
    capability_id = invocation.capability_id
    params = invocation.params

    gov = Governor()
    result = gov.handle_governed_invocation(capability_id, params)

    s = str(result).lower()
    assert slow.calls == 1, "Must not retry implicitly on timeout"
    assert result is not None
    assert ("checking online" in s) or ("can’t do" in s) or ("timeout" in s) or ("fail" in s), f"Unexpected result: {result}"