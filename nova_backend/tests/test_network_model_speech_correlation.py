from __future__ import annotations

from types import SimpleNamespace


def test_network_mediator_logs_request_and_session_ids(monkeypatch):
    from src.governor.network_mediator import NetworkMediator

    events: list[tuple[str, dict]] = []

    class _FakeRegistry:
        def get(self, capability_id: int):
            return SimpleNamespace(id=capability_id)

        def is_enabled(self, capability_id: int) -> bool:
            return True

    class _Response:
        status_code = 200
        is_redirect = False
        is_permanent_redirect = False
        headers: dict[str, str] = {}
        content = b"{}"
        text = "{}"

        @staticmethod
        def json() -> dict:
            return {}

        @staticmethod
        def raise_for_status() -> None:
            return None

    mediator = NetworkMediator()
    mediator._registry = _FakeRegistry()
    mediator.ledger = SimpleNamespace(log_event=lambda event, meta: events.append((event, dict(meta))))

    monkeypatch.setattr("src.governor.network_mediator.requests.request", lambda **kwargs: _Response())

    result = mediator.request(
        capability_id=16,
        method="GET",
        url="https://example.com",
        as_json=True,
        request_id="req-corr-1",
        session_id="sess-corr-1",
    )

    assert result["status_code"] == 200
    assert events
    event_name, metadata = events[-1]
    assert event_name == "EXTERNAL_NETWORK_CALL"
    assert metadata.get("request_id") == "req-corr-1"
    assert metadata.get("session_id") == "sess-corr-1"


def test_model_network_mediator_logs_request_and_session_ids(monkeypatch):
    from src.llm.model_network_mediator import ModelNetworkMediator

    events: list[tuple[str, dict]] = []

    class _Response:
        status_code = 200
        content = b'{"ok": true}'

        @staticmethod
        def json() -> dict:
            return {"ok": True}

        @staticmethod
        def raise_for_status() -> None:
            return None

    mediator = ModelNetworkMediator()
    mediator._ledger = SimpleNamespace(log_event=lambda event, meta: events.append((event, dict(meta))))
    mediator._session = SimpleNamespace(request=lambda **kwargs: _Response())

    result = mediator.request_json(
        method="POST",
        url="http://localhost:11434/api/chat",
        json_payload={"ping": "pong"},
        timeout=2.0,
        request_id="req-corr-2",
        session_id="sess-corr-2",
    )

    assert result.status_code == 200
    assert events
    event_name, metadata = events[-1]
    assert event_name == "MODEL_NETWORK_CALL"
    assert metadata.get("request_id") == "req-corr-2"
    assert metadata.get("session_id") == "sess-corr-2"


def test_tts_capability_logs_request_and_session_ids(monkeypatch):
    from src.actions.action_request import ActionRequest
    from src.executors import tts_executor as mod

    events: list[tuple[str, dict]] = []
    monkeypatch.setattr(mod.TTSEngine, "speak", lambda text: None)
    monkeypatch.setattr(
        mod,
        "LedgerWriter",
        lambda: SimpleNamespace(log_event=lambda event, meta: events.append((event, dict(meta)))),
    )

    req = ActionRequest(
        request_id="req-corr-3",
        capability_id=18,
        params={"text": "Hello", "session_id": "sess-corr-3"},
    )
    result = mod.execute_tts(req)

    assert result.success is True
    assert events
    event_name, metadata = events[-1]
    assert event_name == "SPEECH_RENDERED"
    assert metadata.get("request_id") == "req-corr-3"
    assert metadata.get("session_id") == "sess-corr-3"
