from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

from src.tasks.notification_delivery import (
    NotificationRequest,
    NotificationResult,
    ReminderDeliveryService,
)
from src.tasks.notification_schedule_store import NotificationScheduleStore


def test_dashboard_refresh_does_not_initiate_reminder_delivery() -> None:
    session_source = (
        Path(__file__).resolve().parents[2]
        / "src"
        / "websocket"
        / "session_handler.py"
    ).read_text(encoding="utf-8")

    assert "snapshot = _process_due_notification_delivery(" not in session_source


def test_uncertain_delivery_event_is_registered() -> None:
    event_source = (
        Path(__file__).resolve().parents[2] / "src" / "ledger" / "event_types.py"
    ).read_text(encoding="utf-8")

    assert '"NOTIFICATION_DELIVERY_UNCERTAIN"' in event_source


class _Notifier:
    def __init__(self, *, accepted: bool = True):
        self.accepted = accepted
        self.requests: list[NotificationRequest] = []

    def notify(self, request: NotificationRequest) -> NotificationResult:
        self.requests.append(request)
        return NotificationResult(
            accepted=self.accepted,
            adapter="test",
            error_code="" if self.accepted else "TEST_FAILURE",
        )


class _Governor:
    def allow_notification_delivery(self, _metadata):
        return True, "allowed"


class _ResumeProbe:
    def __init__(self, observations):
        self._observations = iter(observations)

    def observe(self, _now):
        return next(self._observations)


def _make_due(store: NotificationScheduleStore, now: datetime, *, minutes_late: int = 1):
    item = store.create_schedule(
        kind="reminder",
        title="Reminder: call the dentist",
        body="Call the dentist",
        recurrence="once",
        next_run_at=now - timedelta(minutes=minutes_late),
    )
    store.grant_delivery_authority(
        item["id"], channel="windows_toast", receipt_logger=lambda *_: None
    )
    return item


def _service(store, notifier, ledger=None):
    return ReminderDeliveryService(
        store=store,
        notifier=notifier,
        governor=_Governor(),
        ledger_logger=(ledger or (lambda *_: None)),
        tick_seconds=30,
    )


def test_due_delivery_runs_without_dashboard_and_repeated_ticks_do_not_duplicate(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    item = _make_due(store, now)
    notifier = _Notifier()
    service = _service(store, notifier)

    first = service.run_tick(now=now)
    second = service.run_tick(now=now + timedelta(seconds=30))

    assert first.delivered == 1
    assert second.delivered == 0
    assert [request.schedule_id for request in notifier.requests] == [item["id"]]
    saved = store.get_schedule(item["id"])
    assert saved["active"] is False
    assert saved["last_delivery_outcome"] == "delivered"


def test_parallel_claim_allows_one_delivery_for_occurrence(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    item = _make_due(store, now)

    with ThreadPoolExecutor(max_workers=8) as pool:
        claims = list(
            pool.map(
                lambda _: store.claim_due_occurrence(item["id"], now=now),
                range(16),
            )
        )

    won = [claim for claim in claims if claim.get("claimed")]
    assert len(won) == 1
    assert won[0]["occurrence_id"] == f'{item["id"]}@{item["next_run_at"]}'


def test_restart_delivers_overdue_once_with_original_due_time(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    path = tmp_path / "schedules.json"
    first_store = NotificationScheduleStore(path)
    item = _make_due(first_store, now, minutes_late=5)
    notifier = _Notifier()

    restarted = _service(NotificationScheduleStore(path), notifier)
    outcome = restarted.run_tick(now=now, startup=True)
    restarted_again = _service(NotificationScheduleStore(path), notifier)
    repeated = restarted_again.run_tick(now=now + timedelta(seconds=10), startup=True)

    assert outcome.delivered == 1
    assert repeated.delivered == 0
    assert len(notifier.requests) == 1
    request = notifier.requests[0]
    assert request.overdue is True
    assert request.original_due_at == datetime.fromisoformat(item["next_run_at"])
    assert "Missed while Nova wasn't running" in request.body


def test_restart_marks_interrupted_claim_uncertain_without_retrying(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    path = tmp_path / "schedules.json"
    store = NotificationScheduleStore(path)
    item = _make_due(store, now)
    assert store.claim_due_occurrence(item["id"], now=now)["claimed"] is True
    notifier = _Notifier()

    restarted = _service(NotificationScheduleStore(path), notifier)
    restarted.run_tick(now=now + timedelta(seconds=10), startup=True)

    saved = store.get_schedule(item["id"])
    assert notifier.requests == []
    assert saved["last_delivery_outcome"] == "delivery_uncertain"
    assert saved["active"] is False


def test_sleep_holds_due_reminder_until_user_returns_then_marks_it_overdue(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    item = _make_due(store, now)
    notifier = _Notifier()
    probe = _ResumeProbe(
        [
            {"resume_detected": True, "user_present": False},
            {"resume_detected": False, "user_present": True},
        ]
    )
    service = ReminderDeliveryService(
        store=store,
        notifier=notifier,
        governor=_Governor(),
        ledger_logger=lambda *_: None,
        tick_seconds=30,
        resume_probe=probe,
    )

    held = service.run_tick(now=now)
    assert store.get_schedule(item["id"])["active"] is True
    delivered = service.run_tick(now=now + timedelta(seconds=10))

    assert held.delivered == 0
    assert delivered.delivered == 1
    assert len(notifier.requests) == 1
    assert notifier.requests[0].overdue is True
    assert notifier.requests[0].body.startswith(
        "Delivered late — your laptop was asleep or the screen was off"
    )


def test_late_wording_matches_startup_lock_display_and_generic_reasons(tmp_path):
    base = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    cases = (
        ("startup", True, "", "Missed while Nova wasn't running"),
        ("display", False, "display_off", "asleep or the screen was off"),
        ("locked", False, "session_locked", "while the screen was locked"),
        ("generic", False, "", "Delivered late:"),
    )
    for name, startup, hold_reason, expected in cases:
        store = NotificationScheduleStore(tmp_path / f"{name}.json")
        item = _make_due(store, base, minutes_late=5)
        if hold_reason:
            store.record_delivery_hold(item["id"], reason=hold_reason, now=base)
        notifier = _Notifier()
        _service(store, notifier).run_tick(now=base, startup=startup)
        assert expected in notifier.requests[0].body


def test_edit_or_cancel_before_due_never_delivers_old_occurrence(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    cancelled = _make_due(store, now)
    edited = _make_due(store, now)
    store.cancel_schedule(cancelled["id"])
    store.reschedule_schedule(edited["id"], next_run_at=now + timedelta(hours=2))
    notifier = _Notifier()

    outcome = _service(store, notifier).run_tick(now=now)

    assert outcome.delivered == 0
    assert notifier.requests == []


def test_clock_jump_forward_then_back_does_not_repeat_delivery(tmp_path):
    start = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    _make_due(store, start)
    notifier = _Notifier()
    service = _service(store, notifier)

    service.run_tick(now=start + timedelta(hours=2))
    service.run_tick(now=start - timedelta(hours=1))
    service.run_tick(now=start + timedelta(hours=3))

    assert len(notifier.requests) == 1


def test_notifier_failure_is_uncertain_not_delivered(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    item = _make_due(store, now)
    notifier = _Notifier(accepted=False)

    outcome = _service(store, notifier).run_tick(now=now)

    assert outcome.delivered == 0
    assert outcome.uncertain == 1
    saved = store.get_schedule(item["id"])
    assert saved["last_delivery_outcome"] == "delivery_uncertain"
    assert saved["active"] is False


def test_delivery_path_opens_no_network_socket(tmp_path, monkeypatch):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    _make_due(store, now)
    notifier = _Notifier()

    def blocked_socket(*_args, **_kwargs):
        raise AssertionError("delivery path attempted network access")

    monkeypatch.setattr(socket, "socket", blocked_socket)

    assert _service(store, notifier).run_tick(now=now).delivered == 1


def test_attempt_and_completion_ledger_events_bracket_display(tmp_path):
    now = datetime(2026, 10, 21, 15, 0, tzinfo=timezone.utc)
    store = NotificationScheduleStore(tmp_path / "schedules.json")
    _make_due(store, now)
    events = []

    _service(store, _Notifier(), ledger=lambda name, data: events.append((name, data))).run_tick(now=now)

    assert [name for name, _ in events] == [
        "NOTIFICATION_DELIVERY_ATTEMPTED",
        "NOTIFICATION_DELIVERY_COMPLETED",
    ]

