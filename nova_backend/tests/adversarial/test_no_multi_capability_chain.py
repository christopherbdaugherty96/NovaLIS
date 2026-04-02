from __future__ import annotations

from tests.adversarial._helpers import SRC_ROOT, read_text


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


def test_brain_server_does_not_chain_track_cluster_to_track_capability():
    # The track_cluster post-dispatch routing was extracted from brain_server.py into
    # session_handler.py as part of the session-loop refactor. Check the live location.
    source = read_text(SRC_ROOT / "websocket" / "session_handler.py")
    assert "if capability_id == 50 and params.get(\"action\") == \"track_cluster\":" in source
    assert "governor.handle_governed_invocation,\n                            52" not in source


def test_brain_server_uses_shared_web_planner_not_executor_reference():
    # plan_web_open is called from session_handler.py (where cap 17 enrichment happens)
    # not from brain_server.py directly. The governance contract holds: a shared planner
    # is used rather than referencing the executor class directly.
    session_source = read_text(SRC_ROOT / "websocket" / "session_handler.py")
    assert "plan_web_open(" in session_source
    assert "WebpageLaunchExecutor" not in session_source
