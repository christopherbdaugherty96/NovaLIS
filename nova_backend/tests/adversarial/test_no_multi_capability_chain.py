from __future__ import annotations


class CaptureLedger:
    def __init__(self):
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, data: dict):
        self.events.append((event_type, data))


class FakeNetworkMediator:
    def request(self, **kwargs):
        return {"status_code": 200, "data": {"RelatedTopics": []}}


def test_single_request_has_single_action_attempt(monkeypatch):
    from src.governor.governor_mediator import GovernorMediator
    from src.governor.governor import Governor

    ledger = CaptureLedger()

    import src.ledger.writer as ledger_mod
    monkeypatch.setattr(ledger_mod, "LedgerWriter", lambda *a, **k: ledger, raising=False)

    import src.governor.network_mediator as nm_mod
    monkeypatch.setattr(nm_mod, "NetworkMediator", lambda *a, **k: FakeNetworkMediator(), raising=False)

    invocation = GovernorMediator.parse_governed_invocation("search for nova")
    assert invocation is not None

    gov = Governor()
    _ = gov.handle_governed_invocation(invocation.capability_id, invocation.params)

    attempts = [d for e, d in ledger.events if e == "ACTION_ATTEMPTED"]
    completed = [d for e, d in ledger.events if e == "ACTION_COMPLETED"]

    assert len(attempts) == 1
    assert len(completed) == 1
    assert attempts[0]["capability_id"] == completed[0]["capability_id"]
