from __future__ import annotations

from src.brain_server import _build_thread_detail_widget, _compute_thread_change_summary


def test_change_summary_for_new_thread_snapshot():
    current = {"updated_at": "2026-03-12T10:00:00+00:00"}
    assert _compute_thread_change_summary(current, None) == "Changed: new thread activity recorded."


def test_change_summary_prioritizes_decision_change():
    previous = {
        "latest_decision": "Use old build pipeline",
        "latest_blocker": "Import path issue",
        "memory_count": 2,
        "last_memory_updated_at": "2026-03-12T09:00:00+00:00",
        "updated_at": "2026-03-12T09:00:00+00:00",
    }
    current = {
        "latest_decision": "Use PYTHONPATH check before rebuild",
        "latest_blocker": "Import path issue",
        "memory_count": 3,
        "last_memory_updated_at": "2026-03-12T10:00:00+00:00",
        "updated_at": "2026-03-12T10:00:00+00:00",
    }
    assert _compute_thread_change_summary(current, previous) == "Changed: decision updated."


def test_change_summary_detects_memory_addition_without_other_changes():
    previous = {
        "latest_decision": "",
        "latest_blocker": "Container import failure",
        "memory_count": 1,
        "last_memory_updated_at": "2026-03-12T09:00:00+00:00",
        "updated_at": "2026-03-12T09:00:00+00:00",
    }
    current = {
        "latest_decision": "",
        "latest_blocker": "Container import failure",
        "memory_count": 2,
        "last_memory_updated_at": "2026-03-12T10:00:00+00:00",
        "updated_at": "2026-03-12T10:00:00+00:00",
    }
    assert _compute_thread_change_summary(current, previous) == "Changed: memory entry added."


def test_change_summary_handles_no_major_updates():
    previous = {
        "latest_decision": "Use pinned dependency set",
        "latest_blocker": "Dependency mismatch",
        "memory_count": 4,
        "last_memory_updated_at": "2026-03-12T09:00:00+00:00",
        "updated_at": "2026-03-12T09:00:00+00:00",
    }
    current = dict(previous)
    assert _compute_thread_change_summary(current, previous) == "Changed: no major updates."


def test_thread_detail_widget_payload_has_polished_fields():
    detail = {
        "name": "Deployment Issue",
        "goal": "Ship stable deployment",
        "latest_blocker": "Container cannot resolve module path",
        "latest_next_action": "Verify PYTHONPATH in container",
        "health_reason": "A blocker exists, but there is at least one follow-up action.",
        "recent_decisions": ["Inspect PYTHONPATH before rebuild."],
    }
    memory_items = [
        {"id": "MEM-1", "title": "Decision: Deployment Issue", "tier": "active", "updated_at": "2026-03-12T12:00:00+00:00"},
        {"id": "MEM-2", "title": "Thread Snapshot: Deployment Issue", "tier": "active", "updated_at": "2026-03-12T11:00:00+00:00"},
    ]
    widget = _build_thread_detail_widget(detail=detail, memory_items=memory_items)
    assert widget["type"] == "thread_detail"
    assert "Blocked because" in str(widget.get("why_blocked") or "")
    assert str(widget.get("next_step") or "") == "Verify PYTHONPATH in container"
    assert "address the current blocker" in str(widget.get("why_next_step") or "")
    assert list(widget.get("recent_decisions") or []) == ["Inspect PYTHONPATH before rebuild."]
