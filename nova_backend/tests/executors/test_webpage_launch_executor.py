from __future__ import annotations

from types import SimpleNamespace


def _request(params: dict):
    return SimpleNamespace(params=params, request_id="req-web-1")


class _FakeLedger:
    def __init__(self):
        self.events = []

    def log_event(self, event_type: str, payload: dict):
        self.events.append((event_type, payload))


def test_plan_open_preset_no_confirmation():
    from src.executors.webpage_launch_executor import WebpageLaunchExecutor

    plan = WebpageLaunchExecutor.plan_open({"target": "github"})
    assert plan["ok"] is True
    assert plan["requires_confirmation"] is False
    assert "github" in plan["url"]


def test_plan_open_unknown_domain_requires_confirmation():
    from src.executors.webpage_launch_executor import WebpageLaunchExecutor

    plan = WebpageLaunchExecutor.plan_open({"target": "example.org"})
    assert plan["ok"] is True
    assert plan["requires_confirmation"] is True
    assert plan["domain"] == "example.org"


def test_execute_preview_returns_widget():
    from src.executors.webpage_launch_executor import WebpageLaunchExecutor

    ledger = _FakeLedger()
    executor = WebpageLaunchExecutor(ledger=ledger)
    result = executor.execute(_request({"target": "example.org", "preview": True}))

    assert result.success is True
    assert isinstance(result.data, dict)
    assert result.data["widget"]["type"] == "website_preview"
    assert any(evt[0] == "WEBPAGE_PREVIEW" for evt in ledger.events)


def test_execute_open_includes_reason_and_risk(monkeypatch):
    from src.executors.webpage_launch_executor import WebpageLaunchExecutor

    monkeypatch.setattr("src.executors.webpage_launch_executor.webbrowser.open", lambda *_: True)
    ledger = _FakeLedger()
    executor = WebpageLaunchExecutor(ledger=ledger)

    result = executor.execute(_request({"target": "github"}))
    assert result.success is True
    assert "Reason: user-invoked" in result.message
    assert "Risk: low" in result.message
    assert any(evt[0] == "WEBPAGE_LAUNCH" for evt in ledger.events)


def test_execute_open_returns_failure_when_browser_open_returns_false(monkeypatch):
    from src.executors.webpage_launch_executor import WebpageLaunchExecutor

    monkeypatch.setattr("src.executors.webpage_launch_executor.webbrowser.open", lambda *_: False)
    ledger = _FakeLedger()
    executor = WebpageLaunchExecutor(ledger=ledger)

    result = executor.execute(_request({"target": "github"}))
    assert result.success is False
    assert "Could not open the browser." in result.message
    launch_events = [evt for evt in ledger.events if evt[0] == "WEBPAGE_LAUNCH"]
    assert launch_events
    assert launch_events[-1][1].get("success") is False
