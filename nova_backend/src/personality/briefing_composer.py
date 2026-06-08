from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from src.personality.chief_of_staff_profile import ChiefOfStaffProfile

EMPTY_BRIEFING_TEXT = "I do not see anything that needs your attention right now."


@dataclass(frozen=True)
class BriefingSection:
    """One section of a composed briefing."""

    label: str
    priority: int
    lines: tuple[str, ...]
    source_timestamp: float | None = None


@dataclass(frozen=True)
class Briefing:
    """Immutable briefing output — presentation-only."""

    sections: tuple[BriefingSection, ...]
    mode: str
    generated_at: float

    def as_text(self) -> str:
        if not self.sections:
            return EMPTY_BRIEFING_TEXT
        parts: list[str] = []
        for section in self.sections:
            parts.append(f"**{section.label}**")
            for line in section.lines:
                parts.append(f"  {line}")
            if section.source_timestamp is not None:
                age = self.generated_at - section.source_timestamp
                if age > _DEFAULT_PROFILE.default_staleness_threshold_seconds:
                    mins = int(age // 60)
                    parts.append(f"  (data from {mins} minutes ago)")
        return "\n".join(parts)

    def as_unprioritized_text(self) -> str:
        if not self.sections:
            return EMPTY_BRIEFING_TEXT
        parts: list[str] = []
        for section in sorted(self.sections, key=lambda s: s.label):
            parts.append(f"**{section.label}**")
            for line in section.lines:
                parts.append(f"  {line}")
            if section.source_timestamp is not None:
                age = self.generated_at - section.source_timestamp
                if age > _DEFAULT_PROFILE.default_staleness_threshold_seconds:
                    mins = int(age // 60)
                    parts.append(f"  (data from {mins} minutes ago)")
        return "\n".join(parts)


_DEFAULT_PROFILE = ChiefOfStaffProfile()


class BriefingComposer:
    """Composes briefings from immutable snapshot data.

    Receives only plain dicts, frozen dataclasses, tuples, strings,
    and numbers. Never receives live store/service/client instances.
    Never calls capabilities, executors, or governance components.
    """

    def __init__(
        self,
        *,
        profile: ChiefOfStaffProfile | None = None,
    ) -> None:
        self._profile = profile or _DEFAULT_PROFILE

    def compose(
        self,
        *,
        session_data: Mapping[str, Any] | None = None,
        thread_snapshot: Sequence[Mapping[str, Any]] | None = None,
        notice_snapshot: Sequence[Mapping[str, Any]] | None = None,
        mode: str = "home",
    ) -> Briefing:
        now = time.time()
        sections: list[BriefingSection] = []

        if session_data:
            sections.extend(self._extract_session_sections(session_data, now))

        if thread_snapshot:
            sections.extend(self._extract_thread_sections(thread_snapshot))

        if notice_snapshot:
            sections.extend(self._extract_notice_sections(notice_snapshot))

        sections.sort(key=lambda s: s.priority)

        return Briefing(
            sections=tuple(sections),
            mode=mode,
            generated_at=now,
        )

    def _extract_session_sections(
        self,
        data: Mapping[str, Any],
        now: float,
    ) -> list[BriefingSection]:
        sections: list[BriefingSection] = []

        shopify = data.get("shopify")
        if isinstance(shopify, dict):
            lines: list[str] = []
            order_count = shopify.get("order_count")
            if order_count is not None:
                lines.append(f"{order_count} orders.")
            revenue = shopify.get("revenue")
            if revenue is not None:
                lines.append(f"Revenue: ${revenue}.")
            inventory_alerts = shopify.get("inventory_alerts")
            if isinstance(inventory_alerts, (list, tuple)):
                for alert in inventory_alerts[:3]:
                    lines.append(f"Inventory alert: {alert}")
            if lines:
                ts = shopify.get("timestamp")
                sections.append(BriefingSection(
                    label="Shopify",
                    priority=10,
                    lines=tuple(lines),
                    source_timestamp=float(ts) if ts is not None else None,
                ))

        calendar = data.get("calendar")
        if isinstance(calendar, dict):
            lines = []
            events = calendar.get("events")
            if isinstance(events, (list, tuple)):
                for event in events[:5]:
                    if isinstance(event, dict):
                        lines.append(
                            f"{event.get('time', '?')}: {event.get('title', '?')}"
                        )
                    elif isinstance(event, str):
                        lines.append(event)
            if lines:
                ts = calendar.get("timestamp")
                sections.append(BriefingSection(
                    label="Calendar",
                    priority=20,
                    lines=tuple(lines),
                    source_timestamp=float(ts) if ts is not None else None,
                ))

        return sections

    def _extract_thread_sections(
        self,
        threads: Sequence[Mapping[str, Any]],
    ) -> list[BriefingSection]:
        if not threads:
            return []
        lines: list[str] = []
        for thread in threads[:5]:
            name = thread.get("name", "Unnamed")
            status = thread.get("status", "")
            blocker = thread.get("latest_blocker", "")
            line = str(name)
            if status:
                line += f" ({status})"
            if blocker:
                line += f" — blocked: {blocker}"
            lines.append(line)
        return [
            BriefingSection(
                label="Project Threads",
                priority=15,
                lines=tuple(lines),
            ),
        ]

    def _extract_notice_sections(
        self,
        notices: Sequence[Mapping[str, Any]],
    ) -> list[BriefingSection]:
        active = [
            n for n in notices
            if isinstance(n, dict) and n.get("status", "active") == "active"
        ]
        if not active:
            return []
        lines: list[str] = []
        for notice in active[:3]:
            summary = notice.get("summary", "")
            if summary:
                lines.append(str(summary))
        return [
            BriefingSection(
                label="Notices",
                priority=5,
                lines=tuple(lines),
            ),
        ]
