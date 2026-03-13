from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"


def test_brain_server_exposes_manual_notification_scheduling_controls():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")

    assert "SHOW_SCHEDULES_COMMANDS" in source
    assert "SCHEDULE_BRIEF_RE" in source
    assert "REMIND_ME_RE" in source
    assert "send_notification_schedule_widget" in source
    assert "NOTIFICATION_SCHEDULE_CREATED" in source
    assert "schedule daily brief at 8:00 am" in source
