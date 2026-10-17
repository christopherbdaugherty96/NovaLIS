from __future__ import annotations

from datetime import datetime, timedelta, timezone, tzinfo

import pytest
from src import brain_server
from src.tasks.notification_schedule_store import NotificationScheduleStore
from tests.phase45._websocket_test_helpers import _chat_messages
from tests.websocket.test_commitment_truth_reminder_handoff import (
    _RecordingScheduleStore,
    _run_session,
)

ZERO = timedelta(0)
HOUR = timedelta(hours=1)


def _first_sunday_on_or_after(value: datetime) -> datetime:
    days_to_go = 6 - value.weekday()
    return value + timedelta(days=days_to_go) if days_to_go else value


def _us_dst_range(year: int) -> tuple[datetime, datetime]:
    return (
        _first_sunday_on_or_after(datetime(year, 3, 8, 2)),
        _first_sunday_on_or_after(datetime(year, 11, 1, 2)),
    )


class _EasternTime(tzinfo):
    """Deterministic US Eastern rules for zone-injected DST tests."""

    _standard = timedelta(hours=-5)

    def tzname(self, value):
        return "EDT" if self.dst(value) else "EST"

    def utcoffset(self, value):
        return self._standard + self.dst(value)

    def dst(self, value):
        if value is None or value.tzinfo is None:
            return ZERO
        start, end = _us_dst_range(value.year)
        local = value.replace(tzinfo=None)
        if start + HOUR <= local < end - HOUR:
            return HOUR
        if end - HOUR <= local < end:
            return ZERO if value.fold else HOUR
        if start <= local < start + HOUR:
            return HOUR if value.fold else ZERO
        return ZERO

    def fromutc(self, value):
        standard = value.replace(tzinfo=None) + self._standard
        daylight = standard + HOUR
        start, end = _us_dst_range(standard.year)
        if end <= daylight < end + HOUR:
            return standard.replace(tzinfo=self, fold=1)
        if standard < start or daylight >= end:
            return standard.replace(tzinfo=self)
        return daylight.replace(tzinfo=self)


EASTERN = _EasternTime()


@pytest.mark.parametrize(
    ("now", "time_text", "expected"),
    (
        (datetime(2026, 10, 31, 20, 0, tzinfo=EASTERN), "tomorrow 9am", datetime(2026, 11, 1, 9, 0, tzinfo=EASTERN)),
        (datetime(2027, 3, 13, 20, 0, tzinfo=EASTERN), "tomorrow 9am", datetime(2027, 3, 14, 9, 0, tzinfo=EASTERN)),
        (datetime(2026, 10, 31, 20, 0, tzinfo=EASTERN), "on Sunday at 9am", datetime(2026, 11, 1, 9, 0, tzinfo=EASTERN)),
        (datetime(2027, 3, 13, 20, 0, tzinfo=EASTERN), "on Sunday at 9am", datetime(2027, 3, 14, 9, 0, tzinfo=EASTERN)),
        (datetime(2026, 10, 31, 23, 0, tzinfo=EASTERN), "9am", datetime(2026, 11, 1, 9, 0, tzinfo=EASTERN)),
        (datetime(2027, 3, 13, 23, 0, tzinfo=EASTERN), "9am", datetime(2027, 3, 14, 9, 0, tzinfo=EASTERN)),
    ),
)
def test_schedule_parser_keeps_wall_clock_across_dst(monkeypatch, now, time_text, expected):
    monkeypatch.setattr(brain_server, "_local_now", lambda: now)

    actual = brain_server._parse_schedule_datetime(
        time_text,
        recurrence="once",
        local_zone=EASTERN,
    )

    assert actual == expected
    assert actual.hour == expected.hour
    assert actual.utcoffset() == expected.utcoffset()


def test_schedule_parser_refuses_nonexistent_spring_forward_time(monkeypatch):
    monkeypatch.setattr(
        brain_server,
        "_local_now",
        lambda: datetime(2027, 3, 13, 20, 0, tzinfo=EASTERN),
    )

    with pytest.raises(ValueError, match="does not exist"):
        brain_server._parse_schedule_datetime(
            "tomorrow 2:30 am",
            recurrence="once",
            local_zone=EASTERN,
        )


def test_schedule_parser_uses_first_fall_back_occurrence(monkeypatch):
    monkeypatch.setattr(
        brain_server,
        "_local_now",
        lambda: datetime(2026, 10, 31, 20, 0, tzinfo=EASTERN),
    )

    actual = brain_server._parse_schedule_datetime(
        "tomorrow 1:30 am",
        recurrence="once",
        local_zone=EASTERN,
    )

    assert actual == datetime(2026, 11, 1, 1, 30, tzinfo=EASTERN, fold=0)
    assert actual.fold == 0
    assert actual.utcoffset().total_seconds() == -4 * 60 * 60


@pytest.mark.parametrize(
    ("recurrence", "first_run", "dismissed_at", "expected"),
    (
        (
            "daily",
            datetime(2026, 10, 31, 9, 0, tzinfo=EASTERN),
            datetime(2026, 10, 31, 10, 0, tzinfo=EASTERN),
            datetime(2026, 11, 1, 9, 0, tzinfo=EASTERN),
        ),
        (
            "weekly",
            datetime(2026, 10, 25, 9, 0, tzinfo=EASTERN),
            datetime(2026, 10, 25, 10, 0, tzinfo=EASTERN),
            datetime(2026, 11, 1, 9, 0, tzinfo=EASTERN),
        ),
        (
            "daily",
            datetime(2027, 3, 13, 9, 0, tzinfo=EASTERN),
            datetime(2027, 3, 13, 10, 0, tzinfo=EASTERN),
            datetime(2027, 3, 14, 9, 0, tzinfo=EASTERN),
        ),
        (
            "weekly",
            datetime(2027, 3, 7, 9, 0, tzinfo=EASTERN),
            datetime(2027, 3, 7, 10, 0, tzinfo=EASTERN),
            datetime(2027, 3, 14, 9, 0, tzinfo=EASTERN),
        ),
    ),
)
def test_repeating_schedule_keeps_wall_clock_across_dst(
    tmp_path,
    recurrence,
    first_run,
    dismissed_at,
    expected,
):
    store = NotificationScheduleStore(tmp_path / "schedules.json", local_zone=EASTERN)
    item = store.create_schedule(
        kind="reminder",
        title="DST repeat",
        body="Check the DST repeat",
        recurrence=recurrence,
        next_run_at=first_run,
    )

    dismissed = store.dismiss_schedule(item["id"], now=dismissed_at)
    actual = datetime.fromisoformat(dismissed["next_run_at"]).astimezone(EASTERN)

    assert actual == expected
    assert actual.hour == 9


@pytest.mark.parametrize(
    ("recurrence", "first_run", "dismissed_at", "expected"),
    (
        (
            "daily",
            datetime(2027, 3, 13, 2, 30, tzinfo=EASTERN),
            datetime(2027, 3, 13, 3, 0, tzinfo=EASTERN),
            datetime(2027, 3, 15, 2, 30, tzinfo=EASTERN),
        ),
        (
            "weekly",
            datetime(2027, 3, 7, 2, 30, tzinfo=EASTERN),
            datetime(2027, 3, 7, 3, 0, tzinfo=EASTERN),
            datetime(2027, 3, 21, 2, 30, tzinfo=EASTERN),
        ),
    ),
)
def test_repeating_schedule_skips_nonexistent_spring_forward_occurrence(
    tmp_path,
    recurrence,
    first_run,
    dismissed_at,
    expected,
):
    store = NotificationScheduleStore(tmp_path / "schedules.json", local_zone=EASTERN)
    item = store.create_schedule(
        kind="reminder",
        title="DST gap repeat",
        body="Skip the nonexistent occurrence",
        recurrence=recurrence,
        next_run_at=first_run,
    )

    dismissed = store.dismiss_schedule(item["id"], now=dismissed_at)
    actual = datetime.fromisoformat(dismissed["next_run_at"]).astimezone(EASTERN)

    assert actual == expected
    assert actual.hour == 2
    assert actual.minute == 30


def test_reminder_confirmation_matches_stored_time_across_dst(monkeypatch):
    now = datetime(2026, 10, 31, 20, 0, tzinfo=timezone(timedelta(hours=-4)))
    expected = datetime(2026, 11, 1, 9, 0, tzinfo=EASTERN)
    store = _RecordingScheduleStore()
    monkeypatch.setattr(brain_server, "_local_now", lambda: now)
    monkeypatch.setattr(brain_server, "_schedule_local_zone", lambda: EASTERN, raising=False)

    ws = _run_session(
        monkeypatch,
        ["remind me tomorrow at 9am to TEST-QA-F2 dst check"],
        store,
    )

    assert len(store.created) == 1
    assert store.created[0]["next_run_at"] == expected
    confirmation = next(message for message in _chat_messages(ws) if "Reminder saved:" in message)
    assert "Requested for: Nov 01, 9:00 AM" in confirmation

