from __future__ import annotations

import os
from datetime import datetime
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
        if "schedule" in q and any(
            hint in q for hint in ("my ", "on my", "what", "what's", "whats", "today", "tomorrow", "events")
        ):
            return True
        return False

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

    def _read_today_events(self, path: Path) -> list[dict]:
        raw = path.read_text(encoding="utf-8", errors="ignore")
        lines = self._unfold_ics_lines(raw)

        today = datetime.now().date()
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
                if dt is None or dt.date() != today:
                    continue
                summary = (current.get("SUMMARY") or "Untitled event").strip()
                events.append(
                    {
                        "title": summary,
                        "time": self._format_time(dt, dt_raw),
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
    def _widget_payload(
        *,
        summary: str,
        events: list[dict],
        connected: bool,
        status: str,
        source_label: str = "",
        setup_hint: str = "",
    ) -> dict:
        return {
            "type": "calendar",
            "summary": summary,
            "events": events,
            "connected": connected,
            "status": status,
            "source_label": source_label,
            "setup_hint": setup_hint,
        }

    async def handle(self, query: str) -> SkillResult:
        path = self._calendar_path()
        if path is None:
            summary = "Not connected."
            setup_hint = "Set NOVA_CALENDAR_ICS_PATH to a local .ics file to enable calendar snapshots."
            return SkillResult(
                success=True,
                message="Calendar is available, but no ICS file is connected yet.",
                data={"connected": False, "events": [], "setup_hint": setup_hint, "source_label": ""},
                widget_data=self._widget_payload(
                    summary=summary,
                    events=[],
                    connected=False,
                    status="not_connected",
                    source_label="",
                    setup_hint=setup_hint,
                ),
                skill=self.name,
            )

        try:
            events = self._read_today_events(path)
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
                    source_label=path.name,
                    setup_hint="",
                ),
                skill=self.name,
            )

        if not events:
            summary = "No events scheduled today."
            message = "No calendar events are scheduled for today."
        else:
            lead = "; ".join(f"{item['time']} {item['title']}" for item in events[:3])
            remaining = len(events) - 3
            if remaining > 0:
                lead = f"{lead}; +{remaining} more"
            summary = lead
            message = f"Today's calendar: {lead}."

        return SkillResult(
            success=True,
            message=message,
            data={"connected": True, "events": events, "source_label": path.name, "setup_hint": ""},
            widget_data=self._widget_payload(
                summary=summary,
                events=events,
                connected=True,
                status="ok",
                source_label=path.name,
                setup_hint="",
            ),
            skill=self.name,
        )
