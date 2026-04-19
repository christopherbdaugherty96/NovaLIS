"""
meta_intent_handler.py
======================
Handles conversational meta-intents that don't require an LLM call.

Covers:
  - Greetings          "hello", "hi", "hey", "good morning" …
  - What can you do    "what can you do", "list capabilities", "help" …
  - Out of scope       "can you send a text?", "why can't you book flights?" …
  - Phase / status     "what phase are you in", "what tier is this?" …
  - What's planned     "what's coming next", "what's on the roadmap?" …

Usage::

    handler = MetaIntentHandler()
    response = handler.handle(user_text)
    if response is not None:
        # send response, skip LLM
        ...

Returns ``None`` when the text doesn't match any meta-intent so the caller
can continue to the general-chat fallback.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Registry path (relative to this file's package root)
# ---------------------------------------------------------------------------
_SRC_DIR = Path(__file__).resolve().parent.parent
_REGISTRY_PATH = _SRC_DIR / "config" / "registry.json"

# ---------------------------------------------------------------------------
# Current build state — update alongside MasterRoadMap / Now.md
# ---------------------------------------------------------------------------
_CURRENT_TIER = "Tier 2"
_CURRENT_TIER_GOAL = "first real-world action"
_CURRENT_STATUS = (
    "Email drafting (cap 64) shipped — Nova can now prepare an email and open "
    "it in your mail client. You always decide whether to send."
)
_NEXT_UP = (
    "Tier 2.5 — backup and restore, uninstaller, offline awareness, "
    "and a log export."
)
_PLANNED = (
    "After that: refactoring the large internal files (Tier 3), then a full "
    "distribution channel, user support, and security maintenance (Tier 4). "
    "Calendar write is planned but not yet authorised."
)

# ---------------------------------------------------------------------------
# Human-readable group labels
# ---------------------------------------------------------------------------
_GROUP_LABELS: dict[str, str] = {
    "intelligence":   "Research and information",
    "local_control":  "Computer and local control",
    "speech_output":  "Voice output",
    "communication":  "Email and communication",
    "diagnostics":    "System diagnostics",
    "home_agent":     "Home agent",
}

# Short user-facing labels per capability name (overrides raw snake_case name)
_CAP_LABELS: dict[str, str] = {
    "governed_web_search":       "Web search",
    "open_website":              "Open a website",
    "speak_text":                "Read text aloud",
    "open_file_folder":          "Open files and folders",
    "volume_up_down":            "Volume control",
    "media_play_pause":          "Media play / pause",
    "brightness_control":        "Brightness control",
    "response_verification":     "Verify an answer",
    "external_reasoning_review": "Second opinion",
    "os_diagnostics":            "System status",
    "multi_source_reporting":    "Multi-source report",
    "headline_summary":          "News headline summary",
    "intelligence_brief":        "Intelligence brief",
    "topic_memory_map":          "Topic memory map",
    "story_tracker_update":      "Track a news story",
    "story_tracker_view":        "View tracked stories",
    "analysis_document":         "Analysis document",
    "weather_snapshot":          "Weather",
    "news_snapshot":             "News snapshot",
    "calendar_snapshot":         "Calendar snapshot",
    "screen_capture":            "Screenshot",
    "screen_analysis":           "Screen analysis",
    "explain_anything":          "Explain what you're looking at",
    "memory_governance":         "Governed memory",
    "openclaw_execute":          "Morning brief / home agent",
    "send_email_draft":          "Email draft (opens in your mail client)",
}

# ---------------------------------------------------------------------------
# Intent patterns
# ---------------------------------------------------------------------------

_GREETING_RE = re.compile(
    r"^\s*(?:"
    r"(?:hey|hi|hello|howdy|greetings|yo|sup|hiya)[\s,!.]*(?:nova|there|friend)?[!.]*"
    r"|good\s+(?:morning|afternoon|evening|day)[\s,!.]*(?:nova)?"
    r"|morning|afternoon|evening"
    r")\s*$",
    re.IGNORECASE,
)

_WHAT_CAN_YOU_DO_RE = re.compile(
    r"^\s*(?:"
    r"what\s+can\s+(?:you|nova)\s+do"
    r"|what\s+(?:are\s+)?(?:your\s+)?capabilities"
    r"|show\s+(?:me\s+)?(?:your\s+)?capabilities"
    r"|list\s+capabilities"
    r"|what\s+(?:do\s+you|does\s+nova)\s+(?:support|handle|know(?:\s+how\s+to\s+do)?)"
    r"|(?:help|commands|options|menu)"
    r"|what\s+(?:can\s+i\s+(?:ask|do)|(?:should|could)\s+i\s+(?:ask|say|try))"
    r"|(?:show|tell)\s+me\s+what\s+(?:you|nova)\s+can\s+do"
    r")\s*[.?!]*\s*$",
    re.IGNORECASE,
)

_OUT_OF_SCOPE_RE = re.compile(
    r"^\s*(?:"
    r"(?:can|could|will|would|does|is)\s+(?:you|nova)\s+(?:be\s+able\s+to\s+)?"
    r"|why\s+(?:can(?:not|'t)|won't|doesn'?t|isn'?t)\s+(?:you|nova)\s+"
    r"|why\s+(?:can'?t|won'?t|doesn'?t)\s+(?:it|this)\s+"
    r"|(?:i\s+wish\s+(?:you|nova)|i\s+want\s+(?:you|nova)\s+to)\s+"
    r")",
    re.IGNORECASE,
)

_PHASE_QUERY_RE = re.compile(
    r"^\s*(?:"
    r"what\s+(?:phase|tier|stage|version)\s+(?:are\s+you\s+(?:in|at)|is\s+(?:nova|this))"
    r"|(?:which|what)\s+(?:phase|tier|stage)\s+(?:is\s+(?:nova|this)\s+(?:in|at)|are\s+you\s+(?:in|at))"
    r"|current\s+(?:phase|tier|stage|build)(?:\s+(?:status|state|number|info))?"
    r"|(?:phase|tier|stage|build)\s+(?:status|state|number|info)"
    r")\s*[.?!]*\s*$",
    re.IGNORECASE,
)

_WHATS_PLANNED_RE = re.compile(
    r"^\s*(?:"
    r"what(?:'?s|\s+is)\s+(?:coming(?:\s+\w+)*|next|planned|on\s+the\s+roadmap|in\s+the\s+pipeline)"
    r"|what(?:'?s|\s+is)\s+(?:nova\s+)?working\s+on\s+next"
    r"|(?:future|upcoming)\s+(?:features?|capabilities?|plans?)"
    r"|roadmap"
    r"|what\s+will\s+(?:you|nova)\s+(?:be\s+able\s+to\s+\S+|get|have|support)"
    r"|when\s+will\s+(?:you|nova)\s+(?:be\s+able\s+to|get|have|support)"
    r"|when\s+(?:is|will)\s+.+\s+(?:coming|available|ready|supported)"
    r")\s*[.?!]*\s*$",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Registry loader (cached per process)
# ---------------------------------------------------------------------------

_registry_cache: Optional[dict] = None


def _load_registry() -> dict:
    global _registry_cache
    if _registry_cache is None:
        try:
            _registry_cache = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
        except Exception:
            _registry_cache = {}
    return _registry_cache


def _all_caps_by_group() -> dict[str, list[tuple[str, bool]]]:
    """
    Return {group_label: [(cap_label, is_active), ...]} for ALL capabilities,
    active or not, so Nova can give a complete honest picture.
    """
    reg = _load_registry()
    caps_by_id: dict[int, dict] = {
        int(c["id"]): c
        for c in reg.get("capabilities", [])
    }
    groups: dict[str, list[int]] = reg.get("capability_groups", {})

    result: dict[str, list[tuple[str, bool]]] = {}
    seen: set[int] = set()

    for group_key, cap_ids in groups.items():
        label = _GROUP_LABELS.get(group_key, group_key.replace("_", " ").title())
        entries: list[tuple[str, bool]] = []
        for cid in cap_ids:
            if cid in caps_by_id and cid not in seen:
                seen.add(cid)
                cap = caps_by_id[cid]
                name = cap.get("name", "")
                is_active = bool(cap.get("enabled")) and cap.get("status") == "active"
                entries.append((_CAP_LABELS.get(name, name.replace("_", " ").title()), is_active))
        if entries:
            result[label] = entries

    # Anything not in a named group
    ungrouped: list[tuple[str, bool]] = []
    for cid, cap in caps_by_id.items():
        if cid not in seen:
            name = cap.get("name", "")
            is_active = bool(cap.get("enabled")) and cap.get("status") == "active"
            ungrouped.append((_CAP_LABELS.get(name, name.replace("_", " ").title()), is_active))
    if ungrouped:
        result.setdefault("Other", []).extend(ungrouped)

    return result


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------

def _build_greeting() -> str:
    return "Hello. How can I help?"


def _build_what_can_you_do() -> str:
    groups = _all_caps_by_group()
    if not groups:
        return (
            "I have 26 governed capabilities across research, local control, "
            "email drafting, memory, and more. Type a request to get started."
        )

    active_total = sum(1 for entries in groups.values() for _, active in entries if active)
    inactive_total = sum(1 for entries in groups.values() for _, active in entries if not active)
    total = active_total + inactive_total

    lines: list[str] = [
        f"Nova has {total} capabilities. "
        f"{active_total} are active now"
        + (f", {inactive_total} are not yet active." if inactive_total else "."),
        "",
    ]

    for group_label, entries in groups.items():
        lines.append(f"{group_label}:")
        for cap_label, is_active in entries:
            status = "on" if is_active else "off"
            lines.append(f"  [{status}]  {cap_label}")
        lines.append("")

    lines.append(
        'Ask me anything on the [on] list directly. '
        'Type "what\'s planned" to see what\'s coming next.'
    )
    return "\n".join(lines).strip()


def _build_out_of_scope(text: str) -> str:
    # Try to pull out what they were asking about
    snip = text.strip().rstrip(".?!")
    if len(snip) > 80:
        snip = snip[:77] + "..."
    return (
        f"That's not something I can do yet.\n\n"
        f"Nova is designed to stay inside a defined set of governed capabilities "
        f"and expand only when each new one is fully verified. "
        f"If you're asking about something like sending messages, booking, "
        f"or writing files — those aren't available in the current build.\n\n"
        f'Type "what can you do" to see what is available today, '
        f'or "what\'s planned" to see what\'s coming next.'
    )


def _build_phase_status() -> str:
    return (
        f"Nova is currently in {_CURRENT_TIER} — {_CURRENT_TIER_GOAL}.\n\n"
        f"{_CURRENT_STATUS}\n\n"
        f"Next up: {_NEXT_UP}"
    )


def _build_whats_planned() -> str:
    return (
        f"Current focus ({_CURRENT_TIER}): {_CURRENT_STATUS}\n\n"
        f"Next: {_NEXT_UP}\n\n"
        f"{_PLANNED}"
    )


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class MetaIntentHandler:
    """
    Matches a small set of conversational meta-intents and returns a
    deterministic response — no LLM call required.

    Returns ``None`` if the text doesn't match any meta-intent.
    """

    def handle(self, text: str) -> Optional[str]:
        """Return a response string or None."""
        # Normalise curly/smart apostrophes so regexes can use plain '
        t = text.strip().replace("\u2019", "'").replace("\u2018", "'")
        if not t:
            return None

        if _GREETING_RE.match(t):
            return _build_greeting()

        if _WHAT_CAN_YOU_DO_RE.match(t):
            return _build_what_can_you_do()

        if _PHASE_QUERY_RE.match(t):
            return _build_phase_status()

        if _WHATS_PLANNED_RE.match(t):
            return _build_whats_planned()

        if _OUT_OF_SCOPE_RE.match(t):
            return _build_out_of_scope(t)

        return None
