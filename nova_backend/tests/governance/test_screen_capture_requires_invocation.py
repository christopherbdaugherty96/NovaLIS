from __future__ import annotations

import inspect
from pathlib import Path

from src.executors.explain_anything_executor import ExplainAnythingExecutor
from src.executors.screen_capture_executor import ScreenCaptureExecutor

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BRAIN_SERVER_PATH = PROJECT_ROOT / "src" / "brain_server.py"


def test_screen_capture_executor_has_explicit_invocation_gate():
    source = inspect.getsource(ScreenCaptureExecutor.execute)
    assert "invocation_source" in source
    assert "ALLOWED_INVOCATION_SOURCES" in inspect.getsource(ScreenCaptureExecutor)
    assert "requires explicit invocation source" in source.lower()


def test_explain_anything_executor_has_explicit_invocation_gate():
    source = inspect.getsource(ExplainAnythingExecutor.execute)
    assert "invocation_source" in source
    assert "ALLOWED_INVOCATION_SOURCES" in inspect.getsource(ExplainAnythingExecutor)
    assert "requires explicit invocation source" in source.lower()


def test_brain_server_overrides_invocation_source_for_perception_capabilities():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")
    assert "if capability_id in {58, 59, 60}:" in source
    assert 'params["invocation_source"] = invocation_source' in source
