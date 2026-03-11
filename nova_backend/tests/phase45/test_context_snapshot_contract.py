from __future__ import annotations

import pytest

from src.context.context_snapshot_service import ContextSnapshotService


class _FakeLedger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, payload))


def test_context_snapshot_service_collects_read_only_signals_and_logs_events():
    ledger = _FakeLedger()
    service = ContextSnapshotService(
        active_window_provider=lambda: {"title": "Python Downloads", "app": "Chrome"},
        browser_context_provider=lambda active: {"is_browser": True, "url": "https://python.org/downloads", "page_title": active.get("title"), "selected_text": ""},
        system_context_provider=lambda: {"os": "Windows", "os_release": "11", "hostname": "NOVA-DEV"},
        cursor_provider=lambda: {"x": 200, "y": 300, "screen_width": 1920, "screen_height": 1080},
        ledger=ledger,
    )
    snapshot = service.capture_snapshot(request_id="req-ctx-1", invocation_source="ui")

    assert snapshot["request_id"] == "req-ctx-1"
    assert snapshot["invocation_source"] == "ui"
    assert snapshot["browser"]["is_browser"] is True
    assert snapshot["system"]["os"] == "Windows"
    assert "authority" not in snapshot

    event_names = [name for name, _ in ledger.events]
    assert "CONTEXT_SNAPSHOT_REQUESTED" in event_names
    assert "CONTEXT_SNAPSHOT_COMPLETED" in event_names


def test_context_snapshot_service_requires_explicit_invocation_source():
    service = ContextSnapshotService(
        active_window_provider=lambda: {},
        browser_context_provider=lambda _: {},
        system_context_provider=lambda: {},
        cursor_provider=lambda: {},
        ledger=None,
    )
    with pytest.raises(ValueError):
        service.capture_snapshot(request_id="req-ctx-2", invocation_source="")
