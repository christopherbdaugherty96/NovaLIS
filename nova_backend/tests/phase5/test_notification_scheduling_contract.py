from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"
SESSION_HANDLER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "websocket" / "session_handler.py"
GOVERNOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "governor.py"
STORE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "tasks" / "notification_schedule_store.py"
EVENT_TYPES_PATH = PROJECT_ROOT / "nova_backend" / "src" / "ledger" / "event_types.py"


def test_brain_server_exposes_manual_notification_scheduling_controls():
    source = (
        BRAIN_SERVER_PATH.read_text(encoding="utf-8")
        + "\n"
        + SESSION_HANDLER_PATH.read_text(encoding="utf-8")
    )

    assert "SHOW_SCHEDULES_COMMANDS" in source
    assert "NOTIFICATION_SETTINGS_COMMANDS" in source
    assert "SCHEDULE_BRIEF_RE" in source
    assert "REMIND_ME_RE" in source
    assert "RESCHEDULE_SCHEDULE_RE" in source
    assert "SET_QUIET_HOURS_RE" in source
    assert "SET_NOTIFICATION_RATE_LIMIT_RE" in source
    assert "send_notification_schedule_widget" in source
    assert "NOTIFICATION_SCHEDULE_CREATED" in source
    assert "NOTIFICATION_SCHEDULE_UPDATED" in source
    assert "NOTIFICATION_POLICY_UPDATED" in source
    assert "NOTIFICATION_DELIVERY_ATTEMPTED" in source
    assert "NOTIFICATION_DELIVERY_COMPLETED" in source
    assert "NOTIFICATION_DELIVERY_SUPPRESSED" in source
    assert "schedule daily brief at 8:00 am" in source


def test_notification_scheduling_uses_store_policy_and_governor_gate():
    governor_source = GOVERNOR_PATH.read_text(encoding="utf-8")
    store_source = STORE_PATH.read_text(encoding="utf-8")
    events_source = EVENT_TYPES_PATH.read_text(encoding="utf-8")

    assert "allow_notification_delivery" in governor_source
    assert "update_policy(" in store_source
    assert "evaluate_delivery_policy(" in store_source
    assert "record_delivery_attempt(" in store_source
    assert "record_delivery_outcome(" in store_source
    assert '"NOTIFICATION_POLICY_UPDATED"' in events_source
    assert '"NOTIFICATION_DELIVERY_ATTEMPTED"' in events_source
    assert '"NOTIFICATION_DELIVERY_COMPLETED"' in events_source
    assert '"NOTIFICATION_DELIVERY_SUPPRESSED"' in events_source
