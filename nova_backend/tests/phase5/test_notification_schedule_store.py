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


def test_notification_schedule_store_policy_snapshot_and_quiet_hours(tmp_path: Path):
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    local_tz = datetime.now().astimezone().tzinfo or timezone.utc
    quiet_now = datetime(2026, 3, 13, 23, 30, tzinfo=local_tz)

    policy = store.update_policy(
        quiet_hours_enabled=True,
        quiet_hours_start="10:00 pm",
        quiet_hours_end="7:00 am",
        max_deliveries_per_hour=1,
    )

    assert policy["quiet_hours_enabled"] is True
    assert policy["quiet_hours_start"] == "22:00"
    assert policy["quiet_hours_end"] == "07:00"
    assert policy["max_deliveries_per_hour"] == 1

    schedule = store.create_schedule(
        kind="reminder",
        title="Reminder: check logs",
        body="Check deployment logs",
        recurrence="once",
        next_run_at=quiet_now.astimezone(timezone.utc) - timedelta(minutes=10),
    )
    result = store.evaluate_delivery_policy(schedule["id"], now=quiet_now)

    assert result["allowed"] is False
    assert result["reason"] == "quiet_hours"


def test_notification_schedule_store_invalid_quiet_hours_end_falls_back_to_end_default(tmp_path: Path):
    store = NotificationScheduleStore(tmp_path / "schedules.json")

    policy = store.update_policy(
        quiet_hours_enabled=True,
        quiet_hours_start="10:00 pm",
        quiet_hours_end="not-a-time",
    )

    assert policy["quiet_hours_start"] == "22:00"
    assert policy["quiet_hours_end"] == "07:00"
    assert policy["quiet_hours_label"] == "10:00 PM to 7:00 AM"


def test_notification_schedule_store_enforces_rate_limit_and_tracks_delivery_audit(tmp_path: Path):
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    now = datetime(2026, 3, 13, 15, 0, tzinfo=timezone.utc)
    store.update_policy(quiet_hours_enabled=False, max_deliveries_per_hour=1)

    first = store.create_schedule(
        kind="daily_brief",
        title="Daily brief",
        body="Run your scheduled daily brief.",
        recurrence="daily",
        next_run_at=now - timedelta(minutes=20),
        command="morning brief",
    )
    second = store.create_schedule(
        kind="reminder",
        title="Reminder: follow up",
        body="Follow up with supplier",
        recurrence="once",
        next_run_at=now - timedelta(minutes=5),
    )

    store.record_delivery_attempt(first["id"], now=now - timedelta(minutes=2))
    store.record_delivery_outcome(
        first["id"],
        outcome="delivered",
        note="Notification surfaced in the scheduled-updates widget.",
        now=now - timedelta(minutes=2),
        surfaced=True,
    )
    second_policy = store.evaluate_delivery_policy(second["id"], now=now)

    assert second_policy["allowed"] is False
    assert second_policy["reason"] == "rate_limit"

    current = store.get_schedule(first["id"])
    assert current is not None
    assert current["last_delivery_attempt_at"]
    assert current["last_delivery_outcome"] == "delivered"
    assert current["last_delivered_at"]


def test_notification_schedule_store_can_reschedule(tmp_path: Path):
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    now = datetime(2026, 3, 13, 15, 0, tzinfo=timezone.utc)

    item = store.create_schedule(
        kind="reminder",
        title="Reminder: review phase 5",
        body="Review phase 5 implementation",
        recurrence="once",
        next_run_at=now + timedelta(hours=1),
    )
    updated = store.reschedule_schedule(item["id"], next_run_at=now + timedelta(hours=3))

    assert updated["id"] == item["id"]
    assert datetime.fromisoformat(updated["next_run_at"]) == now + timedelta(hours=3)
    assert updated["last_surface_at"] == ""
