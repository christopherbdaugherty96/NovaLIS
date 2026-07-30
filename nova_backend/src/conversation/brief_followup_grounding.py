from __future__ import annotations

import re
from datetime import datetime
from hashlib import sha256
from typing import Any

from src.brief.auralis_today import DECISION_ITEM_PREFIXES

DISCUSSION_MARKERS = (
    "tell me more",
    "more about",
    "why does",
    "why is",
    "why should",
    "what caused",
    "what does that mean",
    "what do you think",
    "how should i think",
    "should i",
    "will it",
    "later",
    "after that",
    "that warning",
    "second story",
    "first story",
    "third story",
    "headline",
    "headlines",
    "what matters",
    "what stands out",
    "keep an eye on",
    "what should i watch",
    "complete",
    "partial",
    "done",
)

FETCH_SHAPES = (
    re.compile(r"^\s*(?:what(?:'s| is)\s+)?(?:the\s+)?weather(?:\s+(?:today|forecast))?\s*\??\s*$", re.I),
    re.compile(r"^\s*(?:weather|forecast|news|headlines|calendar|agenda|daily brief|awareness brief)\s*$", re.I),
    re.compile(r"^\s*(?:latest|current|today'?s)\s+(?:news|headlines|weather|forecast)\s*\??\s*$", re.I),
)

# "top/lead/main story" is a natural news reference the ordinal path missed.
TOP_STORY_RE = re.compile(r"\b(?:top|lead|main|biggest)\s+(?:story|stories|headline|headlines)\b", re.I)

_AWARENESS_DECISION_FOLLOWUP_PATTERNS = (
    re.compile(r"\b(?:what|which)\s+decision\s+(?:actually\s+)?(?:requires?|needs?)\s+my\s+attention\b", re.I),
    re.compile(r"\bwhat\s+do\s+i\s+need\s+to\s+decide\b", re.I),
    re.compile(r"\bis\s+there\s+a\s+decision\s+i\s+need\s+to\s+make\b", re.I),
)

# Schedule / calendar / commitment questions. Kept specific to avoid over-capturing
# ordinary chat: explicit schedule nouns, "am I free/busy", or "what do I have <when>".
# Schedule / calendar / commitment QUESTIONS only. Deliberately does not match a
# bare mention of "calendar"/"meeting" (which would over-capture "my calendar logo"
# or "create a calendar event"); it requires an interrogative schedule shape.
_SCHEDULE_Q_RE = re.compile(
    r"\bdo i have\b[^?]*\b(?:meetings?|appointments?|events?|plans?)\b"
    r"|\bwhat\s+(?:meetings?|appointments?)\b"
    r"|\bwhat(?:'s| is)\s+(?:on\s+)?(?:my|the)\s+(?:calendar|schedule|agenda|plate)\b"
    r"|\bwhat(?:'s| is| do i have| have i got| am i doing)\b[^?]*"
    r"\b(?:today|tomorrow|tonight|this\s+week|this\s+morning|this\s+afternoon|this\s+evening|weekend)\b"
    r"|\bam i (?:free|busy|available|booked)\b",
    re.I,
)

ORDINALS = {
    "first": 0,
    "1st": 0,
    "second": 1,
    "2nd": 1,
    "third": 2,
    "3rd": 2,
    "fourth": 3,
    "4th": 3,
    "fifth": 4,
    "5th": 4,
}


def is_fetch_shaped_brief_request(text: str) -> bool:
    clean = str(text or "").strip()
    return bool(clean and any(pattern.match(clean) for pattern in FETCH_SHAPES))


def is_schedule_commitment_question(text: str) -> bool:
    """True when the user is asking about their schedule, calendar, meetings,
    appointments, or commitments."""
    return bool(_SCHEDULE_Q_RE.search(str(text or "")))


def schedule_commitment_guard(text: str, session_state: dict[str, Any] | None) -> str:
    """Fallback truth guard for schedule/calendar/commitment questions. Hard backstop:
    a schedule question that reaches the general-chat fallback (i.e. grounded routing did
    not already answer it) must NEVER be handed to the local model, which otherwise
    fabricates commitments. Returns "" only for non-schedule questions.

    - Calendar loaded: answer deterministically from the sourced calendar facts (never the
      model), including the honest "nothing scheduled" case.
    - Calendar not loaded: refuse safely and say Nova won't guess.
    """
    state = session_state or {}
    if not is_schedule_commitment_question(text):
        return ""
    if _has_grounding_for("calendar", state):
        lines = _calendar_lines(state)
        if lines:
            return (
                "Sourced calendar facts:\n" + "\n".join(lines)
                + "\n\nThat is what the loaded calendar shows. I won't add commitments "
                "that aren't in it."
            )
        return (
            "Your calendar is loaded and shows nothing scheduled. I won't invent "
            "meetings or appointments that aren't there."
        )
    return (
        "I don't have your calendar loaded right now, so I can't tell you what's on "
        "your schedule — and I won't guess. Ask me to check your calendar and I'll "
        "pull up what's actually there."
    )


def is_discussion_shaped_brief_followup(text: str, session_state: dict[str, Any] | None) -> bool:
    clean = str(text or "").strip()
    if not clean or is_fetch_shaped_brief_request(clean):
        return False
    state = session_state or {}
    if not _has_grounding(state):
        return False
    lowered = clean.lower()
    explicit_key = _select_explicit_item_key(lowered, state)
    if explicit_key:
        return _has_grounding_for(explicit_key, state) and _has_domain_discussion_shape(explicit_key, lowered, state)
    active_key = str(state.get("active_brief_item") or "").strip()
    return bool(active_key) and _has_grounding_for(active_key, state) and _has_active_reference_shape(active_key, lowered, state)


def build_grounded_brief_context(text: str, session_state: dict[str, Any] | None) -> str:
    state = session_state or {}
    if not is_discussion_shaped_brief_followup(text, state):
        return ""
    key = _select_item_key(str(text or "").lower(), state)
    sections: list[str] = []

    if key in {"weather", "awareness_brief"}:
        weather = _weather_lines(state)
        if weather:
            sections.append("Weather [source: Visual Crossing/weather widget; status: sourced]\n" + "\n".join(weather))

    if key in {"news", "awareness_brief"}:
        news = _news_lines(str(text or ""), state)
        if news:
            sections.append("News [source: loaded RSS/news widget; status: sourced]\n" + "\n".join(news))

    if key in {"calendar", "awareness_brief"}:
        calendar = _calendar_lines(state)
        if calendar:
            sections.append("Calendar [source: local .ics/calendar widget; status: sourced]\n" + "\n".join(calendar))

    if key in {"runtime", "awareness_brief"}:
        runtime = _runtime_lines(state)
        if runtime:
            sections.append("Runtime status [source: runtime/trust status; status: sourced]\n" + "\n".join(runtime))

    if not sections:
        return ""

    return (
        "Grounded brief facts for this follow-up:\n"
        + "\n\n".join(sections)
        + "\n\nAnswer discipline for this grounded follow-up:\n"
        "- Use only these sourced facts for factual claims about the brief item.\n"
        "- If the sourced facts do not explicitly contain the answer, say: "
        "\"The loaded source does not say.\" Do not infer a yes/no answer from adjacent facts.\n"
        "- If you add interpretation, put it under an `Inference:` label and keep it clearly "
        "separate from sourced facts.\n"
        "- Do not reuse or upgrade your own prior wording as a source."
    )


def answer_grounded_brief_followup(text: str, session_state: dict[str, Any] | None) -> str:
    state = session_state or {}
    lowered = str(text or "").lower()
    key = _select_item_key(lowered, state)

    if key == "weather":
        return _answer_weather_followup(lowered, state)
    if key == "news":
        return _answer_news_followup(str(text or ""), state)
    if key == "calendar":
        return _answer_calendar_followup(str(text or ""), state)
    if key == "runtime":
        return _answer_runtime_followup(state)
    if key == "awareness_brief":
        return _answer_awareness_followup(str(text or ""), state)
    return ""


def store_brief_widget(
    session_state: dict[str, Any],
    key: str,
    widget: dict[str, Any],
    *,
    set_focus: bool = False,
) -> None:
    if not isinstance(session_state, dict) or not isinstance(widget, dict):
        return
    item_key = str(key or "").strip().lower()
    if item_key == "weather":
        session_state["brief_weather"] = dict(widget)
        if set_focus:
            session_state["active_brief_item"] = "weather"
    elif item_key == "news":
        items = list(widget.get("items") or [])
        session_state["news_cache"] = items
        session_state["news_categories"] = dict(widget.get("categories") or {})
        _validate_active_news_story(session_state, items)
        if set_focus:
            session_state["active_brief_item"] = "news"
    elif item_key == "calendar":
        session_state["brief_calendar"] = dict(widget)
        session_state["last_calendar_summary"] = str(widget.get("summary") or "")
        events = _sorted_calendar_events(list(widget.get("events") or []))
        session_state["last_calendar_events"] = events
        _validate_active_calendar_event(session_state, events)
        if set_focus:
            session_state["active_brief_item"] = "calendar"


def store_awareness_brief_surface(
    session_state: dict[str, Any],
    awareness_payload: dict[str, Any],
    *,
    set_focus: bool = False,
) -> None:
    """Store the rendered Awareness Brief without touching Cap 50 cluster state."""
    if not isinstance(session_state, dict) or not isinstance(awareness_payload, dict):
        return
    clusters: list[dict[str, Any]] = []
    for section in list(awareness_payload.get("sections") or []):
        if not isinstance(section, dict):
            continue
        items = [
            str(item or "").strip()
            for item in list(section.get("items") or [])
            if str(item or "").strip()
        ]
        status = str(section.get("status") or "").strip().lower()
        clusters.append(
            {
                "key": str(section.get("key") or "").strip(),
                "title": str(section.get("title") or "").strip(),
                "summary": items[0] if items else "",
                "items": items,
                "implication": "",
                "source": str(section.get("source") or "").strip(),
                "status": status,
                "placeholder": status != "ok" or not items,
                "synthesis_status": "sourced" if status == "ok" and items else (status or "unavailable"),
            }
        )
    session_state["awareness_brief_clusters"] = clusters
    if set_focus:
        session_state["active_brief_item"] = "awareness_brief"


def store_active_news_surface(
    session_state: dict[str, Any],
    surface_type: str,
    stories: list[Any],
    *,
    category_key: str = "",
) -> None:
    """Record the exact visible news collection used by numeric follow-ups.

    The surface is conversation state only. It does not authorize or execute
    anything; it prevents a later story number from silently resolving against
    an older collection.
    """
    if not isinstance(session_state, dict):
        return
    rows = [dict(story or {}) for story in stories if isinstance(story, dict)]
    identities = [_story_identity(row) for row in rows]
    version_seed = "\n".join([str(surface_type or ""), str(category_key or ""), *identities])
    session_state["active_news_surface"] = {
        "surface_type": str(surface_type or "news").strip() or "news",
        "surface_id": sha256(version_seed.encode("utf-8")).hexdigest(),
        "category_key": str(category_key or "").strip().lower(),
        "stories": rows,
        "index_to_story": {index: identity for index, identity in enumerate(identities, start=1)},
    }
    session_state["active_brief_item"] = "news"
    _validate_active_news_story(session_state, rows)


def active_news_surface_clusters(session_state: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Return the active surface in the cluster shape Cap 50 already accepts."""
    state = session_state or {}
    surface = state.get("active_news_surface")
    if not isinstance(surface, dict):
        return list(state.get("last_brief_clusters") or [])
    rows = list(surface.get("stories") or [])
    if str(surface.get("surface_type") or "") == "brief":
        return [dict(row or {}) for row in rows if isinstance(row, dict)]
    clusters: list[dict[str, Any]] = []
    for index, item in enumerate(rows, start=1):
        row = dict(item or {})
        title = _clip(row.get("title") or row.get("headline"))
        if not title:
            continue
        source = _clip(row.get("source") or row.get("publisher") or row.get("domain"), 80)
        clusters.append(
            {
                "id": index,
                "title": title,
                "summary": _clip(row.get("summary") or row.get("description")),
                "implication": "",
                "sources": [source] if source else [],
                "items": [row],
                "placeholder": False,
                "synthesis_status": "headline",
            }
        )
    return clusters


def _has_grounding(state: dict[str, Any]) -> bool:
    return any(
        (
            state.get("brief_weather"),
            state.get("news_cache"),
            state.get("news_categories"),
            state.get("last_brief_clusters"),
            state.get("awareness_brief_clusters"),
            state.get("brief_calendar"),
            state.get("last_calendar_events"),
            state.get("trust_status"),
        )
    )


def _has_grounding_for(key: str, state: dict[str, Any]) -> bool:
    if key == "weather":
        return bool(state.get("brief_weather"))
    if key == "news":
        return bool(state.get("news_cache") or state.get("news_categories") or state.get("last_brief_clusters"))
    if key == "calendar":
        return bool(state.get("brief_calendar") or state.get("last_calendar_events"))
    if key == "runtime":
        return bool(state.get("trust_status"))
    if key == "awareness_brief":
        return bool(
            state.get("awareness_brief_clusters")
            or state.get("last_brief_clusters")
        ) or _has_grounding(state)
    return False


def _select_item_key(lowered: str, state: dict[str, Any]) -> str:
    return _select_explicit_item_key(lowered, state) or _select_active_reference_key(lowered, state)


def _select_explicit_item_key(lowered: str, state: dict[str, Any]) -> str:
    overview_markers = (
        "what matters most",
        "what stands out",
        "what should i watch",
        "keep an eye on",
    )
    active_surface = state.get("active_news_surface")
    active_key = str(state.get("active_brief_item") or "").strip()
    if (
        active_key == "awareness_brief"
        and state.get("awareness_brief_clusters")
        and _is_awareness_decision_followup(lowered)
    ):
        return "awareness_brief"
    if (
        active_key == "awareness_brief"
        and state.get("awareness_brief_clusters")
        and any(marker in lowered for marker in overview_markers)
    ):
        return "awareness_brief"
    if (
        active_key == "news"
        and isinstance(active_surface, dict)
        and active_surface.get("surface_type") != "brief"
        and any(marker in lowered for marker in overview_markers)
    ):
        return "news"
    if state.get("last_brief_clusters") and any(
        marker in lowered
        for marker in overview_markers
    ):
        return "awareness_brief"
    if state.get("active_news_surface") and any(marker in lowered for marker in overview_markers):
        return "news"
    if _contains_any_word(lowered, ("weather", "forecast", "rain", "raining", "temperature", "outside")):
        return "weather"
    if _contains_any_word(lowered, ("news", "headline", "headlines", "article")):
        return "news"
    if TOP_STORY_RE.search(lowered):
        return "news"
    if _ordinal_index(lowered) is not None and _contains_any_word(lowered, ("story", "stories")):
        return "news"
    if _contains_any_word(lowered, ("calendar", "schedule", "agenda")):
        return "calendar"
    if "after that" in lowered and state.get("active_calendar_event"):
        return "calendar"
    if _ordinal_index(lowered) is not None and _contains_any_word(lowered, ("event", "events", "meeting", "meetings")):
        return "calendar"
    if _contains_any_word(lowered, ("warning", "runtime")) or re.search(r"\bconnection\s+status\b", lowered):
        return "runtime"
    if _contains_any_word(lowered, ("brief",)) and _has_discussion_shape(lowered):
        return "awareness_brief"
    return ""


def _select_active_reference_key(lowered: str, state: dict[str, Any]) -> str:
    if _has_reference_shape(lowered):
        return str(state.get("active_brief_item") or "").strip()
    return ""


def _contains_any_word(text: str, words: tuple[str, ...]) -> bool:
    return any(re.search(rf"\b{re.escape(word)}\b", text) for word in words)


def _is_awareness_decision_followup(lowered: str) -> bool:
    return any(pattern.search(lowered) for pattern in _AWARENESS_DECISION_FOLLOWUP_PATTERNS)


def _has_discussion_shape(lowered: str) -> bool:
    return any(marker in lowered for marker in DISCUSSION_MARKERS) or _is_vague_followup(lowered)


def _has_domain_discussion_shape(key: str, lowered: str, state: dict[str, Any]) -> bool:
    if key == "weather":
        return (
            _contains_any_word(lowered, ("rain", "raining", "forecast", "temperature", "outside"))
            or "later" in lowered
            or re.search(r"\bwill\s+it\b", lowered) is not None
        )
    if key == "news":
        if state.get("active_news_surface") and any(
            marker in lowered
            for marker in ("what matters most", "what stands out", "what should i watch", "keep an eye on")
        ):
            return True
        if _ordinal_index(lowered) is not None and _contains_any_word(lowered, ("story", "stories", "headline", "headlines")):
            return True
        if TOP_STORY_RE.search(lowered):
            return True
        return bool(state.get("active_news_story")) and _has_reference_shape(lowered)
    if key == "calendar":
        if "after that" in lowered and state.get("active_calendar_event"):
            return True
        if _ordinal_index(lowered) is not None and _contains_any_word(lowered, ("event", "events", "meeting", "meetings")):
            return True
        return bool(state.get("active_calendar_event")) and _has_reference_shape(lowered)
    if key == "runtime":
        return (
            _contains_any_word(lowered, ("warning", "runtime"))
            or re.search(r"\bconnection\s+status\b", lowered) is not None
        ) and any(marker in lowered for marker in ("what caused", "why", "cause", "mean", "meaning", "that warning"))
    if key == "awareness_brief":
        return _is_awareness_decision_followup(lowered) or _has_reference_shape(lowered) or any(
            marker in lowered
            for marker in (
                "why does",
                "what matters",
                "what stands out",
                "what changed",
                "what should i watch",
                "keep an eye on",
                "complete",
                "partial",
                "done",
            )
        )
    return False


def _has_active_reference_shape(key: str, lowered: str, state: dict[str, Any]) -> bool:
    if key == "calendar" and "after that" in lowered:
        return bool(state.get("active_calendar_event"))
    return _has_reference_shape(lowered)


def _has_reference_shape(lowered: str) -> bool:
    return _contains_any_word(lowered, ("that", "this", "it")) or any(
        marker in lowered
        for marker in (
            "why does",
            "why is",
            "why should",
            "what does that mean",
            "tell me more",
            "more about that",
            "after that",
        )
    )


def _unwrap_widget_data(widget: dict[str, Any]) -> dict[str, Any]:
    data = widget.get("data")
    return data if isinstance(data, dict) else widget


def _clip(value: Any, limit: int = 240) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) > limit:
        return text[: limit - 3].rstrip() + "..."
    return text


def _weather_lines(state: dict[str, Any]) -> list[str]:
    data = _weather_data(state)
    if not data:
        return []
    lines = []
    for field in ("summary", "status", "provider"):
        value = _clip(data.get(field))
        if value:
            lines.append(f"- {field}: {value}")
    forecast = data.get("forecast")
    if isinstance(forecast, dict):
        forecast_text = ", ".join(f"{key}: {_clip(value, 80)}" for key, value in forecast.items() if value)
        if forecast_text:
            lines.append(f"- forecast: {forecast_text}")
    precip = _precipitation_signal(data)
    if precip[1]:
        lines.append(f"- precipitation: {precip[1]}")
    return lines


def _weather_data(state: dict[str, Any]) -> dict[str, Any]:
    widget = state.get("brief_weather")
    if not isinstance(widget, dict):
        return {}
    return _unwrap_widget_data(widget)


def _news_lines(query: str, state: dict[str, Any]) -> list[str]:
    surface = state.get("active_news_surface")
    items = (
        list(surface.get("stories") or [])
        if isinstance(surface, dict) and surface.get("stories")
        else list(state.get("news_cache") or [])
    )
    target = _ordinal_index(query)
    if target is None and _is_vague_followup(query):
        active_story = state.get("active_news_story")
        if isinstance(active_story, dict):
            return [_story_line(active_story, int(state.get("active_news_story_display_index") or 1))]
        return []
    if not items:
        return []
    selected = items[target : target + 1] if target is not None and target < len(items) else items[:5]
    return [_story_line(dict(item or {}), index) for index, item in enumerate(selected, start=(target or 0) + 1)]


def _story_line(row: dict[str, Any], index: int) -> str:
    title = _clip(row.get("title") or row.get("headline"))
    source = _clip(row.get("source") or row.get("publisher") or row.get("domain"), 80)
    summary = _clip(row.get("summary") or row.get("description"))
    if not title:
        return ""
    line = f"- {index}. {title}"
    if source:
        line += f" ({source})"
    if summary:
        line += f": {summary}"
    return line


def _calendar_lines(state: dict[str, Any]) -> list[str]:
    summary = _clip(state.get("last_calendar_summary"))
    events = _sorted_calendar_events(list(state.get("last_calendar_events") or []))
    lines = [f"- summary: {summary}"] if summary else []
    for index, event in enumerate(events[:5], start=1):
        line = _calendar_event_line(dict(event or {}), index)
        if line:
            lines.append(line)
    return lines


def _calendar_event_line(row: dict[str, Any], index: int) -> str:
    title = _clip(row.get("summary") or row.get("title"))
    when = _clip(row.get("start") or row.get("dtstart") or row.get("time"), 120)
    if not title:
        return ""
    return f"- {index}. {title}" + (f" at {when}" if when else "")


def _runtime_lines(state: dict[str, Any]) -> list[str]:
    trust = state.get("trust_status")
    if not isinstance(trust, dict):
        return []
    lines = []
    for key in ("state", "status", "last_failure", "last_external_call", "last_local_call"):
        value = _clip(trust.get(key))
        if value:
            lines.append(f"- {key}: {value}")
    return lines


def _ordinal_index(query: str) -> int | None:
    lowered = str(query or "").lower()
    for token, index in ORDINALS.items():
        if re.search(rf"\b{re.escape(token)}\b", lowered):
            return index
    return None


def _is_vague_followup(query: str) -> bool:
    lowered = str(query or "").lower()
    return _has_reference_shape(lowered) or any(
        marker in lowered for marker in ("tell me more", "more about that")
    )


def _precipitation_signal(data: dict[str, Any]) -> tuple[str, str]:
    candidates = []
    for key in (
        "precip_probability",
        "precipProbability",
        "precipprob",
        "precip_prob",
        "chance_of_rain",
        "rain_probability",
        "pop",
    ):
        if key in data:
            candidates.append((key, data.get(key)))
    forecast = data.get("forecast")
    if isinstance(forecast, dict):
        for key, value in forecast.items():
            lowered_key = str(key).lower()
            if any(token in lowered_key for token in ("precip", "rain", "pop")):
                candidates.append((str(key), value))

    for key, value in candidates:
        parsed = _parse_probability(value)
        if parsed is None:
            continue
        rendered = f"{key}: {_clip(value, 80)}"
        if parsed > 0:
            return "positive", rendered
        return "negative", rendered
    return "unknown", ""


def _parse_probability(value: Any) -> float | None:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "").strip().lower()
    if not text:
        return None
    match = re.search(r"(-?\d+(?:\.\d+)?)\s*%?", text)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def _story_identity(item: dict[str, Any]) -> str:
    for key in ("url", "link", "id", "guid"):
        value = str(item.get(key) or "").strip()
        if value:
            return f"{key}:{value}"
    title = _clip(item.get("title") or item.get("headline"), 500)
    source = _clip(item.get("source") or item.get("publisher") or item.get("domain"), 120)
    return "title:" + sha256(f"{title}\n{source}".encode("utf-8")).hexdigest()


def _validate_active_news_story(state: dict[str, Any], items: list[Any]) -> None:
    active_id = str(state.get("active_news_story_id") or "").strip()
    if not active_id:
        return
    for index, item in enumerate(items):
        row = dict(item or {})
        if _story_identity(row) == active_id:
            state["active_news_story"] = row
            state["active_news_story_index"] = index
            state["active_news_story_display_index"] = index + 1
            return
    for key in ("active_news_story", "active_news_story_id", "active_news_story_index", "active_news_story_display_index"):
        state.pop(key, None)


def _remember_active_news_story(state: dict[str, Any], index: int) -> dict[str, Any] | None:
    surface = state.get("active_news_surface")
    items = (
        list(surface.get("stories") or [])
        if isinstance(surface, dict) and surface.get("stories")
        else list(state.get("news_cache") or [])
    )
    if index < 0 or index >= len(items):
        return None
    row = dict(items[index] or {})
    state["active_news_story"] = row
    state["active_news_story_id"] = _story_identity(row)
    state["active_news_story_index"] = index
    state["active_news_story_display_index"] = index + 1
    state["active_brief_item"] = "news"
    return row


def _parse_calendar_time(row: dict[str, Any]) -> datetime | None:
    raw = row.get("start") or row.get("dtstart")
    if isinstance(raw, dict):
        raw = raw.get("dateTime") or raw.get("date")
    text = str(raw or "").strip()
    if text:
        text = text.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(text)
        except ValueError:
            pass

    date_text = str(row.get("date") or "").strip()
    time_text = str(row.get("time") or "").strip()
    if not date_text:
        return None
    if not time_text or time_text.lower() == "all day":
        try:
            return datetime.fromisoformat(date_text)
        except ValueError:
            return None
    for fmt in ("%Y-%m-%d %I:%M %p", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(f"{date_text} {time_text}", fmt)
        except ValueError:
            continue
    return None


def _calendar_identity(event: dict[str, Any]) -> str:
    for key in ("uid", "id", "event_id"):
        value = str(event.get(key) or "").strip()
        if value:
            return f"{key}:{value}"
    title = _clip(event.get("summary") or event.get("title"), 500)
    when = _clip(event.get("start") or event.get("dtstart") or event.get("time"), 200)
    return "event:" + sha256(f"{title}\n{when}".encode("utf-8")).hexdigest()


def _sorted_calendar_events(events: list[Any]) -> list[dict[str, Any]]:
    rows = [dict(event or {}) for event in events]
    indexed = list(enumerate(rows))
    return [
        row
        for _, row in sorted(
            indexed,
            key=lambda pair: (
                _parse_calendar_time(pair[1]) is None,
                _parse_calendar_time(pair[1]) or datetime.max,
                pair[0],
            ),
        )
    ]


def _validate_active_calendar_event(state: dict[str, Any], events: list[dict[str, Any]]) -> None:
    active_id = str(state.get("active_calendar_event_id") or "").strip()
    if not active_id:
        return
    for index, event in enumerate(events):
        if _calendar_identity(event) == active_id:
            state["active_calendar_event"] = dict(event)
            state["active_calendar_event_index"] = index
            state["active_calendar_event_display_index"] = index + 1
            return
    for key in ("active_calendar_event", "active_calendar_event_id", "active_calendar_event_index", "active_calendar_event_display_index"):
        state.pop(key, None)


def _remember_active_calendar_event(state: dict[str, Any], events: list[dict[str, Any]], index: int) -> dict[str, Any] | None:
    if index < 0 or index >= len(events):
        return None
    row = dict(events[index])
    state["active_calendar_event"] = row
    state["active_calendar_event_id"] = _calendar_identity(row)
    state["active_calendar_event_index"] = index
    state["active_calendar_event_display_index"] = index + 1
    state["active_brief_item"] = "calendar"
    return row


def _answer_weather_followup(lowered: str, state: dict[str, Any]) -> str:
    lines = _weather_lines(state)
    if not lines:
        return "I do not have loaded weather facts to answer from yet."
    facts = " ".join(line.lstrip("- ") for line in lines)
    if any(term in lowered for term in ("rain", "raining", "shower", "storm")):
        precip_state, precip_fact = _precipitation_signal(_weather_data(state))
        if precip_state == "positive":
            return f"Sourced weather facts: {facts}\n\nInference: The loaded precipitation field ({precip_fact}) is above zero, so rain is possible. I do not have an hourly precipitation probability beyond the loaded source."
        if precip_state == "negative":
            return f"Sourced weather facts: {facts}\n\nThe loaded precipitation field ({precip_fact}) does not indicate rain. I should not convert rain-related wording into a positive forecast."
        if re.search(r"\b(rain|showers?|storm|thunder)\b", facts, re.I):
            return f"Sourced weather facts: {facts}\n\nThe loaded source includes rain-related wording, but no structured precipitation probability. I should not convert keyword presence into a positive rain forecast."
        return f"Sourced weather facts: {facts}\n\nThe loaded source does not say whether it will rain later. I should not infer a yes/no rain answer from cloud cover alone."
    return f"Sourced weather facts: {facts}\n\nInference: I can discuss what this means, but only from the loaded weather facts above."


def _answer_news_followup(query: str, state: dict[str, Any]) -> str:
    lowered = str(query or "").lower()
    target = _ordinal_index(query)
    if target is not None:
        selected = _remember_active_news_story(state, target)
        if selected is None:
            return "I do not have that numbered headline in the loaded news state."
    elif _is_vague_followup(query) and isinstance(state.get("active_news_story_index"), int):
        target = state["active_news_story_index"]
    elif _is_vague_followup(query) and state.get("active_brief_item") == "news":
        return "I do not have a selected headline for 'that' anymore. Please pick a headline number from the loaded news first."
    lines = _news_lines(query, state)
    if not lines:
        return "I do not have loaded headline facts to answer from yet."
    if any(marker in lowered for marker in ("what matters most", "what stands out")):
        return (
            "What matters most on the active news surface:\n"
            + lines[0]
            + "\n\nThis is a deterministic ranking of the visible sourced items; I am not adding outside facts."
        )
    if any(marker in lowered for marker in ("what should i watch", "keep an eye on")):
        return "What to watch on the active news surface:\n" + "\n".join(lines[:3])
    if target is not None:
        return (
            "Sourced headline from the loaded news state:\n"
            + "\n".join(lines)
            + "\n\nThe loaded source does not contain more detail than this summary. I can discuss implications as inference, but I should not add unstated facts."
        )
    return (
        "Sourced headlines from the loaded news state:\n"
        + "\n".join(lines)
        + "\n\nInference: These are the items Nova has loaded; I should not add details beyond them without a fresh source."
    )


def _answer_calendar_followup(query: str, state: dict[str, Any]) -> str:
    events = _sorted_calendar_events(list(state.get("last_calendar_events") or []))
    summary = _clip(state.get("last_calendar_summary"))
    if not events and not summary:
        return "I do not have loaded calendar facts to answer from yet."
    target = _ordinal_index(query)
    if target is not None:
        selected = _remember_active_calendar_event(state, events, target)
        if selected is None:
            return "I do not have that numbered calendar event in the loaded calendar state."
        return (
            "Sourced calendar event:\n"
            + _calendar_event_line(selected, target + 1)
            + "\n\nThe loaded source does not contain more detail than this event line."
        )
    if "after that" in str(query or "").lower():
        active_index = state.get("active_calendar_event_index")
        if not isinstance(active_index, int):
            return "I do not know which calendar event 'that' refers to. Please pick an event number first."
        next_index = active_index + 1
        if next_index >= len(events):
            return "Sourced calendar facts: there is no following event in the loaded calendar state."
        next_event = _remember_active_calendar_event(state, events, next_index)
        return "Sourced next calendar event:\n" + _calendar_event_line(next_event or {}, next_index + 1)
    lines = _calendar_lines(state)
    if not lines:
        return "I do not have loaded calendar facts to answer from yet."
    return "Sourced calendar facts:\n" + "\n".join(lines) + "\n\nIf the next-event answer is not explicit above, the loaded source does not say."


def _answer_runtime_followup(state: dict[str, Any]) -> str:
    lines = _runtime_lines(state)
    if not lines:
        return "I do not have loaded runtime-warning facts to answer from yet."
    return "Sourced runtime facts:\n" + "\n".join(lines) + "\n\nIf the cause is not explicit above, the loaded source does not say."


def _answer_awareness_followup(query: str, state: dict[str, Any]) -> str:
    awareness_clusters = list(state.get("awareness_brief_clusters") or [])
    use_awareness_surface = (
        str(state.get("active_brief_item") or "").strip() == "awareness_brief"
        and "awareness_brief_clusters" in state
    )
    cluster_source = awareness_clusters if use_awareness_surface else list(state.get("last_brief_clusters") or [])
    clusters = [dict(row or {}) for row in cluster_source if isinstance(row, dict)]
    if not clusters:
        if use_awareness_surface:
            return "The rendered Awareness Brief does not contain enough live information to identify a lead item."
        return "I do not have a rendered intelligence brief to answer from yet."

    lowered = str(query or "").lower()
    if use_awareness_surface and _is_awareness_decision_followup(lowered):
        return _answer_auralis_decision_followup(clusters)

    placeholders = [
        cluster
        for cluster in clusters
        if cluster.get("placeholder")
        or str(cluster.get("synthesis_status") or "").lower() in {"placeholder", "pending", "paused"}
    ]
    if any(term in lowered for term in ("complete", "partial", "done")):
        if placeholders:
            return (
                f"The rendered brief is partial: {len(placeholders)} of {len(clusters)} "
                "topic clusters still use fallback or pending synthesis."
            )
        return f"The rendered brief is complete: all {len(clusters)} topic clusters have sourced synthesis."

    if use_awareness_surface and len(placeholders) == len(clusters):
        return "The rendered Awareness Brief does not contain enough live information to identify a lead item."

    def render_cluster(cluster: dict[str, Any], *, include_implication: bool = True) -> str:
        title = _clip(cluster.get("title") or "Untitled topic")
        summary = _clip(cluster.get("summary"))
        implication = _clip(cluster.get("implication"))
        if cluster in placeholders:
            items = list(cluster.get("items") or [])
            fallback_title = _clip((items[0] or {}).get("title")) if items and isinstance(items[0], dict) else ""
            summary = summary or fallback_title or "Synthesis is unavailable for this topic."
        line = f"- {title}"
        if summary:
            line += f": {summary}"
        if include_implication and implication:
            line += f" Why it matters: {implication}"
        if use_awareness_surface:
            source = _clip(cluster.get("source"), 80)
            status = _clip(cluster.get("status"), 40)
            labels = []
            if source:
                labels.append(f"source: {source}")
            if status:
                labels.append(f"status: {status}")
            if labels:
                line += f" [{'; '.join(labels)}]"
        return line

    if use_awareness_surface and any(
        term in lowered
        for term in ("what matters", "what stands out", "what should i watch", "keep an eye on")
    ):
        lead = next(cluster for cluster in clusters if cluster not in placeholders)
        return "Lead sourced item from the rendered Awareness Brief:\n" + render_cluster(lead)

    if any(term in lowered for term in ("what matters", "what stands out")):
        lead = next((cluster for cluster in clusters if cluster not in placeholders), clusters[0])
        return (
            "What matters most in the rendered brief:\n"
            + render_cluster(lead)
            + ("\n\nThe brief is still partial, so this ranking uses only the visible sourced material." if placeholders else "")
        )

    if any(term in lowered for term in ("what should i watch", "keep an eye on")):
        selected = [cluster for cluster in clusters if _clip(cluster.get("implication"))][:3] or clusters[:2]
        return "What to watch from the rendered brief:\n" + "\n".join(
            render_cluster(cluster) for cluster in selected
        )

    return "Current rendered brief:\n" + "\n".join(render_cluster(cluster, include_implication=False) for cluster in clusters[:3])


def _answer_auralis_decision_followup(clusters: list[dict[str, Any]]) -> str:
    auralis = next(
        (cluster for cluster in clusters if str(cluster.get("key") or "").strip() == "auralis_today"),
        None,
    )
    if not auralis:
        return "The rendered Awareness Brief does not include Auralis Today decision information."

    source = _clip(auralis.get("source"), 80)
    status = _clip(auralis.get("status"), 40).lower()
    labels = []
    if source:
        labels.append(f"source: {source}")
    if status:
        labels.append(f"status: {status}")
    label_text = f" [{'; '.join(labels)}]" if labels else ""

    if auralis.get("placeholder") or status == "not_configured":
        return (
            "Auralis Today decision information is unavailable in the rendered Awareness Brief."
            + label_text
        )

    items = [
        str(item or "").strip()
        for item in list(auralis.get("items") or [])
        if str(item or "").strip()
    ]
    decision_lines = [
        next((item for item in items if item.startswith(prefix)), "")
        for prefix in DECISION_ITEM_PREFIXES
    ]
    if any(not line for line in decision_lines):
        return (
            "The rendered Auralis Today section does not contain the complete decision-label "
            "contract I need to answer."
            + label_text
        )

    return (
        "Displayed Auralis Today decision items:\n"
        + "\n".join(f"- {line}" for line in decision_lines)
        + label_text
        + "\n\nThese are displayed recommendations, not approval or permission to act."
    )
