"""
meta_intent_handler.py
======================
Handles conversational meta-intents that don't require an LLM call.

Covers:
  - Greetings          "hello", "hi", "hey", "good morning" …
  - Identity           "who are you", "who made you", "what is nova" …
  - What can you do    "what can you do", "list capabilities", "help" …
  - Category help      "what can you do with email", "help with research" …
  - Out of scope       "can you send a text?", "why can't you book flights?" …
  - Phase / status     "what phase are you in", "what tier is this?" …
  - What's planned     "what's coming next", "what's on the roadmap?" …

Usage::

    handler = MetaIntentHandler()
    response = handler.handle(user_text, session_state=session_state)
    if response is not None:
        # send response — no LLM call needed
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
# Registry path
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
    "intelligence":  "Research and information",
    "local_control": "Computer and local control",
    "speech_output": "Voice output",
    "communication": "Email and communication",
    "diagnostics":   "System diagnostics",
    "home_agent":    "Home agent",
}

# ---------------------------------------------------------------------------
# Plain-English capability labels (short name, used in full list)
# ---------------------------------------------------------------------------
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
    "calendar_snapshot":         "Calendar",
    "screen_capture":            "Screenshot",
    "screen_analysis":           "Screen analysis",
    "explain_anything":          "Explain what you're looking at",
    "memory_governance":         "Memory",
    "openclaw_execute":          "Morning brief / home agent",
    "send_email_draft":          "Email draft",
}

# ---------------------------------------------------------------------------
# Plain-English capability descriptions (one sentence, conversational)
# ---------------------------------------------------------------------------
_CAP_DESCRIPTIONS: dict[str, str] = {
    "governed_web_search": (
        "I can search the web and give you a summary of what I find."
    ),
    "open_website": (
        "I can open any website in your browser."
    ),
    "speak_text": (
        "I can read text out loud on your computer."
    ),
    "open_file_folder": (
        "I can open files and folders on your computer — I'll ask you to confirm first."
    ),
    "volume_up_down": (
        "I can turn the volume up, down, or mute it completely."
    ),
    "media_play_pause": (
        "I can play, pause, or skip media on your computer."
    ),
    "brightness_control": (
        "I can make your screen brighter or dimmer."
    ),
    "response_verification": (
        "I can check my own answer and flag anything that looks off."
    ),
    "external_reasoning_review": (
        "I can get a second opinion on something I said, from a separate model."
    ),
    "os_diagnostics": (
        "I can show you how your system is doing — models loaded, connections, status."
    ),
    "multi_source_reporting": (
        "I can pull information from multiple sources and write up a structured report."
    ),
    "headline_summary": (
        "I can summarize a headline or dig into a specific article."
    ),
    "intelligence_brief": (
        "I can put together a short briefing on a topic from today's news."
    ),
    "topic_memory_map": (
        "I can show you what topics are dominating the news right now."
    ),
    "story_tracker_update": (
        "I can start tracking a news story so you can follow it over time."
    ),
    "story_tracker_view": (
        "I can show you how a story has developed since you started tracking it."
    ),
    "analysis_document": (
        "I can write up a structured analysis document on any topic you give me."
    ),
    "weather_snapshot": (
        "I can check the current weather or the forecast."
    ),
    "news_snapshot": (
        "I can pull today's headlines for you."
    ),
    "calendar_snapshot": (
        "I can check what's on your calendar today."
    ),
    "screen_capture": (
        "I can take a screenshot of your screen."
    ),
    "screen_analysis": (
        "I can look at your screen and describe what's on it."
    ),
    "explain_anything": (
        "I can explain whatever you're looking at — a page, a document, an app."
    ),
    "memory_governance": (
        "I can remember things you tell me and bring them up later when they're useful."
    ),
    "openclaw_execute": (
        "I can run a morning brief or home agent template."
    ),
    "send_email_draft": (
        "I can draft an email and open it in your mail app — you decide whether to send."
    ),
}

# ---------------------------------------------------------------------------
# Category keyword mapping for "what can you do with X"
# ---------------------------------------------------------------------------
_CATEGORY_KEYWORDS: dict[str, str] = {
    # communication
    "email":         "communication",
    "mail":          "communication",
    "draft":         "communication",
    "compose":       "communication",
    # research / intelligence
    "research":      "intelligence",
    "news":          "intelligence",
    "search":        "intelligence",
    "web":           "intelligence",
    "weather":       "intelligence",
    "calendar":      "intelligence",
    "memory":        "intelligence",
    "remember":      "intelligence",
    "headline":      "intelligence",
    "brief":         "intelligence",
    "report":        "intelligence",
    "article":       "intelligence",
    "story":         "intelligence",
    "track":         "intelligence",
    "screen":        "intelligence",
    "explain":       "intelligence",
    "analyze":       "intelligence",
    "analysis":      "intelligence",
    # local control
    "computer":      "local_control",
    "volume":        "local_control",
    "brightness":    "local_control",
    "file":          "local_control",
    "folder":        "local_control",
    "website":       "local_control",
    "browser":       "local_control",
    "open":          "local_control",
    "media":         "local_control",
    "music":         "local_control",
    "play":          "local_control",
    "pause":         "local_control",
    # voice
    "voice":         "speech_output",
    "speak":         "speech_output",
    "aloud":         "speech_output",
    "read out":      "speech_output",
    "tts":           "speech_output",
    # diagnostics
    "system":        "diagnostics",
    "status":        "diagnostics",
    "health":        "diagnostics",
    "diagnostics":   "diagnostics",
    # home agent
    "agent":         "home_agent",
    "morning":       "home_agent",
    "template":      "home_agent",
}

# Known "not built yet" keyword sets — used to give specific out-of-scope messages
_NOT_BUILT_CATEGORIES: list[tuple[frozenset[str], str]] = [
    (
        frozenset({"twitter", "instagram", "facebook", "post", "tweet", "tiktok",
                   "social media", "linkedin", "reddit"}),
        "Posting to social media isn't something I'm set up for yet."
    ),
    (
        frozenset({"book", "reserve", "reservation", "hotel", "flight",
                   "restaurant", "uber", "lyft", "appointment"}),
        "I can't book or reserve things yet."
    ),
    (
        frozenset({"text", "sms", "whatsapp", "imessage", "telegram",
                   "signal", "dm", "direct message"}),
        "I can't send text messages or chat through other apps yet."
    ),
    (
        frozenset({"call", "phone call", "facetime", "video call", "zoom",
                   "ring", "dial"}),
        "Making calls isn't something I can do yet."
    ),
    (
        frozenset({"order", "buy", "purchase", "amazon", "shopping",
                   "checkout", "cart"}),
        "I can't place orders or make purchases yet."
    ),
    (
        frozenset({"transfer money", "pay", "venmo", "paypal", "bank",
                   "wire", "invoice"}),
        "I can't handle payments or banking yet."
    ),
    (
        frozenset({"write to file", "edit file", "delete file", "create file",
                   "save file", "modify file"}),
        "I can't write or edit files directly yet."
    ),
    (
        frozenset({"send email", "send the email", "send it"}),
        "I can draft an email and open it for you — but I can't send it on my own. "
        "You stay in control of what goes out."
    ),
]

# ---------------------------------------------------------------------------
# Intent patterns
# ---------------------------------------------------------------------------

_GREETING_RE = re.compile(
    r"^\s*(?:"
    r"(?:hey|hi|hello|howdy|greetings|yo|sup|hiya|heya|helo|hii|heyy)"
    r"[\s,!.]*(?:nova|there|friend|buddy)?[!.]*"
    r"|good\s+(?:morning|afternoon|evening|day)[\s,!.]*(?:nova)?"
    r"|morning|afternoon|evening"
    r"|(?:what(?:'?s|\s+is)\s+up|wassup|wazzup|sup\s+nova)"
    r")\s*$",
    re.IGNORECASE,
)

_IDENTITY_RE = re.compile(
    r"^\s*(?:"
    r"(?:who|what)\s+(?:are\s+you|is\s+nova)"
    r"|what(?:'?s|\s+is)\s+nova"
    r"|(?:tell|explain)\s+(?:me\s+)?(?:about\s+)?(?:yourself|nova|what\s+you\s+are)"
    r"|(?:describe|explain)\s+(?:yourself|nova)"
    r"|who\s+(?:made|built|created|designed|developed|owns?|runs?)\s+(?:you|nova|this)"
    r"|(?:who\s+is|who'?s)\s+(?:behind|responsible\s+for)\s+(?:you|nova|this)"
    r"|where\s+(?:do\s+you|did\s+you)\s+come\s+from"
    r"|are\s+you\s+an?\s+ai"
    r"|what\s+kind\s+of\s+(?:ai|assistant|program|software|app)\s+(?:are\s+you|is\s+(?:nova|this))"
    r"|(?:is|are)\s+(?:nova|you)\s+(?:open\s*source|free|private|local)"
    r"|how\s+(?:does\s+nova|do\s+you)\s+work"
    r"|(?:nova\s+)?(?:about|info|information)(?:\s+nova)?"
    r")\s*[.?!]*\s*$",
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
    r"|what\s+are\s+you\s+good\s+at"
    r"|what\s+do\s+you\s+(?:do|know)"
    r"|(?:can|could)\s+you\s+help(?:\s+me)?"
    r"|(?:i\s+need|i\s+want)\s+(?:some\s+)?help"
    r"|help\s+me"
    r"|(?:get\s+started|where\s+do\s+i\s+start|how\s+(?:do\s+i|can\s+i)\s+(?:use|start)(?:\s+(?:you|nova|this))?)"
    r"|what(?:'?s|\s+is)\s+(?:available|possible)"
    r")\s*[.?!]*\s*$",
    re.IGNORECASE,
)

_CATEGORY_HELP_RE = re.compile(
    r"^\s*(?:"
    r"what\s+can\s+(?:you|nova)\s+do\s+(?:with|for|about|on|around)\s+(?P<topic>\w[\w\s]*?)"
    r"|(?:help|assist)\s+(?:me\s+)?(?:with|for)\s+(?P<topic2>\w[\w\s]*?)"
    r"|(?:show|tell)\s+me\s+(?:what\s+you\s+can\s+do\s+(?:with|for)\s+)?(?P<topic3>\w[\w\s]*?)\s+(?:help|capabilities?|options?)"
    r"|(?P<topic4>\w[\w\s]*?)\s+(?:capabilities?|features?|options?|help)"
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

_LOCAL_STATUS_RE = re.compile(
    r"^\s*(?:"
    r"what\s+works\s+today"
    r"|what\s+(?:actually\s+)?works(?:\s+right\s+now)?"
    r"|what\s+can\s+nova\s+do\s+(?:today|right\s+now)"
    r"|explain\s+what\s+nova\s+can\s+do\s+in\s+plain\s+english"
    r"|what\s+should\s+i\s+try\s+first"
    r"|what\s+should\s+i\s+do\s+first"
    r"|where\s+should\s+i\s+start"
    r")\s*[.?!]*\s*$",
    re.IGNORECASE,
)

_MEMORY_AUTHORITY_RE = re.compile(
    r"^\s*(?:"
    r"can\s+memory\s+authorize\s+actions?"
    r"|does\s+memory\s+authorize\s+actions?"
    r"|can\s+(?:conversation|context|memory)\s+(?:approve|authorize)\s+(?:an\s+)?actions?"
    r"|is\s+memory\s+authority"
    r")\s*[.?!]*\s*$",
    re.IGNORECASE,
)

_MEMORY_EXPLAIN_RE = re.compile(
    r"^\s*(?:"
    r"what\s+does\s+memory\s+do"
    r"|explain\s+memory"
    r"|how\s+does\s+memory\s+work"
    r"|what\s+is\s+nova\s+memory"
    r")\s*[.?!]*\s*$",
    re.IGNORECASE,
)

_MEMORY_RECEIPTS_RE = re.compile(
    r"^\s*(?:"
    r"what\s+is\s+the\s+difference\s+between\s+memory\s+and\s+receipts"
    r"|difference\s+between\s+memory\s+and\s+receipts"
    r"|memory\s+vs\.?\s+receipts"
    r"|receipts\s+vs\.?\s+memory"
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


def _all_caps_by_group() -> dict[str, list[tuple[str, bool, str, bool]]]:
    """
    Return {group_label: [(label, is_active, cap_name, requires_confirmation), ...]}
    for ALL capabilities so responses can show status, descriptions, and confirmation notes.
    """
    reg = _load_registry()
    caps_by_id: dict[int, dict] = {int(c["id"]): c for c in reg.get("capabilities", [])}
    groups: dict[str, list[int]] = reg.get("capability_groups", {})

    result: dict[str, list[tuple[str, bool, str, bool]]] = {}
    seen: set[int] = set()

    for group_key, cap_ids in groups.items():
        label = _GROUP_LABELS.get(group_key, group_key.replace("_", " ").title())
        entries: list[tuple[str, bool, str, bool]] = []
        for cid in cap_ids:
            if cid in caps_by_id and cid not in seen:
                seen.add(cid)
                cap = caps_by_id[cid]
                name = cap.get("name", "")
                is_active = bool(cap.get("enabled")) and cap.get("status") == "active"
                needs_confirm = bool(cap.get("requires_confirmation"))
                entries.append((_CAP_LABELS.get(name, name.replace("_", " ").title()),
                                 is_active, name, needs_confirm))
        if entries:
            result[label] = entries

    ungrouped: list[tuple[str, bool, str, bool]] = []
    for cid, cap in caps_by_id.items():
        if cid not in seen:
            name = cap.get("name", "")
            is_active = bool(cap.get("enabled")) and cap.get("status") == "active"
            needs_confirm = bool(cap.get("requires_confirmation"))
            ungrouped.append((_CAP_LABELS.get(name, name.replace("_", " ").title()),
                               is_active, name, needs_confirm))
    if ungrouped:
        result.setdefault("Other", []).extend(ungrouped)

    return result


def _caps_for_group_key(group_key: str) -> list[tuple[str, bool, str, bool]]:
    """Return the capability entries for a specific group key."""
    reg = _load_registry()
    caps_by_id: dict[int, dict] = {int(c["id"]): c for c in reg.get("capabilities", [])}
    cap_ids: list[int] = reg.get("capability_groups", {}).get(group_key, [])

    entries: list[tuple[str, bool, str, bool]] = []
    for cid in cap_ids:
        if cid in caps_by_id:
            cap = caps_by_id[cid]
            name = cap.get("name", "")
            is_active = bool(cap.get("enabled")) and cap.get("status") == "active"
            needs_confirm = bool(cap.get("requires_confirmation"))
            entries.append((_CAP_LABELS.get(name, name.replace("_", " ").title()),
                             is_active, name, needs_confirm))
    return entries


def _resolve_category_topic(text: str) -> Optional[str]:
    """Return the registry group key that best matches the topic in a category query."""
    t = text.lower()
    for keyword, group_key in _CATEGORY_KEYWORDS.items():
        if keyword in t:
            return group_key
    return None


# ---------------------------------------------------------------------------
# Out-of-scope classifier
# ---------------------------------------------------------------------------

def _classify_out_of_scope(text: str) -> str:
    """
    Distinguish between four cases so the response is specific, not generic.
    """
    t = text.lower()

    # Case 1: matches a known "not built yet" category
    for keywords, specific_msg in _NOT_BUILT_CATEGORIES:
        if any(kw in t for kw in keywords):
            return (
                f"{specific_msg}\n\n"
                "Nova only adds new abilities after they've been fully tested and verified — "
                "so you always know exactly what it can and can't do.\n\n"
                'Say "what can you do" to see what\'s ready, '
                'or "what\'s coming next" to see what\'s being worked on.'
            )

    # Case 2: matches a disabled (off) capability in the registry
    reg = _load_registry()
    for cap in reg.get("capabilities", []):
        name = cap.get("name", "").replace("_", " ")
        label = _CAP_LABELS.get(cap.get("name", ""), "").lower()
        if (name in t or label in t) and not (
            bool(cap.get("enabled")) and cap.get("status") == "active"
        ):
            return (
                f"That's actually a Nova capability, but it's turned off right now.\n\n"
                "It's available in the code but not currently active. "
                "A future update may enable it.\n\n"
                'Say "what can you do" to see everything that\'s on right now.'
            )

    # Case 3: matches an active capability that requires confirmation
    for cap in reg.get("capabilities", []):
        name = cap.get("name", "").replace("_", " ")
        label = _CAP_LABELS.get(cap.get("name", ""), "").lower()
        if (name in t or label in t) and bool(cap.get("requires_confirmation")):
            return (
                "I can do that — but I'll need you to confirm before I go ahead.\n\n"
                "Just ask me directly and I'll walk you through it."
            )

    # Case 4: unclear what they're asking
    return (
        "I'm not quite sure what you're asking me to do.\n\n"
        "If you want me to do something specific, just describe it in plain words — "
        "for example: \"check the news\", \"draft an email to my boss\", "
        "\"what's the weather\", or \"open my downloads folder\".\n\n"
        'Say "what can you do" to see the full list.'
    )


# ---------------------------------------------------------------------------
# Response builders
# ---------------------------------------------------------------------------

def _build_identity() -> str:
    return (
        "I'm Nova — a personal AI assistant built to run entirely on your own computer.\n\n"
        "Nova was created by Christopher Daugherty. The idea is simple: "
        "you should have an AI that works for you, not one that sends your data somewhere else "
        "or does things without you knowing.\n\n"
        "What makes Nova different:\n"
        "  - Everything runs on your machine — no cloud, no third-party servers\n"
        "  - Every action is logged so you can always see what happened and why\n"
        "  - Nova only does things it's been specifically built and tested to do\n"
        "  - You stay in control — it asks before anything important happens\n\n"
        "Right now Nova is in an early stage. It can answer questions, search the web, "
        "check the news and weather, draft emails, control parts of your computer, "
        "and remember things you tell it. It's not yet set up for broader actions "
        "like sending messages or managing workflows on its own.\n\n"
        'Say "what can you do" to see the full list, '
        'or just tell me what you need.'
    )


def _build_greeting(*, first_time: bool = False) -> str:
    if first_time:
        return (
            "Hey! I'm Nova — your local AI assistant. "
            "What can I help you with? "
            '(Say "what can you do" if you want to see everything I\'m able to do.)'
        )
    return "Hey! What can I help you with?"


def _build_what_can_you_do() -> str:
    groups = _all_caps_by_group()
    if not groups:
        return (
            "I can help with things like checking the news, drafting emails, "
            "controlling your computer, and more. Just tell me what you need."
        )

    active_total = sum(1 for entries in groups.values() for _, active, _, _ in entries if active)
    inactive_total = sum(1 for entries in groups.values() for _, active, _, _ in entries if not active)

    lines: list[str] = [
        f"Here's everything I can do — {active_total} things are ready to use"
        + (f", {inactive_total} are currently off" if inactive_total else "")
        + ":",
        "",
    ]

    for group_label, entries in groups.items():
        lines.append(f"{group_label}:")
        for cap_label, is_active, cap_name, needs_confirm in entries:
            marker = "[on] " if is_active else "[off]"
            confirm_note = "  (asks for confirmation)" if needs_confirm and is_active else ""
            lines.append(f"  {marker}  {cap_label}{confirm_note}")
        lines.append("")

    lines.append(
        "Just say what you want — no special commands needed.\n"
        'Ask "what can you do with email" or "what can you do for research" '
        'to get a plain-English explanation of any area.'
    )
    return "\n".join(lines).strip()


def _build_category_help(group_key: str, topic_word: str) -> str:
    group_label = _GROUP_LABELS.get(group_key, group_key.replace("_", " ").title())
    entries = _caps_for_group_key(group_key)

    if not entries:
        return (
            f"I don't have anything specifically for \"{topic_word}\" right now.\n\n"
            'Say "what can you do" to see the full list.'
        )

    lines: list[str] = [f"Here's what I can do in the {group_label} area:\n"]
    for cap_label, is_active, cap_name, needs_confirm in entries:
        desc = _CAP_DESCRIPTIONS.get(cap_name, f"({cap_label})")
        if not is_active:
            lines.append(f"  [off]  {cap_label} — not active right now")
        elif needs_confirm:
            lines.append(f"  [on]   {cap_label} — {desc} (I'll ask you to confirm first)")
        else:
            lines.append(f"  [on]   {cap_label} — {desc}")

    lines.append("")
    lines.append("Just say what you want and I'll take care of it.")
    return "\n".join(lines).strip()


def _build_phase_status() -> str:
    return (
        f"Nova is in an early stage right now — {_CURRENT_TIER}.\n\n"
        f"What that means in plain terms: I can answer questions, search the web, "
        f"check news and weather, draft emails, control parts of your computer, "
        f"and remember things you tell me. "
        f"I'm not yet set up for broader actions like sending messages, "
        f"booking things, or managing full workflows on my own.\n\n"
        f"What just shipped: {_CURRENT_STATUS}\n\n"
        f"What's coming next: {_NEXT_UP}"
    )


def _build_whats_planned() -> str:
    return (
        f"Here's where things stand:\n\n"
        f"Right now ({_CURRENT_TIER}): {_CURRENT_STATUS}\n\n"
        f"Coming next: {_NEXT_UP}\n\n"
        f"Further out: {_PLANNED}"
    )


def _build_local_status() -> str:
    return (
        "What works today\n\n"
        "Nova's local baseline is the strongest thing to test first:\n"
        "- Chat and explanation: ask plain-English questions and get local-first guidance.\n"
        "- Dashboard navigation: use Intro, Home, Chat, Trust, Memory, Settings, News, Workspace, Agent, and Rules.\n"
        "- Memory visibility: durable memory is explicit, inspectable, and revocable.\n"
        "- Receipts: the Trust API shows recent governed-action receipts, and the Trust page is the visual review surface.\n"
        "- Safe local actions: system status, response verification, explain-anything, screen help, and some reversible device controls are governed local capabilities.\n"
        "- Email draft boundary: Nova can prepare a local mail-client draft after confirmation, but it does not send email.\n\n"
        "What to try first\n"
        "1. Ask: what does memory do?\n"
        "2. Open Memory and confirm nothing durable is saved unless you explicitly save it.\n"
        "3. Open Trust and inspect receipts.\n"
        "4. Try a safe local action such as system status.\n\n"
        "Budget note: this answer is a local fallback grounded in Nova's runtime truth. "
        "If the daily model budget is exhausted, Nova should still give useful local guidance instead of dead-ending."
    )


def _build_memory_explanation() -> str:
    return (
        "Memory helps Nova keep continuity, but it is not authority.\n\n"
        "In today's local baseline:\n"
        "- Durable memory is saved only when you explicitly save it.\n"
        "- You can inspect, edit, lock, defer, export, or delete memory from the Memory surface.\n"
        "- Conversation context can help Nova understand what you mean during a session.\n"
        "- Neither memory nor conversation context can approve real-world actions.\n\n"
        "Real actions still need the appropriate governed capability, boundary checks, confirmation when required, and receipts when action proof is expected."
    )


def _build_memory_authority_boundary() -> str:
    return (
        "No. Memory cannot authorize actions.\n\n"
        "Nova's rule is: intelligence is not authority. Memory can provide context, preferences, or continuity, but it cannot grant permission to send, delete, buy, write to Shopify, or take any other real action.\n\n"
        "Authority comes from the governed action path: registered capability, current boundary, confirmation when required, visible status, and receipt/proof where expected."
    )


def _build_memory_receipts_difference() -> str:
    return (
        "Memory and receipts do different jobs.\n\n"
        "Memory:\n"
        "- Stores explicit user-approved context for continuity.\n"
        "- Helps Nova remember preferences, project notes, and useful facts.\n"
        "- Is inspectable and revocable.\n"
        "- Does not authorize actions.\n\n"
        "Receipts:\n"
        "- Record what governed actions happened or were blocked.\n"
        "- Help you review effects, failures, boundaries, and next steps.\n"
        "- Are evidence, not permission.\n\n"
        "Short version: memory helps Nova understand; receipts help you audit what Nova did."
    )


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class MetaIntentHandler:
    """
    Matches conversational meta-intents and returns a plain-English response
    with no LLM call. Returns ``None`` if the text doesn't match.

    Pass ``session_state`` to enable context-aware responses (e.g. first-time
    greeting vs. returning user).
    """

    def handle(
        self,
        text: str,
        session_state: Optional[dict] = None,
    ) -> Optional[str]:
        """Return a response string or None."""
        t = text.strip().replace("\u2019", "'").replace("\u2018", "'")
        if not t:
            return None

        turn_count: int = int((session_state or {}).get("turn_count", 1))

        if _GREETING_RE.match(t):
            return _build_greeting(first_time=(turn_count == 0))

        if _IDENTITY_RE.match(t):
            return _build_identity()

        if _LOCAL_STATUS_RE.match(t):
            return _build_local_status()

        if _MEMORY_AUTHORITY_RE.match(t):
            return _build_memory_authority_boundary()

        if _MEMORY_RECEIPTS_RE.match(t):
            return _build_memory_receipts_difference()

        if _MEMORY_EXPLAIN_RE.match(t):
            return _build_memory_explanation()

        # Category help — "what can you do with email" — checked before generic capability
        m = _CATEGORY_HELP_RE.match(t)
        if m:
            topic = (
                m.group("topic") or m.group("topic2") or
                m.group("topic3") or m.group("topic4") or ""
            ).strip()
            group_key = _resolve_category_topic(t)
            if group_key:
                return _build_category_help(group_key, topic)
            # topic word found but no matching group — fall through to generic list

        if _WHAT_CAN_YOU_DO_RE.match(t):
            return _build_what_can_you_do()

        if _PHASE_QUERY_RE.match(t):
            return _build_phase_status()

        if _WHATS_PLANNED_RE.match(t):
            return _build_whats_planned()

        if _OUT_OF_SCOPE_RE.match(t):
            return _classify_out_of_scope(t)

        return None
