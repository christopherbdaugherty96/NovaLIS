from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from pathlib import Path

from ..base_skill import BaseSkill, SkillResult


class CalendarSkill(BaseSkill):
    name = "calendar"
    _SCHEDULE_COMMAND_HINTS = (
        "schedule daily",
        "schedule an",
        "show schedules",
        "cancel schedule",
        "dismiss schedule",
        "reschedule",
        "remind me",
    )

    def can_handle(self, query: str) -> bool:
        q = (query or "").strip().lower()
        if not q:
            return False
        if any(hint in q for hint in self._SCHEDULE_COMMAND_HINTS):
            return False
        if q in {"calendar", "agenda"}:
            return True
        if "calendar" in q:
            return True
        if "today" in q and ("schedule" in q or "agenda" in q or "events" in q):
            return True
        if "tomorrow" in q and ("schedule" in q or "agenda" in q or "events" in q):
            return True
        if any(hint in q for hint in ("upcoming", "this week", "next 7 days", "coming up")) and any(
            word in q for word in ("schedule", "agenda", "events", "calendar", "what")
        ):
            return True
        if q in {
            "what do i have today",
            "what do i have tomorrow",
            "what's coming up",
            "whats coming up",
            "coming up",
            "this week",
        }:
            return True
        if "schedule" in q and any(
            hint in q
            for hint in (
                "my ",
                "on my",
                "what",
                "what's",
                "whats",
                "today",
                "tomorrow",
                "upcoming",
                "this week",
                "events",
            )
        ):
            return True
        if "agenda" in q and any(hint in q for hint in ("today", "tomorrow", "upcoming", "this week", "coming up")):
            return True
        return False

    @staticmethod
    def _scope_from_query(query: str) -> tuple[str, date, date]:
        q = (query or "").strip().lower()
        today = datetime.now().date()
        if "tomorrow" in q:
            tomorrow = today + timedelta(days=1)
            return ("tomorrow", tomorrow, tomorrow)
        if any(hint in q for hint in ("upcoming", "this week", "next 7 days", "coming up")):
            return ("upcoming", today, today + timedelta(days=6))
        return ("today", today, today)

    @staticmethod
    def _calendar_path() -> Path | None:
        raw = (os.getenv("NOVA_CALENDAR_ICS_PATH") or "").strip()
        if not raw:
            return None
        candidate = Path(raw).expanduser()
        if not candidate.exists() or not candidate.is_file():
            return None
        return candidate

    @staticmethod
    def _unfold_ics_lines(raw_text: str) -> list[str]:
        lines: list[str] = []
        for line in raw_text.splitlines():
            if line.startswith((" ", "\t")) and lines:
                lines[-1] += line[1:]
                continue
            lines.append(line.strip())
        return lines

    @staticmethod
    def _parse_dt(value: str) -> datetime | None:
        clean = (value or "").strip()
        if not clean:
            return None
        if clean.endswith("Z"):
            for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%dT%H%MZ"):
                try:
                    return datetime.strptime(clean, fmt)
                except ValueError:
                    continue
        for fmt in ("%Y%m%dT%H%M%S", "%Y%m%dT%H%M", "%Y%m%d"):
            try:
                return datetime.strptime(clean, fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def _format_time(dt: datetime, raw_value: str) -> str:
        value = (raw_value or "").strip()
        if len(value) == 8 and value.isdigit():
            return "All day"
        return dt.strftime("%I:%M %p").lstrip("0")

    def _read_events_for_range(self, path: Path, start_date: date, end_date: date) -> list[dict]:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        lines = self._unfold_ics_lines(raw)

        in_event = False
        current: dict[str, str] = {}
        events: list[dict] = []

        for line in lines:
            if line == "BEGIN:VEVENT":
                in_event = True
                current = {}
                continue
            if line == "END:VEVENT":
                in_event = False
                dt_raw = current.get("DTSTART", "")
                dt = self._parse_dt(dt_raw)
                if dt is None or not (start_date <= dt.date() <= end_date):
                    continue
                summary = (current.get("SUMMARY") or "Untitled event").strip()
                events.append(
                    {
                        "title": summary,
                        "time": self._format_time(dt, dt_raw),
                        "date": dt.date().isoformat(),
                        "day_label": dt.strftime("%A"),
                        "sort_key": dt.isoformat(),
                    }
                )
                continue
            if not in_event or ":" not in line:
                continue

            key, value = line.split(":", 1)
            key_name = key.split(";", 1)[0].strip().upper()
            if key_name in {"DTSTART", "SUMMARY"} and key_name not in current:
                current[key_name] = value.strip()

        events.sort(key=lambda item: item.get("sort_key", ""))
        for item in events:
            item.pop("sort_key", None)
        return events

    @staticmethod
    def _brief_for_event(event: dict, include_day: bool) -> str:
        prefix = ""
        if include_day:
            day_label = str(event.get("day_label") or "").strip()
            if day_label:
                prefix = f"{day_label} "
        return f"{prefix}{event.get('time', '').strip()} {event.get('title', '').strip()}".strip()

    @classmethod
    def _build_schedule_copy(cls, scope: str, events: list[dict]) -> tuple[str, str]:
        if scope == "tomorrow":
            if not events:
                return ("Nothing on your calendar tomorrow.", "You're clear tomorrow. Nothing is scheduled on your calendar.")
            lead = "; ".join(cls._brief_for_event(item, include_day=False) for item in events[:3])
            remaining = len(events) - 3
            if remaining > 0:
                lead = f"{lead}; +{remaining} more"
            return (lead, f"Tomorrow looks like this: {lead}.")

        if scope == "upcoming":
            if not events:
                return (
                    "Nothing coming up in the next 7 days.",
                    "Your calendar looks open for the next 7 days.",
                )
            lead = "; ".join(cls._brief_for_event(item, include_day=True) for item in events[:4])
            remaining = len(events) - 4
            if remaining > 0:
                lead = f"{lead}; +{remaining} more"
            return (lead, f"Here's what's coming up: {lead}.")

        if not events:
            return ("Nothing on your calendar today.", "You're clear today. Nothing is scheduled on your calendar.")
        lead = "; ".join(cls._brief_for_event(item, include_day=False) for item in events[:3])
        remaining = len(events) - 3
        if remaining > 0:
            lead = f"{lead}; +{remaining} more"
        return (lead, f"Today's schedule: {lead}.")

    @staticmethod
    def _widget_payload(
        *,
        summary: str,
        events: list[dict],
        connected: bool,
        status: str,
        scope: str = "today",
        source_label: str = "",
        setup_hint: str = "",
    ) -> dict:
        return {
            "type": "calendar",
            "summary": summary,
            "events": events,
            "connected": connected,
            "status": status,
            "scope": scope,
            "source_label": source_label,
            "setup_hint": setup_hint,
        }

    async def handle(self, query: str) -> SkillResult:
        path = self._calendar_path()
        if path is None:
            summary = "Not connected."
            setup_hint = "Add a local .ics file in Settings -> Connections to enable schedule-aware answers and briefs."
            return SkillResult(
                success=True,
                message="Calendar is ready when you are. Add a local .ics file in Settings to get schedule-aware answers and briefs.",
                data={"connected": False, "events": [], "setup_hint": setup_hint, "source_label": ""},
                widget_data=self._widget_payload(
                    summary=summary,
                    events=[],
                    connected=False,
                    status="not_connected",
                    scope="today",
                    source_label="",
                    setup_hint=setup_hint,
                ),
                skill=self.name,
            )

        try:
            scope, start_date, end_date = self._scope_from_query(query)
            events = self._read_events_for_range(path, start_date, end_date)
        except Exception:
            return SkillResult(
                success=True,
                message="Calendar data is currently unavailable.",
                data={"connected": True, "events": [], "source_label": path.name, "setup_hint": ""},
                widget_data=self._widget_payload(
                    summary="Unavailable.",
                    events=[],
                    connected=True,
                    status="unavailable",
                    scope=scope,
                    source_label=path.name,
                    setup_hint="",
                ),
                skill=self.name,
            )

        summary, message = self._build_schedule_copy(scope, events)

        return SkillResult(
            success=True,
            message=message,
            data={"connected": True, "events": events, "source_label": path.name, "setup_hint": "", "scope": scope},
            widget_data=self._widget_payload(
                summary=summary,
                events=events,
                connected=True,
                status="ok",
                scope=scope,
                source_label=path.name,
                setup_hint="",
            ),
            skill=self.name,
        )
