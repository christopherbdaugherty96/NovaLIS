# tests/adversarial/test_execute_boundary_timeouts_fail_closed.py
from __future__ import annotations

from src.governor.exceptions import NetworkMediatorError


class SlowNetworkMediator:
    def __init__(self):
        self.calls = 0

    def request(self, capability_id: int | None, method: str, url: str, json_payload: dict | None = None, **kwargs) -> dict:
        self.calls += 1
        raise NetworkMediatorError("timeout")


class CaptureLedger:
    def __init__(self):
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, data: dict):
        self.events.append((event_type, data))


def test_timeout_causes_denial_and_records_lifecycle(monkeypatch):
    monkeypatch.setattr(
        "src.governor.governor.Governor._check_network_budget",
        lambda self, cap_id: None,
    )
    monkeypatch.setenv("BRAVE_API_KEY", "test-key")
    from src.governor.governor_mediator import GovernorMediator
    from src.governor.governor import Governor

    slow = SlowNetworkMediator()
    ledger = CaptureLedger()

    import src.governor.network_mediator as nm_mod
    monkeypatch.setattr(nm_mod, "NetworkMediator", lambda *a, **k: slow, raising=False)

    import src.ledger.writer as ledger_mod
    monkeypatch.setattr(ledger_mod, "LedgerWriter", lambda *a, **k: ledger, raising=False)

    invocation = GovernorMediator.parse_governed_invocation("search for current weather")
    assert invocation is not None

    gov = Governor()
    result = gov.handle_governed_invocation(invocation.capability_id, invocation.params)

    assert slow.calls == 2, "Expected bounded retry behavior (1 initial + 1 retry)"
    assert result.success is False
    assert result.data["widget"]["type"] == "search"
    widget_data = result.data["widget"]["data"]
    assert widget_data["results"] == []
    assert widget_data["query"] == "current weather"
    assert widget_data["result_count"] == 0

    event_types = [event for event, _ in ledger.events]
    assert event_types.count("ACTION_ATTEMPTED") == 1
    assert event_types.count("ACTION_COMPLETED") == 1
    completed = [data for event, data in ledger.events if event == "ACTION_COMPLETED"][0]
    assert completed["success"] is False
