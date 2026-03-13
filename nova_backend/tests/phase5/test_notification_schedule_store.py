from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.tasks.notification_schedule_store import NotificationScheduleStore


def test_notification_schedule_store_summarizes_due_and_upcoming_items(tmp_path: Path):
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    now = datetime(2026, 3, 13, 15, 0, tzinfo=timezone.utc)

    store.create_schedule(
        kind="daily_brief",
        title="Daily brief",
        body="Run your scheduled daily brief.",
        recurrence="daily",
        next_run_at=now - timedelta(minutes=5),
        command="morning brief",
    )
    store.create_schedule(
        kind="reminder",
        title="Reminder: review deployment issue",
        body="Review deployment issue",
        recurrence="once",
        next_run_at=now + timedelta(hours=2),
    )

    summary = store.summarize(now=now)

    assert summary["active_count"] == 2
    assert summary["due_count"] == 1
    assert summary["upcoming_count"] == 1
    assert summary["due_items"][0]["command"] == "morning brief"
    assert summary["upcoming_items"][0]["kind"] == "reminder"


def test_notification_schedule_store_cancel_and_dismiss_are_explicit(tmp_path: Path):
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    now = datetime(2026, 3, 13, 15, 0, tzinfo=timezone.utc)

    daily = store.create_schedule(
        kind="daily_brief",
        title="Daily brief",
        body="Run your scheduled daily brief.",
        recurrence="daily",
        next_run_at=now - timedelta(minutes=5),
        command="morning brief",
    )
    dismissed = store.dismiss_schedule(daily["id"], now=now)
    assert dismissed["active"] is True
    assert datetime.fromisoformat(dismissed["next_run_at"]) > now

    reminder = store.create_schedule(
        kind="reminder",
        title="Reminder: follow up",
        body="Follow up with supplier",
        recurrence="once",
        next_run_at=now + timedelta(hours=1),
    )
    cancelled = store.cancel_schedule(reminder["id"])
    assert cancelled["active"] is False

    remaining = store.list_schedules()
    assert len(remaining) == 1
    assert remaining[0]["id"] == daily["id"]
