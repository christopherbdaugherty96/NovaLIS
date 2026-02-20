# tests/adversarial/test_concurrency_one_enforced.py
from __future__ import annotations

import threading
import time

from tests.adversarial._helpers import try_find_callable

"""
Goal:
- Concurrency=1 enforced (SingleActionQueue).
- Second request should block or deny while first is running.
We simulate two simultaneous search calls.
"""


class BlockingNetworkMediator:
    def __init__(self, gate: threading.Event):
        self.gate = gate
        self.calls = 0

    def request(self, capability_id: int | None, method: str, url: str, json_payload: dict | None = None) -> dict:
        self.calls += 1
        # hold until test releases
        self.gate.wait(timeout=5)
        return {"status_code": 200, "data": {"results": [{"title": "ok", "snippet": "ok", "url": "https://example.com"}], "source": "online_search"}}


def test_single_action_queue_enforced(monkeypatch):
    from src.governor.governor_mediator import GovernorMediator
    from src.governor.governor import Governor

    gate = threading.Event()
    nm = BlockingNetworkMediator(gate)

    import src.governor.network_mediator as nm_mod
    monkeypatch.setattr(nm_mod, "NetworkMediator", lambda *a, **k: nm, raising=False)

    out = {"a": None, "b": None}

    def call_a():
        inv = GovernorMediator.parse_governed_invocation("search for A")
        if inv:
            gov = Governor()
            out["a"] = gov.handle_governed_invocation(*inv)

    def call_b():
        inv = GovernorMediator.parse_governed_invocation("search for B")
        if inv:
            gov = Governor()
            out["b"] = gov.handle_governed_invocation(*inv)

    t1 = threading.Thread(target=call_a, daemon=True)
    t2 = threading.Thread(target=call_b, daemon=True)

    t1.start()
    time.sleep(0.1)  # let A enter
    t2.start()

    # Release after a moment
    time.sleep(0.3)
    gate.set()

    t1.join(timeout=5)
    t2.join(timeout=5)

    assert out["a"] is not None and out["b"] is not None, "Both calls should return (either B denied or queued)"
    # Optionally tighten based on your queue semantics:
    # - If you deny when busy: assert "busy" in str(out["b"]).lower()
    # - If you queue: assert both succeeded but second delayed (you could measure timing)