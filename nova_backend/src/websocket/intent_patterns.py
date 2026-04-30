# src/websocket/intent_patterns.py
"""
Intent recognition patterns for the Nova brain server session loop.

All regex patterns, command sets, and pure intent-matching helpers live here.
Extracted from brain_server.py to keep the orchestration file focused on
session state and routing rather than pattern definitions.

Nothing in this module touches session state, globals, or network I/O.
"""
from __future__ import annotations

import re

from src.build_phase import PHASE_4_2_ENABLED

# -------------------------------------------------
# Phase 4.2 patterns
# -------------------------------------------------
PHASE42_QUERY_RE = re.compile(
    r"^\s*(?:phase\s*4\.?2|phase42|orthogonal(?:\s+analysis)?)\s*(?:[:\-]\s*|\s+)(?P<query>.+)\s*$",
    re.IGNORECASE,
)
PHASE42_HELP_COMMANDS = {
    "phase42",
    "phase 4.2",
    "orthogonal analysis",
    "phase42 help",
    "orthogonal help",
}

# -------------------------------------------------
# Capability help
# -------------------------------------------------
CAPABILITY_HELP_RE = re.compile(
    r"^\s*(?:"
    r"what can you do"
    r"|nova what can you do"
    r"|tell me what you can do"
    r"|show me what you can do"
    r"|show capabilities"
    r"|show me your capabilities"
    r"|what capabilities do you have"
    r"|what capabilities can you do"
    r"|capabilities"
    r"|help capabilities"
    r"|help"
    r")\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Time query
# -------------------------------------------------
TIME_QUERY_RE = re.compile(
    r"^\s*(?:"
    r"time"
    r"|current time"
    r"|local time"
    r"|time now"
    r"|what(?:'s| is)\s+(?:the\s+)?time"
    r"|what time is it"
    r"|tell me(?:\s+the)?\s+time"
    r")\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Local project patterns
# -------------------------------------------------
LOCAL_PROJECT_CURRENT_RE = re.compile(
    r"^\s*(?P<action>audit|summarize|explain)\s+(?:this\s+)?(?P<kind>repo(?:sitory)?|project|folder)\s*$",
    re.IGNORECASE,
)
LOCAL_PROJECT_TARGET_RE = re.compile(
    r"^\s*(?P<action>audit|summarize)\s+(?P<kind>repo(?:sitory)?|project|folder)\s+(?P<target>.+?)\s*$",
    re.IGNORECASE,
)
LOCAL_PROJECT_DISK_RE = re.compile(
    r"^\s*explain\s+(?P<target>.+?)\s+(?:within|on|from)\s+(?:in\s+)?local\s+disk\s*$",
    re.IGNORECASE,
)
CODEBASE_SUMMARY_CURRENT_RE = re.compile(
    r"^\s*(?P<action>summarize|explain|describe)\s+(?:this\s+)?(?:local\s+)?(?P<kind>repo(?:sitory)?|project|codebase)\s*$",
    re.IGNORECASE,
)
CODEBASE_SUMMARY_TARGET_RE = re.compile(
    r"^\s*(?P<action>summarize|explain|describe)\s+(?P<target>.+?)\s+(?P<kind>repo(?:sitory)?|project|codebase)\s*$",
    re.IGNORECASE,
)
CODEBASE_SUMMARY_TARGET_ONLY_RE = re.compile(
    r"^\s*(?P<action>summarize|describe)\s+(?P<target>.+?)\s*$",
    re.IGNORECASE,
)
CODEBASE_DO_RE = re.compile(
    r"^\s*what\s+does\s+(?:(?P<target>.+?)\s+)?(?P<kind>repo(?:sitory)?|project|codebase)\s+do\s*$",
    re.IGNORECASE,
)
CODEBASE_CAPABILITY_RE = re.compile(
    r"^\s*what\s+can\s+(?P<target>.+?)\s+do\s+based\s+on\s+(?:its|their|the)\s+own\s+code\s*$",
    re.IGNORECASE,
)
LOCAL_ARCHITECTURE_REPORT_RE = re.compile(
    r"^\s*create\s+(?:an?\s+)?(?:analysis\s+)?report\s+on\s+(?P<target>.+?)\s+architecture\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# System status patterns
# -------------------------------------------------
TRUST_CENTER_RE = re.compile(
    r"^\s*(?:show\s+)?trust\s+(?:center|review|status)\s*$",
    re.IGNORECASE,
)
VOICE_CHECK_RE = re.compile(
    r"^\s*(?:(?:voice|speaker|audio)\s+(?:check|test)|test\s+(?:voice|speaker|audio))\s*$",
    re.IGNORECASE,
)
VOICE_STATUS_RE = re.compile(
    r"^\s*(?:(?:voice|audio)\s+status|speaker\s+status)\s*$",
    re.IGNORECASE,
)
BRIDGE_STATUS_RE = re.compile(
    r"^\s*(?:(?:openclaw|remote|bridge)\s+status|bridge\s+status)\s*$",
    re.IGNORECASE,
)
CONNECTION_STATUS_RE = re.compile(
    r"^\s*(?:(?:connection|connections|provider|providers)\s+status|show\s+connections)\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Open / local project navigation
# -------------------------------------------------
OPEN_LOCAL_PROJECT_CURRENT_RE = re.compile(
    r"^\s*open\s+(?:this\s+)?(?P<kind>repo(?:sitory)?|project|folder|directory)\s*$",
    re.IGNORECASE,
)
OPEN_LOCAL_PROJECT_TARGET_RE = re.compile(
    r"^\s*open\s+(?P<kind>repo(?:sitory)?|project|folder|directory)\s+(?P<target>.+?)\s*$",
    re.IGNORECASE,
)
LOCAL_LOCATION_HINT_RE = re.compile(
    r"^\s*(?P<target>.+?)\s+(?:from|within|on|in)\s+(?:the\s+)?"
    r"(?P<location>documents|downloads|desktop|pictures|local\s+disk)"
    r"(?:\s+folder)?\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Thread / workspace patterns
# -------------------------------------------------
CREATE_THREAD_RE = re.compile(
    r"^\s*(?:create|start)\s+(?:project\s+)?thread\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)
CONTINUE_THREAD_RE = re.compile(
    r"^\s*continue(?:\s+my)?\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)
# Paused scopes that must not be intercepted by the thread-continuation router.
# When the extracted thread name matches, let run_general_chat_fallback handle
# the turn so build_request_understanding can inject the PAUSED boundary block.
PAUSED_SCOPE_RE = re.compile(
    r"\b(shopify|cap\s*65|auralis|website\s+merger)\b",
    re.IGNORECASE,
)
SHOW_THREADS_RE = re.compile(
    r"^\s*(?:show|list)\s+(?:my\s+)?(?:project\s+)?threads?\s*$",
    re.IGNORECASE,
)
ATTACH_THREAD_RE = re.compile(
    r"^\s*(?:save|attach)\s+this(?:\s+(?:as\s+part\s+of|to|for))\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)
ATTACH_ACTIVE_THREAD_RE = re.compile(
    r"^\s*(?:save|attach)\s+this\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Memory patterns
# -------------------------------------------------
EXPLICIT_MEMORY_SAVE_RE = re.compile(
    r"^\s*(?P<verb>save|remember)\s+(?P<reference>this|that)(?:\s*[:\-]\s*(?P<body>.+?)\s*)?$",
    re.IGNORECASE,
)
DECISION_THREAD_RE = re.compile(
    r"^\s*(?:remember|record)\s+decision\s+(?P<decision>.+?)\s+for\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Project status / blocker patterns
# -------------------------------------------------
PROJECT_STATUS_RE = re.compile(
    r"^\s*(?:project\s+status|status\s+for|status\s+of)\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)
BIGGEST_BLOCKER_RE = re.compile(
    r"^\s*(?:what(?:'s| is)\s+(?:the\s+)?)?(?:biggest|main|current)\s+blocker(?:\s+in|\s+for)?\s*(?P<name>.*)\s*$",
    re.IGNORECASE,
)
THREAD_DETAIL_RE = re.compile(
    r"^\s*(?:thread\s+detail|show\s+thread\s+detail|show\s+thread|thread\s+snapshot|details?\s+for)\s+(?P<name>.+?)\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Workspace / operational context patterns
# -------------------------------------------------
WORKSPACE_HOME_RE = re.compile(
    r"^\s*(?:show\s+)?(?:workspace|project)\s+home\s*$",
    re.IGNORECASE,
)
WORKSPACE_BOARD_RE = re.compile(
    r"^\s*(?:show\s+)?(?:workspace\s+board|project\s+board|project\s+workspace)\s*$",
    re.IGNORECASE,
)
OPERATIONAL_CONTEXT_RE = re.compile(
    r"^\s*(?:show\s+)?(?:operational\s+context|continuity\s+status|session\s+continuity)\s*$",
    re.IGNORECASE,
)
ASSISTIVE_NOTICES_RE = re.compile(
    r"^\s*(?:show\s+)?(?:assistive\s+notices|assistive\s+status|helpfulness\s+status)\s*$",
    re.IGNORECASE,
)
DISMISS_ASSISTIVE_NOTICE_RE = re.compile(
    r"^\s*dismiss\s+assistive\s+notice\s+(.+?)\s*$",
    re.IGNORECASE,
)
RESOLVE_ASSISTIVE_NOTICE_RE = re.compile(
    r"^\s*resolve\s+assistive\s+notice\s+(.+?)\s*$",
    re.IGNORECASE,
)
RESET_OPERATIONAL_CONTEXT_RE = re.compile(
    r"^\s*(?:reset|clear)\s+(?:operational\s+context|continuity|session\s+continuity)\s*$",
    re.IGNORECASE,
)
MOST_BLOCKED_PROJECT_RE = re.compile(
    r"^\s*(?:which(?:\s+of\s+my)?\s+projects?\s+is\s+most\s+blocked(?:\s+right\s+now)?|most\s+blocked\s+project)\s*$",
    re.IGNORECASE,
)
WHY_RECOMMENDATION_RE = re.compile(
    r"^\s*why\s+(?:this|that)\s+recommendation\s*\??\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Tone patterns
# -------------------------------------------------
TONE_STATUS_COMMANDS = {
    "tone",
    "tone status",
    "tone settings",
    "tone profile",
    "response style",
    "response style settings",
}
TONE_SET_RE = re.compile(r"^\s*tone\s+set\s+(?P<body>.+?)\s*$", re.IGNORECASE)
TONE_RESET_RE = re.compile(r"^\s*tone\s+reset(?:\s+(?P<body>.+?))?\s*$", re.IGNORECASE)

# -------------------------------------------------
# Notification / schedule patterns
# -------------------------------------------------
SHOW_SCHEDULES_COMMANDS = {
    "show schedules",
    "list schedules",
    "notification status",
    "notification schedules",
    "scheduled updates",
    "reminders",
}
NOTIFICATION_SETTINGS_COMMANDS = {
    "notification settings",
    "show notification settings",
    "show schedule settings",
    "schedule settings",
    "notification policy",
}
SCHEDULE_BRIEF_RE = re.compile(
    r"^\s*schedule\s+(?:a\s+)?(?:(?:daily|morning)\s+brief)\s+at\s+(?P<time>.+?)\s*$",
    re.IGNORECASE,
)
REMIND_ME_RE = re.compile(
    r"^\s*remind\s+me(?:\s+(?P<daily>daily))?\s+at\s+(?P<time>.+?)\s+to\s+(?P<body>.+?)\s*$",
    re.IGNORECASE,
)
CANCEL_SCHEDULE_RE = re.compile(
    r"^\s*(?:cancel|delete|remove)\s+schedule\s+(?P<schedule_id>SCH-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
DISMISS_SCHEDULE_RE = re.compile(
    r"^\s*(?:dismiss|clear)\s+schedule\s+(?P<schedule_id>SCH-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
RESCHEDULE_SCHEDULE_RE = re.compile(
    r"^\s*reschedule\s+schedule\s+(?P<schedule_id>SCH-[A-Z0-9\-]+)\s+to\s+(?P<time>.+?)\s*$",
    re.IGNORECASE,
)
SET_QUIET_HOURS_RE = re.compile(
    r"^\s*(?:set\s+)?(?:notification\s+)?quiet\s+hours\s+(?:from\s+)?(?P<start>.+?)\s+(?:to|-)\s+(?P<end>.+?)\s*$",
    re.IGNORECASE,
)
CLEAR_QUIET_HOURS_RE = re.compile(
    r"^\s*(?:clear|disable|turn\s+off)\s+(?:notification\s+)?quiet\s+hours\s*$",
    re.IGNORECASE,
)
SET_NOTIFICATION_RATE_LIMIT_RE = re.compile(
    r"^\s*(?:set\s+)?(?:notification\s+)?rate\s+limit\s+(?P<count>\d{1,2})\s+per\s+hour\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Pattern review patterns
# -------------------------------------------------
PATTERN_STATUS_COMMANDS = {
    "pattern status",
    "patterns status",
    "pattern review status",
    "pattern queue",
}
PATTERN_OPT_IN_RE = re.compile(
    r"^\s*(?:pattern|patterns)\s+opt\s+in\s*$|^\s*enable\s+pattern\s+review\s*$",
    re.IGNORECASE,
)
PATTERN_OPT_OUT_RE = re.compile(
    r"^\s*(?:pattern|patterns)\s+opt\s+out\s*$|^\s*disable\s+pattern\s+review\s*$",
    re.IGNORECASE,
)
PATTERN_REVIEW_RE = re.compile(
    r"^\s*(?:review|show)\s+(?:patterns?|pattern\s+review)(?:\s+for\s+(?P<name>.+?))?\s*$",
    re.IGNORECASE,
)
ACCEPT_PATTERN_RE = re.compile(
    r"^\s*(?:accept|approve|keep)\s+pattern\s+(?P<pattern_id>PAT-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
DISMISS_PATTERN_RE = re.compile(
    r"^\s*(?:dismiss|discard|reject)\s+pattern\s+(?P<pattern_id>PAT-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Policy patterns
# -------------------------------------------------
POLICY_STATUS_COMMANDS = {
    "policy overview",
    "policy status",
    "policy list",
    "policies",
    "policy drafts",
    "policy center",
    "policy review",
}
POLICY_CAPABILITY_MAP_COMMANDS = {
    "capability map",
    "authority map",
    "policy capability map",
    "policy candidates",
    "what can policies run",
    "what policies can run",
    "show capability map",
}
POLICY_CREATE_RE = re.compile(
    r"^\s*policy\s+(?:create|draft)\s+(?P<schedule>daily|weekday)\s+"
    r"(?P<action>calendar\s+snapshot|weather\s+snapshot|news\s+snapshot|system\s+status)\s+at\s+(?P<time>.+?)\s*$",
    re.IGNORECASE,
)
POLICY_SHOW_RE = re.compile(
    r"^\s*policy\s+show\s+(?P<policy_id>POL-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
POLICY_DELETE_RE = re.compile(
    r"^\s*policy\s+delete\s+(?P<policy_id>POL-[A-Z0-9\-]+)(?:\s+(?P<confirm>confirm(?:ed)?))?\s*$",
    re.IGNORECASE,
)
POLICY_SIMULATE_RE = re.compile(
    r"^\s*policy\s+simulate\s+(?P<policy_id>POL-[A-Z0-9\-]+)\s*$",
    re.IGNORECASE,
)
POLICY_RUN_ONCE_RE = re.compile(
    r"^\s*policy\s+run\s+(?P<policy_id>POL-[A-Z0-9\-]+)(?:\s+(?P<once>once))?\s*$",
    re.IGNORECASE,
)

# -------------------------------------------------
# Hard-action / topic heuristics
# -------------------------------------------------
HARD_ACTION_PREFIXES = (
    "open ",
    "volume ",
    "set volume ",
    "brightness ",
    "set brightness ",
    "mute",
    "unmute",
    "play",
    "pause",
    "stop playback",
)
TOPIC_NOISE_TERMS = {
    "please",
    "nova",
    "today",
    "now",
    "quickly",
    "brief",
}


def _is_hard_action_command(text: str) -> bool:
    lowered = (text or "").strip().lower().rstrip(".?!")
    if not lowered:
        return False
    return any(lowered.startswith(prefix) for prefix in HARD_ACTION_PREFIXES)


def _extract_topic_candidate(text: str) -> str:
    lowered = (text or "").strip().lower().rstrip(".?!")
    if not lowered:
        return ""

    for prefix in (
        "research ",
        "search ",
        "summarize ",
        "compare ",
        "track ",
        "open ",
        "explain ",
        "tell me about ",
        "how does ",
        "what is ",
        "what are ",
        "describe ",
    ):
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix):].strip()
            break

    lowered = re.sub(r"\b(the|a|an|about|for)\b", " ", lowered)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    if not lowered:
        return ""

    terms = [term for term in re.findall(r"[a-z0-9']+", lowered) if term and term not in TOPIC_NOISE_TERMS]
    if len(terms) < 2:
        return ""

    candidate = " ".join(terms[:8]).strip()
    return candidate[:80]


# -------------------------------------------------
# Phase 4.2 agent helpers (phase-locked, lazy imports)
# -------------------------------------------------

def _build_phase42_agents() -> list:
    if not PHASE_4_2_ENABLED:
        return []

    from src.agents.builder import BuilderAgent
    from src.agents.deep_audit import DeepAuditAgent
    from src.agents.architect import StructuralArchitectAgent
    from src.agents.memory import MemoryAgent
    from src.agents.assumption import AssumptionRiskAgent
    from src.agents.contradiction import ContradictionAggregatorAgent
    from src.agents.adversarial import AdversarialExternalizerAgent

    return [
        BuilderAgent(),
        DeepAuditAgent(),
        StructuralArchitectAgent(),
        MemoryAgent(),
        AssumptionRiskAgent(),
        ContradictionAggregatorAgent(),
        AdversarialExternalizerAgent(),
    ]


def _extract_phase42_query(text: str) -> str | None:
    match = PHASE42_QUERY_RE.match((text or "").strip())
    if not match:
        return None
    query = (match.group("query") or "").strip()
    return query or None
