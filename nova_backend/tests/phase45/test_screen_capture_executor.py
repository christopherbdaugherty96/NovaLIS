from __future__ import annotations

from types import SimpleNamespace

from src.executors.screen_capture_executor import ScreenCaptureExecutor


def _request(params: dict):
    return SimpleNamespace(params=params, request_id="req-screen-1")


class _FakeLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, payload))


class _FakeContextService:
    def capture_snapshot(self, *, request_id: str, invocation_source: str) -> dict:
        del request_id, invocation_source
        return {
            "cursor": {"x": 400, "y": 420, "screen_width": 1920, "screen_height": 1080},
            "active_window": {"title": "Python Downloads"},
            "browser": {"is_browser": True, "url": None},
            "system": {"os": "Windows"},
        }


class _FakeCaptureEngine:
    def capture_region(self, bounds: dict) -> dict:
        return {"ok": True, "image_path": "C:/tmp/capture.png", "bounds": dict(bounds)}


class _FailingCaptureEngine:
    def capture_region(self, bounds: dict) -> dict:
        del bounds
        return {"ok": False, "error": "capture unavailable"}


class _MissingDependencyCaptureEngine:
    def capture_region(self, bounds: dict) -> dict:
        del bounds
        return {
            "ok": False,
            "error": "Capture dependency unavailable: No module named 'pyautogui'",
            "failure_kind": "missing_dependency",
            "missing_dependency": "pyautogui",
        }


def test_screen_capture_executor_requires_explicit_invocation_source():
    ledger = _FakeLedger()
    executor = ScreenCaptureExecutor(
        ledger=ledger,
        context_service=_FakeContextService(),
        capture_engine=_FakeCaptureEngine(),
    )
    result = executor.execute(_request({}))
    assert result.success is False
    assert "explicit invocation source" in result.message.lower()
    assert not ledger.events


def test_screen_capture_executor_logs_requested_and_completed_on_success():
    ledger = _FakeLedger()
    executor = ScreenCaptureExecutor(
        ledger=ledger,
        context_service=_FakeContextService(),
        capture_engine=_FakeCaptureEngine(),
    )
    result = executor.execute(_request({"invocation_source": "ui", "region_size": 640}))
    assert result.success is True
    assert isinstance(result.data, dict)
    assert result.data.get("capture", {}).get("image_path") == "C:/tmp/capture.png"
    assert "Active context: Python Downloads." in result.message
    assert result.data["widget"]["data"]["follow_up_prompts"]

    event_names = [name for name, _ in ledger.events]
    assert "SCREEN_CAPTURE_REQUESTED" in event_names
    assert "SCREEN_CAPTURE_COMPLETED" in event_names
    completion = [payload for name, payload in ledger.events if name == "SCREEN_CAPTURE_COMPLETED"][-1]
    assert completion.get("success") is True


def test_screen_capture_executor_logs_failure_when_capture_fails():
    ledger = _FakeLedger()
    executor = ScreenCaptureExecutor(
        ledger=ledger,
        context_service=_FakeContextService(),
        capture_engine=_FailingCaptureEngine(),
    )
    result = executor.execute(_request({"invocation_source": "voice"}))
    assert result.success is False
    assert "screen capture is unavailable" in result.message.lower()
    assert result.data["capture_error"] == "capture unavailable"
    assert result.data["capture_bounds"]["width"] > 0
    completion = [payload for name, payload in ledger.events if name == "SCREEN_CAPTURE_COMPLETED"][-1]
    assert completion.get("success") is False


def test_screen_capture_executor_surfaces_missing_dependency_reason():
    ledger = _FakeLedger()
    executor = ScreenCaptureExecutor(
        ledger=ledger,
        context_service=_FakeContextService(),
        capture_engine=_MissingDependencyCaptureEngine(),
    )
    result = executor.execute(_request({"invocation_source": "ui"}))

    assert result.success is False
    assert "pyautogui" in result.message
    assert "missing" in result.message.lower()
    assert result.data["capture_failure_kind"] == "missing_dependency"
    assert result.data["missing_dependency"] == "pyautogui"
    assert result.data["capture_error"] == "Capture dependency unavailable: No module named 'pyautogui'"

    completion = [payload for name, payload in ledger.events if name == "SCREEN_CAPTURE_COMPLETED"][-1]
    assert completion.get("success") is False
    assert completion.get("failure_kind") == "missing_dependency"
    assert completion.get("missing_dependency") == "pyautogui"
