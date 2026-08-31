"""Deterministic, read-only projection for Nova's personal operating loop."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.conversation.personal_operations_intent import PersonalOperationsIntent
from src.trust.session_activity import correlate_action_receipts

_MAX_ITEMS = 5
_WAITING_TAGS = {"waiting", "waiting_on", "blocked", "blocker", "dependency"}
_OPEN_TAGS = {"open", "open_loop", "pending", "todo", "task", "next", "next_action"}


@dataclass(frozen=True)
class DailyLoopItem:
    text: str
    source: str


@dataclass(frozen=True)
class DailyLoopSource:
    source: str
    status: str
    detail: str


@dataclass(frozen=True)
class DailyLoopProjection:
    next: tuple[DailyLoopItem, ...]
    changed: tuple[DailyLoopItem, ...]
    waiting_on: tuple[DailyLoopItem, ...]
    open_loops: tuple[DailyLoopItem, ...]
    completed_today: tuple[DailyLoopItem, ...]
    unresolved_outcomes: tuple[DailyLoopItem, ...]
    recommended_next: DailyLoopItem | None
    context_today: tuple[DailyLoopItem, ...]
    sources: tuple[DailyLoopSource, ...]
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        if self.execution_performed or self.authorization_granted:
            raise ValueError("DailyLoopProjection cannot execute or grant authority.")


def _clean(value: Any, *, limit: int = 160) -> str:
    return " ".join(str(value or "").strip().split())[:limit]


def _append(items: list[DailyLoopItem], text: Any, source: str) -> None:
    clean = _clean(text)
    if not clean or any(item.text.casefold() == clean.casefold() for item in items):
        return
    if len(items) < _MAX_ITEMS:
        items.append(DailyLoopItem(clean, source))


def _memory_text(item: dict[str, Any]) -> str:
    return _clean(
        item.get("content_raw")
        or item.get("body")
        or item.get("content")
        or item.get("text")
        or item.get("title")
    )


def _memory_labels(item: dict[str, Any]) -> set[str]:
    labels = {str(tag).strip().lower() for tag in list(item.get("tags") or [])}
    category = str(item.get("category") or item.get("type") or "").strip().lower()
    if category:
        labels.add(category)
    title = str(item.get("title") or "").strip().lower()
    for label in _WAITING_TAGS | _OPEN_TAGS:
        if title.startswith(f"{label.replace('_', ' ')}:"):
            labels.add(label)
    return labels


def _is_current_memory(item: dict[str, Any]) -> bool:
    lock = dict(item.get("lock") or {})
    return (
        not bool(item.get("deleted"))
        and bool(item.get("user_visible", True))
        and not str(lock.get("superseded_by") or "").strip()
        and str(item.get("tier") or "active").strip().lower() in {"active", "locked"}
    )


def _memory_shape_is_valid(item: dict[str, Any]) -> bool:
    return isinstance(item.get("tags", []), list) and isinstance(item.get("lock", {}), dict)


def _parse_timestamp(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed


def _non_action_receipt_detail(receipt: dict[str, Any]) -> str:
    return _clean(
        receipt.get("capability_name")
        or receipt.get("outcome_reason")
        or receipt.get("message")
        or str(receipt.get("event_type") or "").lower().replace("_", " ")
    )


def _receipt_shape_is_valid(receipt: dict[str, Any]) -> bool:
    if str(receipt.get("event_type") or "") not in {"ACTION_ATTEMPTED", "ACTION_COMPLETED"}:
        return True
    capability_id = receipt.get("capability_id")
    if capability_id in (None, ""):
        return True
    try:
        int(capability_id)
    except (TypeError, ValueError):
        return False
    return True


def _explicit_unresolved_session_loops(session_state: dict[str, Any]) -> list[str]:
    context = session_state.get("conversation_context")
    if not isinstance(context, dict):
        return []
    loops: list[str] = []
    for item in list(context.get("open_loops") or []):
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").strip().lower() != "unresolved":
            continue
        text = _clean(item.get("text") or item.get("title") or item.get("body"))
        if text:
            loops.append(text)
    return loops


def _calendar_payload(session_state: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
    widget = session_state.get("brief_calendar")
    if isinstance(widget, dict):
        data = widget.get("data") if isinstance(widget.get("data"), dict) else widget
        status = str(data.get("status") or "").strip().lower()
        connected = data.get("connected") is True and status not in {
            "error",
            "not_connected",
            "not_configured",
            "unavailable",
        }
        return connected, list(data.get("events") or []) if connected else []
    events = list(session_state.get("last_calendar_events") or [])
    return (bool(events), events)


def _weather_payload(session_state: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    widget = session_state.get("brief_weather")
    if not isinstance(widget, dict):
        return False, {}
    data = widget.get("data") if isinstance(widget.get("data"), dict) else widget
    status = str(data.get("status") or "").strip().lower()
    connected = data.get("connected") is True and status not in {
        "error",
        "not_connected",
        "not_configured",
        "unavailable",
    }
    return connected, dict(data) if connected else {}


def _calendar_event_is_upcoming(event: dict[str, Any], now: datetime) -> bool:
    raw_date = str(event.get("date") or "").strip()
    if not raw_date:
        return False
    try:
        event_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    except ValueError:
        return False
    if event_date != now.date():
        return event_date > now.date()
    raw_time = str(event.get("time") or "").strip()
    if raw_time.lower() == "all day":
        return True
    try:
        event_time = datetime.strptime(raw_time, "%I:%M %p").time()
    except ValueError:
        return False
    return event_time >= now.time().replace(tzinfo=None)


def compose_daily_loop_projection(
    *,
    session_state: dict[str, Any] | None = None,
    memory_items: list[dict[str, Any]] | None = None,
    reminders: list[dict[str, Any]] | None = None,
    receipts: list[dict[str, Any]] | None = None,
    now: datetime | None = None,
    memory_available: bool = True,
    reminders_available: bool = True,
    receipts_available: bool = True,
) -> DailyLoopProjection:
    """Project already-loaded/readable Nova state without fetching or mutating it."""

    state = dict(session_state) if isinstance(session_state, dict) else {}
    raw_memories = list(memory_items or [])
    if not all(isinstance(item, dict) and _memory_shape_is_valid(item) for item in raw_memories):
        memory_available = False
        memories: list[dict[str, Any]] = []
    else:
        memories = [item for item in raw_memories if _is_current_memory(item)]
    schedules = [item for item in list(reminders or []) if isinstance(item, dict)]
    raw_receipts = list(receipts or [])
    if not all(isinstance(item, dict) and _receipt_shape_is_valid(item) for item in raw_receipts):
        receipts_available = False
        receipt_rows: list[dict[str, Any]] = []
    else:
        receipt_rows = raw_receipts
    local_now = now if now is not None else datetime.now().astimezone()

    next_items: list[DailyLoopItem] = []
    changed: list[DailyLoopItem] = []
    waiting: list[DailyLoopItem] = []
    open_loops: list[DailyLoopItem] = []
    completed: list[DailyLoopItem] = []
    unresolved: list[DailyLoopItem] = []
    change_candidates: list[tuple[datetime, str]] = []
    context: list[DailyLoopItem] = []
    sources: list[DailyLoopSource] = []

    calendar_connected, events = _calendar_payload(state)
    for event in events:
        if not isinstance(event, dict) or not _calendar_event_is_upcoming(event, local_now):
            continue
        time_label = _clean(event.get("time"), limit=30)
        title = _clean(event.get("title") or "Untitled calendar event")
        _append(next_items, f"{time_label} — {title}" if time_label else title, "calendar")
    sources.append(
        DailyLoopSource(
            "calendar",
            "available" if calendar_connected else "not_loaded",
            "Cached calendar state is available." if calendar_connected else "Calendar is not loaded in this session.",
        )
    )

    for item in memories:
        text = _memory_text(item)
        labels = _memory_labels(item)
        if labels & _WAITING_TAGS:
            _append(waiting, text, "governed_memory")
        if labels & _OPEN_TAGS:
            _append(open_loops, text, "governed_memory")
        if labels & {"next", "next_action"}:
            _append(next_items, text, "governed_memory")
    sources.append(
        DailyLoopSource(
            "governed_memory",
            "available" if memory_available else "unavailable",
            f"{len(memories)} current governed-memory item(s) inspected."
            if memory_available
            else "Governed memory could not be read.",
        )
    )

    for reminder in schedules:
        if not bool(reminder.get("active", True)):
            continue
        if str(reminder.get("kind") or "reminder").strip().lower() == "daily_brief":
            continue
        body = _clean(reminder.get("body") or reminder.get("title"))
        due = _clean(reminder.get("next_run_at"), limit=40)
        _append(next_items, f"{due} — {body}" if due else body, "local_reminders")
        _append(open_loops, body, "local_reminders")
    sources.append(
        DailyLoopSource(
            "local_reminders",
            "available" if reminders_available else "unavailable",
            f"{len(schedules)} active local reminder/schedule item(s) inspected."
            if reminders_available
            else "Local reminders could not be read.",
        )
    )

    action_items = sorted(
        correlate_action_receipts(receipt_rows),
        key=lambda item: str(item.get("outcome_timestamp_utc") or ""),
        reverse=True,
    )
    for item in action_items:
        detail = _clean(item.get("source_label") or item.get("label"))
        timestamp = _parse_timestamp(item.get("outcome_timestamp_utc"))
        if timestamp is None or timestamp.astimezone().date() != local_now.date():
            continue
        receipt_state = str(item.get("classification") or "")
        if str(item.get("activity_origin") or "").strip().lower() == "background_read":
            background_labels = {
                "background_read": "completed",
                "effect_verified": "completed",
                "accepted_unverified": "outcome unverified",
                "unknown_unverified": "outcome unknown",
                "failed": "failed",
                "rejected_or_unsupported": "rejected",
            }
            background_state = background_labels.get(receipt_state, "status unknown")
            change_candidates.append(
                (
                    timestamp,
                    f"Background read {background_state}: {detail}",
                )
            )
            continue
        if receipt_state == "effect_verified":
            _append(completed, detail, "receipts")
            change_candidates.append((timestamp or datetime.min.replace(tzinfo=timezone.utc), f"Completed: {detail}"))
        elif receipt_state == "accepted_unverified":
            _append(unresolved, f"Accepted; outcome unverified: {detail}", "receipts")
            change_candidates.append(
                (
                    timestamp or datetime.min.replace(tzinfo=timezone.utc),
                    f"Accepted; outcome unverified: {detail}",
                )
            )
        elif receipt_state == "unknown_unverified":
            _append(unresolved, f"Outcome unknown; not verified: {detail}", "receipts")
            change_candidates.append(
                (
                    timestamp or datetime.min.replace(tzinfo=timezone.utc),
                    f"Outcome unknown; not verified: {detail}",
                )
            )
        elif receipt_state == "failed":
            change_candidates.append((timestamp or datetime.min.replace(tzinfo=timezone.utc), f"Failed: {detail}"))
        elif receipt_state == "rejected_or_unsupported":
            change_candidates.append((timestamp or datetime.min.replace(tzinfo=timezone.utc), f"Rejected: {detail}"))

    for receipt in receipt_rows:
        event_type = str(receipt.get("event_type") or "").strip()
        if event_type in {"ACTION_ATTEMPTED", "ACTION_COMPLETED"}:
            continue
        timestamp = _parse_timestamp(receipt.get("timestamp_utc"))
        if timestamp is None or timestamp.astimezone().date() != local_now.date():
            continue
        change_candidates.append(
            (
                timestamp or datetime.min.replace(tzinfo=timezone.utc),
                _non_action_receipt_detail(receipt),
            )
        )
    for _, detail in sorted(change_candidates, key=lambda candidate: candidate[0], reverse=True):
        _append(changed, detail, "receipts")
    sources.append(
        DailyLoopSource(
            "receipts",
            "available" if receipts_available else "unavailable",
            f"{len(receipt_rows)} recent receipt(s) inspected."
            if receipts_available
            else "Receipts could not be read.",
        )
    )

    for loop in _explicit_unresolved_session_loops(state):
        _append(open_loops, loop, "session_context")
    sources.append(DailyLoopSource("session_context", "available", "Current-session state inspected."))

    weather_connected, weather_data = _weather_payload(state)
    if weather_connected:
        summary = _clean(weather_data.get("summary") or weather_data.get("forecast"))
        if summary:
            _append(context, summary, "weather")
        sources.append(DailyLoopSource("weather", "available", "Cached weather state is available."))
    else:
        sources.append(DailyLoopSource("weather", "not_loaded", "Weather is not loaded in this session."))

    news_items = list(state.get("news_cache") or [])
    for article in news_items[:2]:
        title = article.get("title") if isinstance(article, dict) else article
        _append(context, title, "news")
    failed_news_refresh = any(
        int(item.get("capability_id") or 0) == 56
        and str(item.get("classification") or "") == "failed"
        for item in action_items
    )
    if news_items:
        sources.append(DailyLoopSource("news", "available", "Cached news state is available."))
    elif failed_news_refresh:
        sources.append(
            DailyLoopSource(
                "news",
                "unavailable",
                "The attempted news refresh failed; current news evidence is unavailable.",
            )
        )
    else:
        sources.append(DailyLoopSource("news", "not_loaded", "News is not loaded in this session."))
    sources.append(DailyLoopSource("google_tasks", "not_connected", "Google Tasks is not connected."))

    recommendation: DailyLoopItem | None = None
    if next_items:
        recommendation = DailyLoopItem(next_items[0].text, f"recommendation_from:{next_items[0].source}")
    elif waiting:
        recommendation = DailyLoopItem(
            f"Review waiting item: {waiting[0].text}",
            f"recommendation_from:{waiting[0].source}",
        )
    elif open_loops:
        recommendation = DailyLoopItem(
            f"Continue open loop: {open_loops[0].text}",
            f"recommendation_from:{open_loops[0].source}",
        )

    return DailyLoopProjection(
        next=tuple(next_items),
        changed=tuple(changed),
        waiting_on=tuple(waiting),
        open_loops=tuple(open_loops),
        completed_today=tuple(completed),
        unresolved_outcomes=tuple(unresolved),
        recommended_next=recommendation,
        context_today=tuple(context),
        sources=tuple(sources),
    )


def render_daily_loop_answer(
    intent: PersonalOperationsIntent,
    projection: DailyLoopProjection,
) -> str:
    """Render one intent from evidence, with source and missing-state truth."""

    selected = {
        PersonalOperationsIntent.MATTERS_TODAY: projection.next + projection.waiting_on + projection.context_today,
        PersonalOperationsIntent.NEXT: projection.next,
        PersonalOperationsIntent.CHANGED: projection.changed,
        PersonalOperationsIntent.WAITING_ON: projection.waiting_on,
        PersonalOperationsIntent.NEED_TO_FINISH: projection.open_loops,
        PersonalOperationsIntent.COMPLETED_TODAY: projection.completed_today,
    }.get(intent, ())

    title = {
        PersonalOperationsIntent.MATTERS_TODAY: "What matters today",
        PersonalOperationsIntent.NEXT: "What you have next",
        PersonalOperationsIntent.CHANGED: "What changed",
        PersonalOperationsIntent.WAITING_ON: "What you're waiting on",
        PersonalOperationsIntent.NEED_TO_FINISH: "What you needed to finish",
        PersonalOperationsIntent.RECOMMENDED_NEXT: "What you should do next",
        PersonalOperationsIntent.COMPLETED_TODAY: "What you finished today",
    }[intent]
    lines = [f"{title}:"]

    if intent == PersonalOperationsIntent.RECOMMENDED_NEXT:
        if projection.recommended_next is None:
            lines.append("- No recommendation is supported by the available state.")
        else:
            lines.append(
                f"- Recommendation (derived, not an instruction): {projection.recommended_next.text} "
                f"[source: {projection.recommended_next.source}]"
            )
    elif selected:
        lines.extend(f"- {item.text} [source: {item.source}]" for item in selected[:_MAX_ITEMS])
    else:
        lines.append("- No matching items are present in the available state.")

    if intent == PersonalOperationsIntent.WAITING_ON and projection.unresolved_outcomes:
        lines.append(f"- Unresolved action outcomes: {len(projection.unresolved_outcomes)}")
    missing = [source.detail for source in projection.sources if source.status not in {"available"}]
    if missing:
        lines.append("Missing-source truth:")
        lines.extend(f"- {detail}" for detail in missing)
    lines.append("No action was executed.")
    return "\n".join(lines)
