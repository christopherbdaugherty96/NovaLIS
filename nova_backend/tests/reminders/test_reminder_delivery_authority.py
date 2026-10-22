from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from src.tasks.notification_delivery import (
    NotificationResult,
    ReminderDeliveryService,
)
from src.tasks.notification_schedule_store import NotificationScheduleStore


class _Notifier:
    def __init__(self) -> None:
        self.requests = []

    def notify(self, request):
        self.requests.append(request)
        return NotificationResult(True, "test")


class _Governor:
    def allow_notification_delivery(self, _metadata):
        return True, "allowed"


class _PresenceProbe:
    def __init__(self, *observations):
        self._observations = iter(observations)

    def observe(self, _now):
        return next(self._observations)


def _due(store: NotificationScheduleStore, now: datetime):
    return store.create_schedule(
        kind="reminder",
        title="Reminder: call the dentist",
        body="Call the dentist",
        recurrence="once",
        next_run_at=now - timedelta(minutes=1),
    )


def _grant(store: NotificationScheduleStore, schedule_id: str):
    events = []
    grant = store.grant_delivery_authority(
        schedule_id,
        channel="windows_toast",
        receipt_logger=lambda name, metadata: events.append((name, metadata)),
    )
    assert events[0][0] == "NOTIFICATION_DELIVERY_AUTHORIZED"
    return grant


def _service(store, notifier, probe):
    return ReminderDeliveryService(
        store=store,
        notifier=notifier,
        governor=_Governor(),
        ledger_logger=lambda *_: None,
        presence_probe=probe,
    )


def test_grant_receipt_failure_is_fail_closed_and_nothing_fires(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    item = _due(store, now)

    with pytest.raises(RuntimeError, match="ledger unavailable"):
        store.grant_delivery_authority(
            item["id"],
            channel="windows_toast",
            receipt_logger=lambda *_: (_ for _ in ()).throw(RuntimeError("ledger unavailable")),
        )

    saved = store.get_schedule(item["id"])
    assert saved["delivery_grant"] == {}
    notifier = _Notifier()
    outcome = _service(
        store,
        notifier,
        _PresenceProbe({"display": "on", "session": "unlocked"}),
    ).run_tick(now=now)
    assert outcome.delivered == 0
    assert notifier.requests == []
    assert store.get_schedule(item["id"])["delivery_hold_reason"] == "state_unknown"


def test_cancel_revokes_grant_and_edit_requires_replacement_grant(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    cancelled = _due(store, now)
    edited = _due(store, now)
    old_grant = _grant(store, edited["id"])
    _grant(store, cancelled["id"])

    cancelled_saved = store.cancel_schedule(cancelled["id"])
    edited_saved = store.reschedule_schedule(
        edited["id"], next_run_at=now + timedelta(hours=1)
    )

    assert cancelled_saved["delivery_grant"]["state"] == "revoked"
    assert edited_saved["delivery_grant"]["state"] == "revoked"
    assert store.delivery_authority_decision(edited["id"], channel="windows_toast")["allowed"] is False

    replacement = _grant(store, edited["id"])
    assert replacement["grant_id"] != old_grant["grant_id"]
    assert replacement["scope_hash"] != old_grant["scope_hash"]
    assert store.delivery_authority_decision(edited["id"], channel="windows_toast")["allowed"] is True


@pytest.mark.parametrize(
    ("observation", "quiet_hours", "expected_reason"),
    [
        ({"display": "off", "session": "unlocked"}, False, "display_off"),
        ({"display": "on", "session": "locked"}, False, "session_locked"),
        ({"display": "unknown", "session": "unknown"}, False, "state_unknown"),
        ({"display": "on", "session": "unlocked"}, True, "quiet_hours"),
    ],
)
def test_named_hold_reasons_are_recorded_and_keep_original_due_time(
    tmp_path, observation, quiet_hours, expected_reason
):
    now = datetime(2026, 10, 21, 23, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json", local_zone=timezone.utc)
    item = _due(store, now)
    if quiet_hours:
        store.update_policy(
            quiet_hours_enabled=True,
            quiet_hours_start="22:00",
            quiet_hours_end="07:00",
        )
    _grant(store, item["id"])
    notifier = _Notifier()

    outcome = _service(store, notifier, _PresenceProbe(observation)).run_tick(now=now)

    saved = store.get_schedule(item["id"])
    assert outcome.delivered == 0
    assert notifier.requests == []
    assert saved["next_run_at"] == item["next_run_at"]
    assert saved["delivery_hold_reason"] == expected_reason
    assert saved["delivery_retry_state"] == "waiting_for_safe_state"
    assert saved["delivery_held_at"]


def test_held_reminder_recovers_after_restart_and_delivers_exactly_once(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    path = tmp_path / "schedules.json"
    store = NotificationScheduleStore(path)
    item = _due(store, now)
    _grant(store, item["id"])
    notifier = _Notifier()

    _service(
        store,
        notifier,
        _PresenceProbe({"display": "off", "session": "unlocked"}),
    ).run_tick(now=now)
    restarted_store = NotificationScheduleStore(path)
    restarted = _service(
        restarted_store,
        notifier,
        _PresenceProbe(
            {"display": "on", "session": "unlocked"},
            {"display": "on", "session": "unlocked"},
        ),
    )

    first = restarted.run_tick(now=now + timedelta(minutes=1), startup=True)
    second = restarted.run_tick(now=now + timedelta(minutes=2))

    assert first.delivered == 1
    assert second.delivered == 0
    assert len(notifier.requests) == 1
    assert restarted_store.get_schedule(item["id"])["delivery_hold_reason"] == ""


def test_policy_change_does_not_invalidate_grant_and_quiet_hours_still_hold(tmp_path):
    outside = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json", local_zone=timezone.utc)
    outside_item = _due(store, outside)
    quiet_item = _due(store, outside)
    _grant(store, outside_item["id"])
    _grant(store, quiet_item["id"])

    store.update_policy(
        quiet_hours_enabled=True,
        quiet_hours_start="23:00",
        quiet_hours_end="06:00",
    )

    assert store.delivery_authority_decision(
        outside_item["id"], channel="windows_toast"
    )["allowed"] is True
    notifier = _Notifier()
    result = _service(
        store,
        notifier,
        _PresenceProbe({"display": "on", "session": "unlocked"}),
    ).run_tick(now=outside)
    assert result.delivered == 2

    quiet = datetime(2026, 10, 21, 23, 30, tzinfo=timezone.utc)
    later = _due(store, quiet)
    _grant(store, later["id"])
    held = _service(
        store,
        notifier,
        _PresenceProbe({"display": "on", "session": "unlocked"}),
    ).run_tick(now=quiet)
    assert held.delivered == 0
    assert store.get_schedule(later["id"])["delivery_hold_reason"] == "quiet_hours"


def test_repeated_same_hold_records_one_transition(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    item = _due(store, now)
    _grant(store, item["id"])
    events = []
    service = ReminderDeliveryService(
        store=store,
        notifier=_Notifier(),
        governor=_Governor(),
        ledger_logger=lambda name, metadata: events.append((name, metadata)),
        presence_probe=_PresenceProbe(
            *[{"display": "off", "session": "unlocked"} for _ in range(20)]
        ),
    )

    for offset in range(20):
        service.run_tick(now=now + timedelta(seconds=30 * offset))

    held_events = [name for name, _ in events if name == "NOTIFICATION_DELIVERY_HELD"]
    assert held_events == ["NOTIFICATION_DELIVERY_HELD"]


def test_legacy_and_revoked_grants_show_needs_confirmation_not_a_hold(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    legacy = _due(store, now)
    revoked = _due(store, now)
    _grant(store, revoked["id"])
    store.reschedule_schedule(revoked["id"], next_run_at=now - timedelta(minutes=1))

    service = _service(
        store,
        _Notifier(),
        _PresenceProbe(
            {"display": "on", "session": "unlocked"},
            {"display": "on", "session": "unlocked"},
        ),
    )
    service.run_tick(now=now)

    summary = store.summarize(now=now)
    rows = {row["id"]: row for row in summary["due_items"]}
    for schedule_id in (legacy["id"], revoked["id"]):
        assert rows[schedule_id]["delivery_authorization_status"] == "needs_confirmation"
        assert rows[schedule_id]["delivery_hold_reason"] == ""
