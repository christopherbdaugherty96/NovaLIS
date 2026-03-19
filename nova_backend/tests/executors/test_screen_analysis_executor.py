from __future__ import annotations

from types import SimpleNamespace

from src.actions.action_result import ActionResult
from src.executors.screen_analysis_executor import ScreenAnalysisExecutor


def _request(params: dict):
    return SimpleNamespace(params=params, request_id="req-screen-analysis-1")


class _FakeLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, payload))


class _SuccessfulCaptureExecutor:
    def execute(self, request) -> ActionResult:
        del request
        payload = {
            "context_snapshot": {
                "active_window": {"title": "Python Downloads", "app": "Chrome"},
                "browser": {"url": "https://www.python.org/downloads/", "is_browser": True},
            },
            "capture": {
                "image_path": "C:/tmp/capture.png",
                "bounds": {"left": 10, "top": 20, "width": 400, "height": 300},
            },
        }
        return ActionResult.ok(
            "Captured the screen region around your cursor.",
            data=payload,
            structured_data=payload,
            speakable_text="Screen region captured.",
            request_id="req-screen-analysis-1",
        )


class _FailingCaptureExecutor:
    def execute(self, request) -> ActionResult:
        del request
        payload = {
            "capture_failure_kind": "missing_dependency",
            "missing_dependency": "pyautogui",
        }
        return ActionResult.failure(
            "Screen capture is unavailable in this runtime because the required dependency 'pyautogui' is missing. Install it, then try again.",
            data=payload,
            structured_data=payload,
            speakable_text="Screen capture is unavailable in this runtime because the required dependency pyautogui is missing.",
            request_id="req-screen-analysis-1",
            outcome_reason="Screen capture is unavailable in this runtime because the required dependency 'pyautogui' is missing. Install it, then try again.",
        )


class _FakeOCR:
    def extract_text(self, image_path: str) -> str:
        assert image_path == "C:/tmp/capture.png"
        return "Download Python 3.14 for Windows"


class _FakeVision:
    def analyze(self, **kwargs) -> dict:
        del kwargs
        return {
            "summary": "This page appears to be the Python downloads page with install options.",
            "next_steps": ["which installer should i choose", "explain this page"],
            "signals": {"page_title": "Python Downloads", "active_url": "https://www.python.org/downloads/"},
        }


def test_screen_analysis_executor_returns_canonical_success_payload():
    ledger = _FakeLedger()
    executor = ScreenAnalysisExecutor(
        ledger=ledger,
        capture_executor=_SuccessfulCaptureExecutor(),
        ocr_pipeline=_FakeOCR(),
        vision_analyzer=_FakeVision(),
    )

    result = executor.execute(_request({"query": "what am i looking at"}))

    assert result.success is True
    assert result.speakable_text.startswith("Screen analysis ready.")
    assert result.structured_data["widget"]["type"] == "screen_analysis"
    assert result.structured_data["analysis"]["summary"].startswith("This page appears")
    assert result.structured_data["working_context_delta"]["task_goal"] == "what am i looking at"
    completion = [payload for name, payload in ledger.events if name == "SCREEN_ANALYSIS_COMPLETED"][-1]
    assert completion["success"] is True


def test_screen_analysis_executor_preserves_capture_failure_in_canonical_shape():
    ledger = _FakeLedger()
    executor = ScreenAnalysisExecutor(
        ledger=ledger,
        capture_executor=_FailingCaptureExecutor(),
        ocr_pipeline=_FakeOCR(),
        vision_analyzer=_FakeVision(),
    )

    result = executor.execute(_request({"query": "what am i looking at"}))

    assert result.success is False
    assert "pyautogui" in result.message
    assert result.structured_data["analysis_stage"] == "capture"
    assert result.structured_data["capture_failure_kind"] == "missing_dependency"
    completion = [payload for name, payload in ledger.events if name == "SCREEN_ANALYSIS_COMPLETED"][-1]
    assert completion["success"] is False

