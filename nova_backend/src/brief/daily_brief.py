"""Daily Brief synthesis module.

Assembles a structured on-demand daily brief from session state, memory,
recent action receipts, weather, calendar, and email data. Deterministic
and non-authorizing: no LLM calls, no capability invocations, no external
effects within this module. External data (weather, calendar) must be
fetched by the caller and injected as parameters.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from src.actions.action_result import ActionResult
from src.cognition.cognitive_layer_contract import (
    CognitiveMode,
    CognitiveRequest,
    CognitiveResult,
    validate_cognitive_result,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MAX_ITEMS_PER_SECTION = 5
_MAX_RECEIPT_LABEL_LEN = 80
_RECEIPT_LABEL_MAP: dict[str, str] = {
    "ACTION_COMPLETED": "action completed",
    "ACTION_ATTEMPTED": "action attempted",
    "EMAIL_DRAFT_CREATED": "email draft created",
    "EMAIL_DRAFT_FAILED": "email draft failed",
    "OPENCLAW_AGENT_RUN_COMPLETED": "OpenClaw run completed",
    "OPENCLAW_ACTION_APPROVED": "OpenClaw action approved",
    "OPENCLAW_ACTION_DENIED": "OpenClaw action denied",
    "MEMORY_ITEM_SAVED": "memory saved",
    "MEMORY_ITEM_DELETED": "memory deleted",
    "SCREEN_CAPTURE_COMPLETED": "screen captured",
    "POLICY_EXECUTION_COMPLETED": "policy executed",
    "POLICY_EXECUTION_BLOCKED": "policy blocked",
}

_INTENT_PATTERNS = (
    re.compile(r"\b(daily\s+brief|morning\s+brief|day\s+brief)\b", re.IGNORECASE),
    re.compile(r"\bwhat(?:'s| is)\s+(?:on\s+(?:my|the|your)?\s*)?(?:agenda|schedule|plate|today)\b", re.IGNORECASE),
    re.compile(r"\b(brief\s+me|catch\s+me\s+up|where\s+(am|are)\s+(i|we)|what\s+should\s+i\s+(do|focus))\b", re.IGNORECASE),
    re.compile(r"\b(open\s+loops?|what(?:'s|\s+is)\s+open|what(?:'s|\s+is)\s+pending)\b", re.IGNORECASE),
)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

class BriefConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class BriefSection:
    title: str
    items: tuple[str, ...]
    confidence: BriefConfidence = BriefConfidence.MEDIUM
    source_label: str = ""

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("BriefSection title must not be empty.")
        if not 0 <= len(self.items) <= _MAX_ITEMS_PER_SECTION * 2:
            raise ValueError(f"BriefSection items out of expected range: {len(self.items)}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "items": list(self.items),
            "confidence": self.confidence.value,
            "source_label": self.source_label,
        }

    @property
    def is_empty(self) -> bool:
        return not self.items


@dataclass(frozen=True)
class DailyBrief:
    """
    Assembled daily brief. Non-authorizing: does not execute, route through
    Governor, or call any capability. Read-only synthesis only.
    """

    date_covered: str
    timestamp_utc: str
    sections: tuple[BriefSection, ...]
    summary: str = ""
    confidence: BriefConfidence = BriefConfidence.LOW
    sources_consulted: tuple[str, ...] = ()

    # Non-authorizing invariants — must always be False
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        if self.execution_performed or self.authorization_granted:
            raise ValueError(
                "DailyBrief is non-authorizing: execution_performed and "
                "authorization_granted must both be False."
            )
        if not self.date_covered.strip():
            raise ValueError("DailyBrief date_covered must not be empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "date_covered": self.date_covered,
            "timestamp_utc": self.timestamp_utc,
            "summary": self.summary,
            "confidence": self.confidence.value,
            "sections": [s.to_dict() for s in self.sections],
            "sources_consulted": list(self.sources_consulted),
            "execution_performed": False,
            "authorization_granted": False,
        }

    def to_speakable(self) -> str:
        if self.summary:
            return self.summary
        parts: list[str] = []
        for section in self.sections:
            if section.is_empty:
                continue
            parts.append(f"{section.title}: {', '.join(section.items[:3])}.")
        return " ".join(parts) if parts else "No brief data available."

    @property
    def has_content(self) -> bool:
        return any(not s.is_empty for s in self.sections)


# ---------------------------------------------------------------------------
# Assembly helpers
# ---------------------------------------------------------------------------

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_label() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _clean(value: Any, *, limit: int = 200) -> str:
    text = str(value or "").strip()
    return text[:limit] if len(text) > limit else text


def _section_confidence(items: list[str]) -> BriefConfidence:
    if len(items) >= 3:
        return BriefConfidence.HIGH
    if len(items) >= 1:
        return BriefConfidence.MEDIUM
    return BriefConfidence.LOW


def _build_today_focus(
    session_state: dict[str, Any],
    working_context: dict[str, Any] | None,
) -> BriefSection:
    items: list[str] = []

    task_goal = _clean(
        (working_context or {}).get("task_goal")
        or session_state.get("task_goal")
        or session_state.get("active_topic")
        or ""
    )
    if task_goal:
        items.append(task_goal)

    active_app = _clean((working_context or {}).get("active_app") or "")
    if active_app and active_app not in items:
        items.append(f"Active: {active_app}")

    conv_topic = _clean(
        (session_state.get("conversation_context") or {}).get("topic") or ""
    )
    if conv_topic and conv_topic not in items:
        items.append(f"Topic: {conv_topic}")

    return BriefSection(
        title="Today's Focus",
        items=tuple(items[:_MAX_ITEMS_PER_SECTION]),
        confidence=_section_confidence(items),
        source_label="session",
    )


def _build_weather(weather_data: dict[str, Any] | None) -> BriefSection:
    """Build a weather section from pre-fetched WeatherService data."""
    if not weather_data:
        return BriefSection(
            title="Weather",
            items=(),
            confidence=BriefConfidence.LOW,
            source_label="weather",
        )

    status = str(weather_data.get("status") or "")
    connected = bool(weather_data.get("connected"))

    if not connected or status in {"not_configured", "unavailable"}:
        hint = _clean(weather_data.get("setup_hint") or weather_data.get("message") or "", limit=120)
        items = (hint,) if hint else ()
        return BriefSection(
            title="Weather",
            items=items,
            confidence=BriefConfidence.LOW,
            source_label="weather",
        )

    summary = _clean(weather_data.get("summary") or "", limit=160)
    forecast = _clean(weather_data.get("forecast") or "", limit=120)
    alerts = [_clean(a, limit=100) for a in (weather_data.get("alerts") or []) if str(a).strip()]

    items: list[str] = []
    if summary:
        items.append(summary)
    if forecast and forecast not in items:
        items.append(forecast)
    items.extend(f"Alert: {a}" for a in alerts[:2])

    return BriefSection(
        title="Weather",
        items=tuple(items[:_MAX_ITEMS_PER_SECTION]),
        confidence=BriefConfidence.HIGH if items else BriefConfidence.LOW,
        source_label="weather",
    )


def _build_calendar(calendar_data: dict[str, Any] | None) -> BriefSection:
    """Build a calendar section from pre-fetched CalendarSkill data."""
    if not calendar_data:
        return BriefSection(
            title="Calendar",
            items=(),
            confidence=BriefConfidence.LOW,
            source_label="calendar",
        )

    connected = bool(calendar_data.get("connected"))
    status = str(calendar_data.get("status") or "")

    if not connected or status in {"not_connected", "unavailable"}:
        hint = _clean(
            calendar_data.get("setup_hint")
            or "Add a local .ics file in Settings to enable calendar.",
            limit=120,
        )
        return BriefSection(
            title="Calendar",
            items=(hint,),
            confidence=BriefConfidence.LOW,
            source_label="calendar",
        )

    events = list(calendar_data.get("events") or [])
    items: list[str] = []
    for event in events[:_MAX_ITEMS_PER_SECTION]:
        if not isinstance(event, dict):
            continue
        time_label = _clean(event.get("time") or "", limit=20)
        title = _clean(event.get("title") or "Untitled", limit=80)
        entry = f"{time_label} — {title}" if time_label else title
        if entry:
            items.append(entry)

    if not items:
        scope = str(calendar_data.get("scope") or "today")
        items = [f"Nothing on your calendar {scope}."]

    return BriefSection(
        title="Calendar",
        items=tuple(items),
        confidence=BriefConfidence.HIGH if events else BriefConfidence.MEDIUM,
        source_label=_clean(calendar_data.get("source_label") or "calendar", limit=40),
    )


def _build_important_emails(important_emails: list[dict[str, Any]] | None) -> BriefSection:
    """
    Placeholder section for important emails.

    Will return live data once an email connector is configured.
    Currently returns a not-configured notice so the brief UI can show
    the section with a setup prompt.
    """
    if important_emails:
        items: list[str] = []
        for email in important_emails[:_MAX_ITEMS_PER_SECTION]:
            if not isinstance(email, dict):
                continue
            sender = _clean(email.get("sender") or "", limit=40)
            subject = _clean(email.get("subject") or "No subject", limit=80)
            entry = f"{sender}: {subject}" if sender else subject
            if entry:
                items.append(entry)
        if items:
            return BriefSection(
                title="Important Emails",
                items=tuple(items),
                confidence=BriefConfidence.HIGH,
                source_label="email",
            )

    return BriefSection(
        title="Important Emails",
        items=("Email connector not configured. Connect Gmail or IMAP in Settings.",),
        confidence=BriefConfidence.LOW,
        source_label="email_placeholder",
    )


def _build_next_actions(memory_items: list[dict[str, Any]]) -> BriefSection:
    actions: list[str] = []
    for item in memory_items:
        if not isinstance(item, dict):
            continue
        category = _clean(item.get("category") or item.get("type") or "")
        content = _clean(item.get("content") or item.get("text") or "")
        if not content:
            continue
        if category.lower() in {"action", "task", "todo", "next_action", "next"}:
            actions.append(content)
        if len(actions) >= _MAX_ITEMS_PER_SECTION:
            break

    return BriefSection(
        title="Top Next Actions",
        items=tuple(actions),
        confidence=_section_confidence(actions),
        source_label="memory",
    )


def _build_open_loops(memory_items: list[dict[str, Any]]) -> BriefSection:
    loops: list[str] = []
    for item in memory_items:
        if not isinstance(item, dict):
            continue
        category = _clean(item.get("category") or item.get("type") or "")
        content = _clean(item.get("content") or item.get("text") or "")
        if not content:
            continue
        if category.lower() in {"open_loop", "loop", "open", "pending", "unresolved"}:
            loops.append(content)
        if len(loops) >= _MAX_ITEMS_PER_SECTION:
            break

    return BriefSection(
        title="Open Loops",
        items=tuple(loops),
        confidence=_section_confidence(loops),
        source_label="memory",
    )


def _build_recent_decisions(memory_items: list[dict[str, Any]]) -> BriefSection:
    decisions: list[str] = []
    for item in memory_items:
        if not isinstance(item, dict):
            continue
        category = _clean(item.get("category") or item.get("type") or "")
        content = _clean(item.get("content") or item.get("text") or "")
        if not content:
            continue
        if category.lower() in {"decision", "choice", "resolved", "decided"}:
            decisions.append(content)
        if len(decisions) >= _MAX_ITEMS_PER_SECTION:
            break

    return BriefSection(
        title="Recent Decisions",
        items=tuple(decisions),
        confidence=_section_confidence(decisions),
        source_label="memory",
    )


def _build_memory_reminders(memory_items: list[dict[str, Any]]) -> BriefSection:
    reminders: list[str] = []
    for item in memory_items:
        if not isinstance(item, dict):
            continue
        category = _clean(item.get("category") or item.get("type") or "")
        content = _clean(item.get("content") or item.get("text") or "")
        if not content:
            continue
        if category.lower() in {"reminder", "note", "remember", "context", "preference"}:
            reminders.append(content)
        if len(reminders) >= _MAX_ITEMS_PER_SECTION:
            break

    return BriefSection(
        title="Memory Reminders",
        items=tuple(reminders),
        confidence=_section_confidence(reminders),
        source_label="memory",
    )


def _build_recent_receipts(recent_receipts: list[dict[str, Any]]) -> BriefSection:
    labels: list[str] = []
    for receipt in recent_receipts:
        event_type = str(receipt.get("event_type") or "")
        label = _RECEIPT_LABEL_MAP.get(event_type, event_type.lower().replace("_", " "))
        ts = str(receipt.get("timestamp_utc") or "")
        detail = _clean(
            receipt.get("capability_name")
            or receipt.get("outcome_reason")
            or receipt.get("message")
            or "",
            limit=60,
        )
        entry = f"{label}: {detail}" if detail else label
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                entry = f"{dt.strftime('%H:%M')} — {entry}"
            except ValueError:
                pass
        if entry not in labels:
            labels.append(entry)
        if len(labels) >= _MAX_ITEMS_PER_SECTION:
            break

    return BriefSection(
        title="Recent Actions",
        items=tuple(labels),
        confidence=BriefConfidence.HIGH if labels else BriefConfidence.LOW,
        source_label="receipts",
    )


def _build_blocked_items(memory_items: list[dict[str, Any]]) -> BriefSection:
    blocked: list[str] = []
    for item in memory_items:
        if not isinstance(item, dict):
            continue
        category = _clean(item.get("category") or item.get("type") or "")
        content = _clean(item.get("content") or item.get("text") or "")
        if not content:
            continue
        if category.lower() in {"blocked", "blocker", "stuck", "waiting", "dependency"}:
            blocked.append(content)
        if len(blocked) >= _MAX_ITEMS_PER_SECTION:
            break

    return BriefSection(
        title="Blocked Items",
        items=tuple(blocked),
        confidence=_section_confidence(blocked),
        source_label="memory",
    )


def _build_recommended_next_step(
    next_actions: BriefSection,
    open_loops: BriefSection,
    session_state: dict[str, Any],
) -> BriefSection:
    recommendation: str = ""

    # Priority: first open next action > first open loop > session goal
    if next_actions.items:
        recommendation = next_actions.items[0]
    elif open_loops.items:
        recommendation = f"Resolve: {open_loops.items[0]}"
    else:
        conv_goal = _clean(
            (session_state.get("conversation_context") or {}).get("user_goal") or ""
        )
        if conv_goal:
            recommendation = f"Continue: {conv_goal}"

    items = (recommendation,) if recommendation else ()
    return BriefSection(
        title="Recommended Next Step",
        items=items,
        confidence=BriefConfidence.MEDIUM if items else BriefConfidence.LOW,
        source_label="synthesis",
    )


def _overall_confidence(sections: list[BriefSection]) -> BriefConfidence:
    filled = [s for s in sections if not s.is_empty]
    if not filled:
        return BriefConfidence.LOW
    high_count = sum(1 for s in filled if s.confidence == BriefConfidence.HIGH)
    if high_count >= 2:
        return BriefConfidence.HIGH
    if len(filled) >= 2:
        return BriefConfidence.MEDIUM
    return BriefConfidence.LOW


def _build_summary(sections: list[BriefSection], date: str) -> str:
    filled = [s for s in sections if not s.is_empty]
    if not filled:
        return f"No brief data available for {date}."
    parts = []
    for section in filled[:3]:
        first = section.items[0] if section.items else ""
        if first:
            parts.append(first)
    if not parts:
        return f"Brief assembled for {date}."
    return f"For {date}: " + ". ".join(parts) + "."


# ---------------------------------------------------------------------------
# Public composition function
# ---------------------------------------------------------------------------

def compose_daily_brief(
    *,
    session_state: dict[str, Any] | None = None,
    memory_items: list[dict[str, Any]] | None = None,
    recent_receipts: list[dict[str, Any]] | None = None,
    working_context: dict[str, Any] | None = None,
    weather_data: dict[str, Any] | None = None,
    calendar_data: dict[str, Any] | None = None,
    important_emails: list[dict[str, Any]] | None = None,
) -> DailyBrief:
    """
    Assemble a DailyBrief from available data sources.

    All inputs are optional — returns a valid (possibly sparse) brief on
    any combination of missing data. Never raises on missing or malformed input.

    External data (weather_data, calendar_data, important_emails) must be
    fetched by the caller and injected here. This function is synchronous
    and produces no external effects.
    """
    _session = dict(session_state or {})
    _memory = list(memory_items or [])
    _receipts = list(recent_receipts or [])
    _ctx = dict(working_context or {})

    today = _today_label()
    now = _utc_now()

    focus = _build_today_focus(_session, _ctx)
    weather = _build_weather(weather_data)
    calendar = _build_calendar(calendar_data)
    emails = _build_important_emails(important_emails)
    next_actions = _build_next_actions(_memory)
    open_loops = _build_open_loops(_memory)
    decisions = _build_recent_decisions(_memory)
    reminders = _build_memory_reminders(_memory)
    receipts_section = _build_recent_receipts(_receipts)
    blocked = _build_blocked_items(_memory)
    recommended = _build_recommended_next_step(next_actions, open_loops, _session)

    all_sections = (
        focus,
        weather,
        calendar,
        emails,
        next_actions,
        open_loops,
        decisions,
        reminders,
        receipts_section,
        blocked,
        recommended,
    )

    sources: list[str] = []
    if _memory:
        sources.append("memory")
    if _receipts:
        sources.append("receipts")
    if _session:
        sources.append("session")
    if _ctx:
        sources.append("working_context")
    if weather_data and weather_data.get("connected"):
        sources.append("weather")
    if calendar_data and calendar_data.get("connected"):
        sources.append("calendar")

    confidence = _overall_confidence(list(all_sections))
    summary = _build_summary(list(all_sections), today)

    return DailyBrief(
        date_covered=today,
        timestamp_utc=now,
        sections=all_sections,
        summary=summary,
        confidence=confidence,
        sources_consulted=tuple(sources),
    )


# ---------------------------------------------------------------------------
# Output adapters
# ---------------------------------------------------------------------------

def brief_to_cognitive_result(brief: DailyBrief) -> CognitiveResult:
    """Convert a DailyBrief to a CognitiveResult for cognition pipeline use."""
    key_points = tuple(
        f"{s.title}: {s.items[0]}"
        for s in brief.sections
        if not s.is_empty
    )
    confidence_float = {"high": 0.85, "medium": 0.60, "low": 0.35}[brief.confidence.value]

    result = CognitiveResult(
        summary=brief.summary or brief.to_speakable(),
        key_points=key_points,
        supporting_sources=brief.sources_consulted,
        confidence=confidence_float,
        module_name="daily_brief",
        diagnostics={
            "date_covered": brief.date_covered,
            "sections_with_content": sum(1 for s in brief.sections if not s.is_empty),
            "total_sections": len(brief.sections),
        },
    )
    validate_cognitive_result(result)
    return result


def brief_to_action_result(brief: DailyBrief, *, request_id: str = "") -> ActionResult:
    """Wrap a DailyBrief in a governance-aware ActionResult."""
    return ActionResult.ok(
        message=f"Daily brief assembled for {brief.date_covered}.",
        speakable_text=brief.to_speakable(),
        structured_data=brief.to_dict(),
        request_id=request_id or None,
        authority_class="read_only",
        external_effect=False,
        reversible=True,
        risk_level="low",
    )


# ---------------------------------------------------------------------------
# Intent detection helper
# ---------------------------------------------------------------------------

def is_daily_brief_request(query: str) -> bool:
    """Return True if the query is asking for a daily brief."""
    normalized = str(query or "").strip()
    return any(pattern.search(normalized) for pattern in _INTENT_PATTERNS)
