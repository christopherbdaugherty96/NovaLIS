from __future__ import annotations

import inspect

from src.executors.explain_anything_executor import ExplainAnythingExecutor
from src.executors.screen_analysis_executor import ScreenAnalysisExecutor
from src.executors.screen_capture_executor import ScreenCaptureExecutor
from src.ledger.event_types import EVENT_TYPES


def test_perception_event_types_are_registered_in_ledger_taxonomy():
    expected = {
        "CONTEXT_SNAPSHOT_REQUESTED",
        "CONTEXT_SNAPSHOT_COMPLETED",
        "SCREEN_CAPTURE_REQUESTED",
        "SCREEN_CAPTURE_COMPLETED",
        "SCREEN_ANALYSIS_COMPLETED",
        "EXPLAIN_ANYTHING_REQUESTED",
        "EXPLAIN_ANYTHING_COMPLETED",
        "WORKING_CONTEXT_CREATED",
        "WORKING_CONTEXT_UPDATED",
        "WORKING_CONTEXT_PRUNED",
        "WORKING_CONTEXT_CONSUMED",
    }
    assert expected.issubset(EVENT_TYPES)


def test_screen_capture_executor_references_capture_events():
    source = inspect.getsource(ScreenCaptureExecutor)
    assert "SCREEN_CAPTURE_REQUESTED" in source
    assert "SCREEN_CAPTURE_COMPLETED" in source


def test_screen_analysis_executor_references_analysis_completion_event():
    source = inspect.getsource(ScreenAnalysisExecutor)
    assert "SCREEN_ANALYSIS_COMPLETED" in source


def test_explain_anything_executor_references_request_and_completion_events():
    source = inspect.getsource(ExplainAnythingExecutor)
    assert "EXPLAIN_ANYTHING_REQUESTED" in source
    assert "EXPLAIN_ANYTHING_COMPLETED" in source
