import asyncio
from datetime import datetime, timedelta

from src.skills.calendar import CalendarSkill


def test_calendar_skill_reports_not_connected_when_path_missing(monkeypatch):
    monkeypatch.delenv("NOVA_CALENDAR_ICS_PATH", raising=False)
    skill = CalendarSkill()
    result = asyncio.run(skill.handle("calendar"))

    assert result.success is True
    assert result.skill == "calendar"
    assert "no ICS file is connected" in result.message
    assert (result.widget_data or {}).get("summary") == "Not connected."


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
    assert "Today's calendar:" in result.message
    widget = result.widget_data or {}
    events = widget.get("events") or []
    assert len(events) == 1
    assert events[0]["title"] == "Team Standup"
