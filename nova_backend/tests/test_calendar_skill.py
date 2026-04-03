import asyncio
from datetime import datetime, timedelta

from src.skills.calendar import CalendarSkill


def test_calendar_skill_reports_not_connected_when_path_missing(monkeypatch):
    monkeypatch.delenv("NOVA_CALENDAR_ICS_PATH", raising=False)
    skill = CalendarSkill()
    result = asyncio.run(skill.handle("calendar"))

    assert result.success is True
    assert result.skill == "calendar"
    assert "calendar is ready when you are" in result.message.lower()
    widget = result.widget_data or {}
    assert widget.get("summary") == "Not connected."
    assert widget.get("status") == "not_connected"
    assert ".ics file" in widget.get("setup_hint", "")


def test_calendar_skill_reads_todays_events(monkeypatch, tmp_path):
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    ics_text = (
        "BEGIN:VCALENDAR\n"
        "BEGIN:VEVENT\n"
        f"DTSTART:{today.strftime('%Y%m%dT090000')}\n"
        "SUMMARY:Team Standup\n"
        "END:VEVENT\n"
        "BEGIN:VEVENT\n"
        f"DTSTART:{tomorrow.strftime('%Y%m%dT090000')}\n"
        "SUMMARY:Tomorrow Event\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    )
    ics_path = tmp_path / "calendar.ics"
    ics_path.write_text(ics_text, encoding="utf-8")
    monkeypatch.setenv("NOVA_CALENDAR_ICS_PATH", str(ics_path))

    skill = CalendarSkill()
    result = asyncio.run(skill.handle("today's schedule"))

    assert result.success is True
    assert "Today's schedule:" in result.message
    widget = result.widget_data or {}
    events = widget.get("events") or []
    assert len(events) == 1
    assert events[0]["title"] == "Team Standup"
    assert widget.get("status") == "ok"
    assert widget.get("source_label") == "calendar.ics"
    assert result.data["scope"] == "today"


def test_calendar_skill_reads_tomorrows_events(monkeypatch, tmp_path):
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    ics_text = (
        "BEGIN:VCALENDAR\n"
        "BEGIN:VEVENT\n"
        f"DTSTART:{today.strftime('%Y%m%dT090000')}\n"
        "SUMMARY:Today Event\n"
        "END:VEVENT\n"
        "BEGIN:VEVENT\n"
        f"DTSTART:{tomorrow.strftime('%Y%m%dT143000')}\n"
        "SUMMARY:Interview Prep\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    )
    ics_path = tmp_path / "calendar.ics"
    ics_path.write_text(ics_text, encoding="utf-8")
    monkeypatch.setenv("NOVA_CALENDAR_ICS_PATH", str(ics_path))

    skill = CalendarSkill()
    result = asyncio.run(skill.handle("tomorrow's schedule"))

    assert result.success is True
    assert "Tomorrow looks like this:" in result.message
    widget = result.widget_data or {}
    events = widget.get("events") or []
    assert len(events) == 1
    assert events[0]["title"] == "Interview Prep"
    assert result.data["scope"] == "tomorrow"


def test_calendar_skill_reads_upcoming_events(monkeypatch, tmp_path):
    today = datetime.now()
    in_three_days = today + timedelta(days=3)
    in_ten_days = today + timedelta(days=10)
    ics_text = (
        "BEGIN:VCALENDAR\n"
        "BEGIN:VEVENT\n"
        f"DTSTART:{today.strftime('%Y%m%dT090000')}\n"
        "SUMMARY:Standup\n"
        "END:VEVENT\n"
        "BEGIN:VEVENT\n"
        f"DTSTART:{in_three_days.strftime('%Y%m%dT110000')}\n"
        "SUMMARY:Planning Session\n"
        "END:VEVENT\n"
        "BEGIN:VEVENT\n"
        f"DTSTART:{in_ten_days.strftime('%Y%m%dT110000')}\n"
        "SUMMARY:Far Future Event\n"
        "END:VEVENT\n"
        "END:VCALENDAR\n"
    )
    ics_path = tmp_path / "calendar.ics"
    ics_path.write_text(ics_text, encoding="utf-8")
    monkeypatch.setenv("NOVA_CALENDAR_ICS_PATH", str(ics_path))

    skill = CalendarSkill()
    result = asyncio.run(skill.handle("upcoming events"))

    assert result.success is True
    assert "Here's what's coming up:" in result.message
    widget = result.widget_data or {}
    events = widget.get("events") or []
    assert len(events) == 2
    assert events[0]["title"] == "Standup"
    assert events[1]["title"] == "Planning Session"
    assert all(item["title"] != "Far Future Event" for item in events)
    assert result.data["scope"] == "upcoming"


def test_calendar_skill_does_not_hijack_schedule_management_commands():
    skill = CalendarSkill()

    assert skill.can_handle("show schedules") is False
    assert skill.can_handle("schedule daily brief at 8:00 am") is False
    assert skill.can_handle("what's on my schedule today") is True
    assert skill.can_handle("what do i have tomorrow") is True
    assert skill.can_handle("upcoming events") is True
    assert skill.can_handle("what's coming up") is True
    assert skill.can_handle("agenda for tomorrow") is True
