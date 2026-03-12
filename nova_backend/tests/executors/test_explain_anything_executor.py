from __future__ import annotations

from types import SimpleNamespace

from src.actions.action_result import ActionResult
from src.executors.explain_anything_executor import ExplainAnythingExecutor


def _request(params: dict):
    return SimpleNamespace(params=params, request_id="req-explain-1")


class _FakeLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, payload))


class _FakeContextService:
    def __init__(self, snapshot: dict):
        self.snapshot = snapshot

    def capture_snapshot(self, *, request_id: str, invocation_source: str) -> dict:
        del request_id, invocation_source
        return dict(self.snapshot)


class _FakeScreenAnalysisExecutor:
    def __init__(self) -> None:
        self.last_params = {}

    def execute(self, request) -> ActionResult:
        self.last_params = dict(request.params or {})
        return ActionResult.ok(
            message="Delegated screen explanation.",
            data={
                "context_snapshot": dict((request.params or {}).get("context_snapshot") or {}),
                "widget": {"type": "screen_analysis", "data": {"summary": "ok"}},
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )


def test_explain_anything_requires_invocation_source():
    ledger = _FakeLedger()
    executor = ExplainAnythingExecutor(
        ledger=ledger,
        context_service=_FakeContextService({}),
        screen_analysis_executor=_FakeScreenAnalysisExecutor(),
    )
    result = executor.execute(_request({}))
    assert result.success is False
    assert "invocation source" in result.message.lower()
    event_names = [name for name, _ in ledger.events]
    assert "EXPLAIN_ANYTHING_REQUESTED" in event_names
    assert "EXPLAIN_ANYTHING_COMPLETED" in event_names


def test_explain_anything_delegates_to_screen_analysis_when_context_available():
    snapshot = {
        "cursor": {"x": 100, "y": 100, "screen_width": 1920, "screen_height": 1080},
        "browser": {"is_browser": False},
        "active_window": {"title": "Terminal"},
        "system": {"os": "Windows"},
    }
    ledger = _FakeLedger()
    executor = ExplainAnythingExecutor(
        ledger=ledger,
        context_service=_FakeContextService(snapshot),
        screen_analysis_executor=_FakeScreenAnalysisExecutor(),
    )
    result = executor.execute(_request({"invocation_source": "voice", "query": "explain this"}))
    assert result.success is True
    assert "delegated" in result.message.lower()
    assert result.data["widget"]["type"] == "screen_analysis"
    completion = [payload for name, payload in ledger.events if name == "EXPLAIN_ANYTHING_COMPLETED"][-1]
    assert completion.get("success") is True
    assert completion.get("route") in {"screen", "webpage"}


def test_explain_anything_file_route_summarizes_module_not_found(tmp_path):
    target = tmp_path / "error.log"
    target.write_text("Traceback...\nModuleNotFoundError: No module named 'requests'\n", encoding="utf-8")

    snapshot = {
        "cursor": {"x": 0, "y": 0, "screen_width": 0, "screen_height": 0},
        "browser": {"is_browser": False},
    }
    ledger = _FakeLedger()
    executor = ExplainAnythingExecutor(
        ledger=ledger,
        context_service=_FakeContextService(snapshot),
        screen_analysis_executor=_FakeScreenAnalysisExecutor(),
    )
    result = executor.execute(
        _request({"invocation_source": "text", "file_path": str(target), "query": "what is this error"})
    )
    assert result.success is True
    assert "pip install requests" in result.message
    assert result.data["widget"]["type"] == "file_explanation"
    completion = [payload for name, payload in ledger.events if name == "EXPLAIN_ANYTHING_COMPLETED"][-1]
    assert completion.get("success") is True
    assert completion.get("route") == "file"


def test_explain_anything_file_route_limits_large_file_reads(tmp_path):
    target = tmp_path / "large.txt"
    target.write_text("a" * 150000, encoding="utf-8")

    executor = ExplainAnythingExecutor(
        ledger=_FakeLedger(),
        context_service=_FakeContextService({"cursor": {"screen_width": 0, "screen_height": 0}, "browser": {"is_browser": False}}),
        screen_analysis_executor=_FakeScreenAnalysisExecutor(),
    )
    result = executor.execute(_request({"invocation_source": "text", "file_path": str(target)}))
    assert result.success is True
    assert "first 120000 characters" in result.message


def test_explain_anything_uses_working_context_selected_file_when_direct_path_missing(tmp_path):
    target = tmp_path / "notes.md"
    target.write_text("This is a release note document.", encoding="utf-8")

    executor = ExplainAnythingExecutor(
        ledger=_FakeLedger(),
        context_service=_FakeContextService({"cursor": {"screen_width": 0, "screen_height": 0}, "browser": {"is_browser": False}}),
        screen_analysis_executor=_FakeScreenAnalysisExecutor(),
    )
    result = executor.execute(
        _request(
            {
                "invocation_source": "text",
                "query": "explain this",
                "working_context": {"selected_file": str(target)},
            }
        )
    )
    assert result.success is True
    assert "File explanation" in result.message
    assert result.data.get("analysis", {}).get("file_path") == str(target)


def test_explain_anything_uses_working_context_goal_when_query_missing():
    snapshot = {
        "cursor": {"x": 140, "y": 120, "screen_width": 1920, "screen_height": 1080},
        "browser": {"is_browser": True, "page_title": "Python Downloads"},
        "active_window": {"title": "Python Downloads", "app": "Chrome"},
        "system": {"os": "Windows"},
    }
    screen = _FakeScreenAnalysisExecutor()
    executor = ExplainAnythingExecutor(
        ledger=_FakeLedger(),
        context_service=_FakeContextService(snapshot),
        screen_analysis_executor=screen,
    )
    result = executor.execute(
        _request(
            {
                "invocation_source": "ui",
                "working_context": {"task_goal": "which one should i download"},
            }
        )
    )
    assert result.success is True
    assert screen.last_params.get("query") == "which one should i download"
