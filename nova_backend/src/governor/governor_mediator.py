# src/governor/governor_mediator.py

from __future__ import annotations

import os
import platform
import re
import threading
from time import monotonic
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union

PENDING_CLARIFICATION_TTL_SECONDS = 60.0
MAX_PENDING_CLARIFICATIONS = 10_000
MIN_CLARIFICATION_QUERY_CHARS = 2
MAX_CLARIFICATION_QUERY_CHARS = 500
ENABLED_CAP_CACHE_TTL_SECONDS = 5.0

_pending_clarification: Dict[str, tuple[int, float]] = {}
_enabled_capability_ids_cache: frozenset[int] | None = None
_enabled_capability_ids_cache_at = 0.0
_enabled_capability_ids_cache_profile = ""
_state_lock = threading.RLock()


def _evict_expired_pending_clarifications(now: float | None = None) -> None:
    t = monotonic() if now is None else now
    with _state_lock:
        stale = [
            session_id
            for session_id, (_, created_at) in _pending_clarification.items()
            if t - created_at > PENDING_CLARIFICATION_TTL_SECONDS
        ]
        for session_id in stale:
            _pending_clarification.pop(session_id, None)

        if len(_pending_clarification) <= MAX_PENDING_CLARIFICATIONS:
            return

        overflow = len(_pending_clarification) - MAX_PENDING_CLARIFICATIONS
        oldest = sorted(_pending_clarification.items(), key=lambda item: item[1][1])[:overflow]
        for session_id, _ in oldest:
            _pending_clarification.pop(session_id, None)


def _pop_pending_clarification(session_id: str | None) -> tuple[int, float] | None:
    if not session_id:
        return None
    with _state_lock:
        return _pending_clarification.pop(session_id, None)


def _set_pending_clarification(session_id: str | None, capability_id: int) -> None:
    if not session_id:
        return
    with _state_lock:
        _pending_clarification[session_id] = (capability_id, monotonic())


def _load_enabled_capability_ids() -> frozenset[int]:
    global _enabled_capability_ids_cache
    global _enabled_capability_ids_cache_at
    global _enabled_capability_ids_cache_profile
    now = monotonic()
    current_profile = str(os.getenv("NOVA_RUNTIME_PROFILE") or "").strip() or "default"
    with _state_lock:
        if (
            _enabled_capability_ids_cache is not None
            and (now - _enabled_capability_ids_cache_at) <= ENABLED_CAP_CACHE_TTL_SECONDS
            and _enabled_capability_ids_cache_profile == current_profile
        ):
            return _enabled_capability_ids_cache

    try:
        from src.governor.capability_registry import CapabilityRegistry

        registry = CapabilityRegistry()
    except Exception:
        with _state_lock:
            _enabled_capability_ids_cache = frozenset()
            _enabled_capability_ids_cache_at = now
            _enabled_capability_ids_cache_profile = current_profile
            return _enabled_capability_ids_cache

    enabled_ids = frozenset(
        int(cap.id)
        for cap in registry.all_capabilities()
        if registry.is_enabled(cap.id)
    )
    with _state_lock:
        _enabled_capability_ids_cache = enabled_ids
        _enabled_capability_ids_cache_at = now
        _enabled_capability_ids_cache_profile = current_profile
        return enabled_ids


def _invocation_if_enabled(capability_id: int, params: Dict[str, Any]) -> Invocation | None:
    if capability_id in _load_enabled_capability_ids():
        return Invocation(capability_id=capability_id, params=params)
    return None


def _platform_supports_volume_action(action: str) -> bool:
    command = (action or "").strip().lower()
    system = platform.system()
    if command in {"up", "down", "set"}:
        return system in {"Linux", "Darwin", "Windows"}
    if command in {"mute", "unmute"}:
        return system in {"Linux", "Darwin", "Windows"}
    return False


def _platform_supports_media_action(action: str) -> bool:
    command = (action or "").strip().lower()
    if command not in {"play", "pause", "resume"}:
        return False
    return platform.system() in {"Linux", "Darwin", "Windows"}


def _normalize_spoken_request(text: str) -> str:
    normalized = re.sub(
        r"^\s*(?:hey|hi|okay|ok)[\s,.\-!?:;]*nova\b[\s,.\-!?:;]*",
        "",
        str(text or ""),
        flags=re.IGNORECASE,
    )
    normalized = re.sub(r"^\s*(?:can|could|would|will|do)\s+you\s+", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"^\s*please\s+", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+please\s*$", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\b(\d{1,3})\s*(?:percent|%)\b", r"\1", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized

SEARCH_RE = re.compile(r"^\s*(search(?: for)?|look up)\s+(?P<q>.+?)\s*$", re.IGNORECASE)
SOURCE_RELIABILITY_RE = re.compile(
    r"^\s*analy[sz]e\s+source\s+reliability\s+(?:for|of|on)\s+(?P<q>.+?)\s*$",
    re.IGNORECASE,
)
INTEL_RESEARCH_RE = re.compile(
    r"^\s*(?:research|analy[sz]e|create\s+(?:an?\s+)?intelligence\s+brief(?:\s+(?:on|about))?|intelligence\s+brief\s+(?:on|about)|report)\s+(?P<q>.+?)\s*$",
    re.IGNORECASE,
)
NATURAL_RESEARCH_RE = re.compile(
    r"^\s*(?:what(?:'s| is)\s+going on with|tell me about|help me understand|explain\s+(?!section\b))\s+(?P<q>.+?)\s*$",
    re.IGNORECASE,
)
WHY_RESEARCH_RE = re.compile(
    r"^\s*why\s+(?:is|are)\s+(?P<q>.+?)\s+(?:down|dropping|falling|up|rising)\s*$",
    re.IGNORECASE,
)
CURRENT_INFO_QUESTION_RE = re.compile(
    r"^\s*(?:what|who|when|where|why|how)\b.+\b(?:latest|current|recent|today|news|update|updates|happening|happened|price|forecast|status)\b.*\s*$",
    re.IGNORECASE,
)
LATEST_ON_RE = re.compile(
    r"^\s*(?:give me|show me|tell me)\s+(?:the\s+)?(?:latest|current|recent)(?:\s+updates?)?\s+(?:on|about)\s+(?P<q>.+?)\s*$",
    re.IGNORECASE,
)
QUESTION_PREFIX_RE = re.compile(
    r"^\s*(?:what|who|when|where|why|how|is|are|can|do|does|did|will|would|should|could)\b",
    re.IGNORECASE,
)
OPEN_RE = re.compile(r"^\s*open\s+(?P<name>\w+)\s*$", re.IGNORECASE)
OPEN_WEBSITE_RE = re.compile(
    r"^\s*(?:open|go to|take me to)\s+(?:the\s+)?(?:website|site|webpage)\s+(?P<target>.+?)\s*$",
    re.IGNORECASE,
)
OPEN_NAME_RE = re.compile(r"^\s*open\s+(?P<target>[A-Za-z0-9_.\- ]+)\s*$", re.IGNORECASE)
OPEN_SOURCE_INDEX_RE = re.compile(r"^\s*open\s+(?:source|result)\s+(?P<idx>\d{1,2})\s*$", re.IGNORECASE)
PREVIEW_SOURCE_INDEX_RE = re.compile(r"^\s*preview\s+(?:source|result)\s+(?P<idx>\d{1,2})\s*$", re.IGNORECASE)
PREVIEW_WEBSITE_RE = re.compile(r"^\s*preview\s+(?P<target>[A-Za-z0-9_.\- ]+)\s*$", re.IGNORECASE)
OPEN_FOLDER_RE = re.compile(r"^\s*open\s+(?P<folder>documents|downloads|desktop|pictures)\s*$", re.IGNORECASE)
OPEN_FOLDER_FRIENDLY_RE = re.compile(
    r"^\s*open\s+(?:my\s+)?(?P<folder>documents|downloads|desktop|pictures)(?:\s+folder)?\s*$",
    re.IGNORECASE,
)
OPEN_FILE_RE = re.compile(r"^\s*open\s+(?:file|document)\s+(?P<path>.+?)\s*$", re.IGNORECASE)
SET_VOLUME_RE = re.compile(r"^\s*set\s+volume(?:\s+to)?\s+(?P<level>\d{1,3})\s*$", re.IGNORECASE)
VOLUME_VALUE_RE = re.compile(r"^\s*volume\s+(?P<level>\d{1,3})\s*$", re.IGNORECASE)
SET_BRIGHTNESS_RE = re.compile(r"^\s*set\s+(?:screen\s+)?brightness(?:\s+to)?\s+(?P<level>\d{1,3})\s*$", re.IGNORECASE)
BRIGHTNESS_VALUE_RE = re.compile(r"^\s*brightness\s+(?P<level>\d{1,3})\s*$", re.IGNORECASE)
WEATHER_RE = re.compile(
    r"^\s*(?:weather|weather update|current weather|weather forecast|show me the weather|tell me the weather|how(?:'s| is) the weather(?: in [a-z0-9 ,.\-]+)?(?: today| now| tomorrow)?|what(?:'s| is) (?:the )?weather(?: in [a-z0-9 ,.\-]+)?(?: today| now| tomorrow)?|forecast(?: today| tomorrow)?)\s*$",
    re.IGNORECASE,
)
NEWS_RE = re.compile(
    r"^\s*(?:news|headlines|(?:latest|current|recent|top)\s+headlines|latest news|top news|news update|catch me up on the news|what(?:'s| is) going on in the news|what(?:'s| is) (?:the )?news(?: today| now)?)\s*$",
    re.IGNORECASE,
)
CALENDAR_RE = re.compile(
    r"^\s*(?:calendar|calendar update|agenda|schedule|my calendar|show my calendar|my schedule|show my schedule|what do i have today|what do i have tomorrow|what(?:'s| is) on today|what(?:'s| is) on tomorrow|todays schedule|today's schedule|tomorrows schedule|tomorrow's schedule|todays calendar|today's calendar|tomorrows calendar|tomorrow's calendar|upcoming schedule|upcoming calendar|upcoming events|show upcoming events|coming up|what(?:'s| is) coming up|my upcoming schedule|this week|this week(?:'s)? schedule|this week(?:'s)? calendar|agenda (?:for )?today|agenda (?:for )?tomorrow|what(?:'s| is) on (?:my )?calendar(?: (?:today|tomorrow))?|what(?:'s| is) on (?:my )?schedule(?: (?:today|tomorrow))?)\s*$",
    re.IGNORECASE,
)
SYSTEM_RE = re.compile(
    r"^\s*(?:system|system check|system status|how(?:'s| is) the system doing|how(?:'s| is) nova doing|what(?:'s| is) (?:the )?system status)\s*$",
    re.IGNORECASE,
)
SCREEN_CAPTURE_RE = re.compile(
    r"^\s*(?:take\s+(?:a\s+)?screenshot|capture\s+(?:the\s+)?screen|capture\s+this\s+screen|grab\s+(?:the\s+)?screen)\s*$",
    re.IGNORECASE,
)
SCREEN_ANALYSIS_RE = re.compile(
    r"^\s*(?:analy[sz]e\s+(?:the\s+)?screen|analy[sz]e\s+this\s+screen|explain\s+this\s+screen|help\s+me\s+understand\s+this\s+screen|read\s+this\s+screen)\s*$",
    re.IGNORECASE,
)
EXPLAIN_ANYTHING_RE = re.compile(
    r"^\s*(?:"
    r"what(?:'s| is)\s+(?:this|this\s+error|this\s+page|this\s+chart)"
    r"|what\s+(?:am\s+i|i(?:'m| am))\s+looking\s+at"
    r"|look\s+at\s+this"
    r"|read\s+this\s+page"
    r"|help\s+me\s+understand\s+this"
    r"|explain\s+(?:this|what\s+i\s+am\s+looking\s+at|what\s+i'm\s+looking\s+at|this\s+error|this\s+chart|this\s+page)"
    r"|analy[sz]e\s+this"
    r"|view\s+(?:the\s+|this\s+)?screen"
    r"|which\s+one\s+should\s+i\s+download"
    r")\s*$",
    re.IGNORECASE,
)
EXPLAIN_FOLLOWUP_RE = re.compile(
    r"^\s*(?:"
    r"help\s+me\s+do\s+(?:this|it)"
    r"|walk\s+me\s+through\s+(?:this|it)"
    r"|guide\s+me\s+through\s+(?:this|it)"
    r"|what\s+should\s+i\s+(?:do\s+next|click\s+next)"
    r"|how\s+do\s+i\s+do\s+(?:this|it)"
    r")\s*$",
    re.IGNORECASE,
)
SET_REPORT_RE = re.compile(r"^\s*(report|summarize)\s+(?P<q>.+?)\s*$", re.IGNORECASE)
HEADLINE_SUMMARY_RE = re.compile(
    r"^\s*summarize\s+(?:(?:headline|headlines)\s+)?(?P<sel>all|[\w\s,;&]+)\s*$",
    re.IGNORECASE,
)
SOURCE_NEWS_SUMMARY_RE = re.compile(
    r"^\s*(?:summarize|summary(?:\s+of)?|details?|give me details)\s+(?P<source>.+?)\s+news\s*$",
    re.IGNORECASE,
)
GENERIC_NEWS_SUMMARY_RE = re.compile(
    r"^\s*(?:summarize|summary(?:\s+of)?|details?|give me details)\s+"
    r"(?:(?:the|latest|recent|today'?s|current)\s+)*news"
    r"(?:\s+(?:about|on)\s+(?P<topic>.+?))?\s*$",
    re.IGNORECASE,
)
TOPIC_UPDATES_RE = re.compile(
    r"^\s*(?:search(?:\s+for)?\s+)?(?:most\s+recent\s+updates?|recent\s+updates?|updates?)\s+(?:with|on|about)\s+(?P<topic>.+?)\s*$",
    re.IGNORECASE,
)
INTEL_BRIEF_RE = re.compile(
    r"^\s*(?:daily|intelligence|news)\s+brief\s*$|^\s*give me (?:the )?(?:daily|intelligence)\s+brief\s*$",
    re.IGNORECASE,
)
TODAY_NEWS_RE = re.compile(
    r"^\s*(?:today'?s|todays|latest|recent|current)\s+news\s*$|^\s*news\s+(?:today|updates)\s*$",
    re.IGNORECASE,
)
TOPIC_MAP_RE = re.compile(
    r"^\s*(?:show|open|view)?\s*(?:the\s+)?topic(?:\s+memory)?\s+map\s*$",
    re.IGNORECASE,
)
TRACK_STORY_RE = re.compile(r"^\s*track\s+story\s+(?P<topic>.+?)\s*$", re.IGNORECASE)
FOLLOW_STORY_RE = re.compile(r"^\s*(?:follow|keep\s+following)\s+(?:story\s+)?(?P<topic>.+?)\s*$", re.IGNORECASE)
UPDATE_STORY_RE = re.compile(r"^\s*update\s+story\s+(?P<topic>.+?)\s*$", re.IGNORECASE)
SHOW_STORY_RE = re.compile(r"^\s*show\s+story\s+(?P<topic>.+?)\s*$", re.IGNORECASE)
COMPARE_STORY_RE = re.compile(
    r"^\s*compare\s+story\s+(?P<topic>.+?)\s+last\s+(?P<days>\d{1,3})\s+days\s*$",
    re.IGNORECASE,
)
COMPARE_STORIES_RE = re.compile(
    r"^\s*compare\s+stories\s+(?P<left>.+?)\s+and\s+(?P<right>.+?)\s*$",
    re.IGNORECASE,
)
STOP_TRACKING_RE = re.compile(r"^\s*(?:stop\s+tracking|stop\s+following)\s+(?P<topic>.+?)\s*$", re.IGNORECASE)
UPDATE_TRACKED_STORIES_RE = re.compile(r"^\s*update\s+tracked\s+stories\s*$", re.IGNORECASE)
BRIEF_WITH_TRACKING_RE = re.compile(r"^\s*brief\s+with\s+story\s+tracking\s*$", re.IGNORECASE)
LINK_STORY_RE = re.compile(
    r"^\s*link\s+story\s+(?P<left>.+?)\s+to\s+(?P<right>.+?)\s*$",
    re.IGNORECASE,
)
SHOW_REL_GRAPH_RE = re.compile(
    r"^\s*show\s+(?:story\s+)?relationship\s+graph\s*$",
    re.IGNORECASE,
)
EXPAND_STORY_INDEX_RE = re.compile(
    r"^\s*(?:expand|explain|details?)(?:\s+story)?\s+(?P<idx>\d{1,2})\s*$",
    re.IGNORECASE,
)
COMPARE_STORY_INDEX_RE = re.compile(
    r"^\s*compare(?:\s+story)?\s+(?P<left>\d{1,2})\s+(?:and|vs)\s+(?P<right>\d{1,2})\s*$",
    re.IGNORECASE,
)
COMPARE_HEADLINE_INDEX_RE = re.compile(
    r"^\s*compare\s+headlines?\s+(?P<left>\d{1,2})\s+(?:and|vs)\s+(?P<right>\d{1,2})\s*$",
    re.IGNORECASE,
)
STORY_PAGE_SUMMARY_RE = re.compile(
    r"^\s*(?:summary(?:\s+of)?|summarize|details?|more(?:\s+on)?)\s+"
    r"(?:story|article)\s*#?\s*(?P<idx>\d{1,2})(?:\s+please)?\s*$",
    re.IGNORECASE,
)
STORY_PAGE_SUMMARY_ALT_RE = re.compile(
    r"^\s*(?:story|article)\s*#?\s*(?P<idx>\d{1,2})\s+"
    r"(?:summary|details?|more)(?:\s+please)?\s*$",
    re.IGNORECASE,
)
TRACK_STORY_INDEX_RE = re.compile(
    r"^\s*track\s+story\s+(?P<idx>\d{1,2})\s*$",
    re.IGNORECASE,
)
VERIFY_RE = re.compile(
    r"^\s*(?:verify|double\s+check|fact\s*check|validate(?:\s+sources?)?)"
    r"(?:\s+(?P<text>.+?))?\s*$",
    re.IGNORECASE,
)
SECOND_OPINION_RE = re.compile(
    r"^\s*(?:second\s+opinion|deepseek\s+second\s+opinion|review\s+this\s+answer|pressure\s*check)"
    r"(?:\s+(?P<text>.+?))?\s*$",
    re.IGNORECASE,
)
DOC_CREATE_RE = re.compile(
    r"^\s*(?:write|create|generate|make)\s+(?:a\s+)?(?:detailed\s+)?(?:analysis(?:\s+report)?|report|document|write[- ]?up)\s+(?:on|about)\s+(?P<topic>.+?)\s*$",
    re.IGNORECASE,
)
DOC_SUMMARIZE_RE = re.compile(
    r"^\s*(?:summarize|sum\s+up)\s+doc(?:ument)?\s+(?P<doc_id>\d+)\s*$",
    re.IGNORECASE,
)
DOC_EXPLAIN_SECTION_RE = re.compile(
    r"^\s*(?:explain|walk\s+me\s+through)\s+section\s+(?P<section>\d+)(?:\s+of\s+doc(?:ument)?\s+(?P<doc_id>\d+))?\s*$",
    re.IGNORECASE,
)
DOC_LIST_RE = re.compile(
    r"^\s*(?:"
    r"(?:list|show)\s+(?:my\s+)?(?:(?:analysis\s+)?docs?(?:uments)?|analysis\s+reports?)"
    r"|open\s+(?:my\s+)?(?:analysis\s+docs?(?:uments)?|analysis\s+reports?)"
    r")\s*$",
    re.IGNORECASE,
)
MEMORY_SAVE_FRIENDLY_RE = re.compile(
    r"^\s*(?:remember|save)\s+this(?:\s+in\s+memory)?\s*:\s*(?P<body>.+?)\s*$",
    re.IGNORECASE,
)
MEMORY_SAVE_RE = re.compile(
    r"^\s*memory\s+save\s+(?P<title>[^:]{1,120})\s*:\s*(?P<body>.+?)\s*$",
    re.IGNORECASE,
)
MEMORY_SAVE_THREAD_SNAPSHOT_RE = re.compile(
    r"^\s*memory\s+save\s+thread\s+(?P<thread_name>.+?)\s*$",
    re.IGNORECASE,
)
MEMORY_SAVE_THREAD_DECISION_RE = re.compile(
    r"^\s*memory\s+save\s+decision\s+for\s+(?P<thread_name>[^:]{1,120})\s*:\s*(?P<decision>.+?)\s*$",
    re.IGNORECASE,
)
MEMORY_LIST_THREAD_RE = re.compile(
    r"^\s*memory\s+list\s+thread\s+(?P<thread_name>.+?)\s*$",
    re.IGNORECASE,
)
MEMORY_OVERVIEW_RE = re.compile(
    r"^\s*memory\s+(?:overview|status|review)\s*$",
    re.IGNORECASE,
)
MEMORY_LIST_RE = re.compile(
    r"^\s*memory\s+list(?:\s+(?P<tier>locked|active|deferred))?\s*$",
    re.IGNORECASE,
)
MEMORY_LIST_FRIENDLY_RE = re.compile(
    r"^\s*(?:show|list)\s+(?:me\s+)?(?:my\s+|saved\s+)?memories\s*$|^\s*what\s+have\s+you\s+saved\s*$",
    re.IGNORECASE,
)
MEMORY_RECENT_RE = re.compile(
    r"^\s*(?:recent\s+memories|recent\s+memory|memory\s+recent)\s*$",
    re.IGNORECASE,
)
MEMORY_SEARCH_RE = re.compile(
    r"^\s*(?:memory\s+search|search\s+(?:my\s+)?memories?\s+for|find\s+(?:my\s+)?memories?\s+for|find\s+in\s+(?:my\s+)?memory)\s+(?P<query>.+?)\s*$",
    re.IGNORECASE,
)
MEMORY_RECALL_FRIENDLY_RE = re.compile(
    r"^\s*(?:what\s+do\s+you\s+remember|show\s+what\s+you\s+remember|what(?:'s| is)\s+in\s+(?:my\s+)?memory)\s*$",
    re.IGNORECASE,
)
MEMORY_SHOW_FRIENDLY_RE = re.compile(
    r"^\s*(?:show|open)\s+(?:that|last|recent)\s+memory\s*$",
    re.IGNORECASE,
)
MEMORY_EXPORT_RE = re.compile(
    r"^\s*(?:memory\s+export|export\s+(?:my\s+)?memory|download\s+(?:my\s+)?memory)\s*$",
    re.IGNORECASE,
)
MEMORY_SHOW_RE = re.compile(
    r"^\s*memory\s+show\s+(?P<item_id>[A-Za-z0-9\-_]+)\s*$",
    re.IGNORECASE,
)
MEMORY_LOCK_RE = re.compile(
    r"^\s*memory\s+lock\s+(?P<item_id>[A-Za-z0-9\-_]+)\s*$",
    re.IGNORECASE,
)
MEMORY_DEFER_RE = re.compile(
    r"^\s*memory\s+defer\s+(?P<item_id>[A-Za-z0-9\-_]+)\s*$",
    re.IGNORECASE,
)
MEMORY_UNLOCK_RE = re.compile(
    r"^\s*memory\s+unlock\s+(?P<item_id>[A-Za-z0-9\-_]+)(?:\s+(?P<confirm>confirm(?:ed)?))?\s*$",
    re.IGNORECASE,
)
MEMORY_DELETE_RE = re.compile(
    r"^\s*memory\s+delete\s+(?P<item_id>[A-Za-z0-9\-_]+)(?:\s+(?P<confirm>confirm(?:ed)?))?\s*$",
    re.IGNORECASE,
)
MEMORY_DELETE_FRIENDLY_RE = re.compile(
    r"^\s*(?:delete|remove)\s+(?:(?:that|last|recent)\s+memory|memory\s+(?P<item_id>[A-Za-z0-9\-_]+))(?:\s+(?P<confirm>confirm(?:ed)?))?\s*$",
    re.IGNORECASE,
)
MEMORY_FORGET_THIS_RE = re.compile(
    r"^\s*forget\s+(?P<item_ref>this|that|last|recent)(?:\s+memory)?(?:\s+(?P<confirm>confirm(?:ed)?))?\s*$",
    re.IGNORECASE,
)
MEMORY_SUPERSEDE_RE = re.compile(
    r"^\s*memory\s+supersede\s+(?P<item_id>[A-Za-z0-9\-_]+)\s+with\s+(?P<title>[^:]{1,120})\s*:\s*(?P<body>.+?)"
    r"(?:\s+(?P<confirm>confirm(?:ed)?))?\s*$",
    re.IGNORECASE,
)
MEMORY_EDIT_RE = re.compile(
    r"^\s*(?:edit|update)\s+(?:(?:that|last|recent)\s+memory|memory\s+(?P<item_id>[A-Za-z0-9\-_]+))\s*:\s*(?P<body>.+?)(?:\s+(?P<confirm>confirm(?:ed)?))?\s*$",
    re.IGNORECASE,
)
COMMAND_ONLY_RE = re.compile(
    r"^\s*(?P<verb>open|search|research|summarize|compare|track|memory)\s*$",
    re.IGNORECASE,
)
RUN_TEMPLATE_RE = re.compile(
    r"^\s*(?:run|execute|start|trigger)\s+(?:home[\s\-]?agent\s+)?(?:template\s+)?(?P<template_id>[A-Za-z0-9_\-]{1,64})\s*$",
    re.IGNORECASE,
)
MORNING_BRIEF_RE = re.compile(
    r"^\s*(?:run|give me|show me|start)?\s*(?:the\s+)?morning\s+brief(?:\s+template)?\s*$",
    re.IGNORECASE,
)
SHOPIFY_REPORT_RE = re.compile(
    r"^\s*(?:shopify\s+(?:report|stats|status|intelligence|summary|snapshot|brief|overview|store)"
    r"|(?:store|shop)\s+(?:report|stats|status|intelligence|summary|snapshot)"
    r"|(?:show|get|fetch|pull)\s+(?:my\s+)?shopify\s+(?:data|metrics|orders?|products?|store)"
    r"|how(?:'s|\s+is)\s+(?:my\s+)?(?:shopify\s+)?store\s+doing"
    r")\b.*$",
    re.IGNORECASE,
)
SEND_EMAIL_DRAFT_RE = re.compile(
    # verb + "email/e-mail"
    r"^\s*(?:draft|compose|write|prepare)\s+(?:me\s+)?(?:an?\s+)?e?-?mail\b"
    # optional "to <recipient>" — stops before keyword prepositions via negative lookahead
    r"(?:\s+to\s+(?P<to>[^\s]+(?:\s+(?!(?:about|regarding|re:|with\s+subject|subject)\b)[^\s]+)*))?"
    # optional "about / regarding / subject: <topic>"
    r"(?:\s+(?:about|regarding|re:|with\s+subject|subject[:\s]+)\s+(?P<subject>.+?))?\s*$",
    re.IGNORECASE,
)
EMAIL_SHORTHAND_RE = re.compile(
    r"^\s*email\s+(?P<to>[A-Za-z0-9._%+\-@][\w._%+\-@]*)(?:\s+about\s+(?P<subject>.+?))?\s*$",
    re.IGNORECASE,
)

_NUMBER_WORDS = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
}

TIME_SENSITIVITY_TERMS = (
    "latest",
    "current",
    "recent",
    "today",
    "now",
    "update",
    "updates",
    "as of",
    "this week",
    "this month",
    "this year",
)

FINANCE_TERMS = (
    "stock",
    "stocks",
    "share",
    "shares",
    "price",
    "quote",
    "market",
    "markets",
    "crypto",
    "bitcoin",
    "ethereum",
    "dogecoin",
    "solana",
    "nasdaq",
    "dow",
    "s&p",
    "earnings",
    "inflation",
    "cpi",
    "fed",
    "interest rate",
    "rate cut",
    "bond yield",
    "oil price",
    "gold price",
)

LEGAL_POLICY_TERMS = (
    "legal",
    "illegal",
    "law",
    "laws",
    "regulation",
    "regulations",
    "regulated",
    "policy",
    "bill",
    "act",
    "compliance",
    "court",
    "ruling",
    "supreme court",
    "statute",
    "tax rule",
    "license",
    "permit",
    "ban",
    "banned",
    "allowed",
)

LOCATION_HINT_RE = re.compile(r"\b(?:in|for|under)\s+[a-z][a-z\s]{2,}\b", re.IGNORECASE)

NEWS_CATEGORY_ALIASES: dict[str, set[str]] = {
    "global": {"global", "world", "international"},
    "politics": {
        "politics",
        "politics news",
        "political",
        "political news",
        "policy",
        "government",
        "politics left",
        "politics center",
        "politics right",
        "left politics",
        "center politics",
        "right politics",
        "progressive politics",
        "conservative politics",
        "centrist politics",
        "institutional politics",
    },
    "local": {"local", "local news", "national", "u.s.", "us news", "us"},
    "tech": {"tech", "technology", "ai"},
    "crypto": {"crypto", "crypto news", "markets", "market", "stocks", "stock", "business", "finance"},
}


def _normalize_number_words(text: str) -> str:
    out = text
    for word, digit in _NUMBER_WORDS.items():
        out = re.sub(rf"\b{word}\b", digit, out, flags=re.IGNORECASE)
    return out


def _looks_like_time_sensitive_finance_or_policy_query(text: str) -> bool:
    raw = (text or "").strip()
    if not raw:
        return False
    lowered = raw.lower()
    if not QUESTION_PREFIX_RE.match(lowered):
        return False

    has_time_marker = any(term in lowered for term in TIME_SENSITIVITY_TERMS) or bool(
        re.search(r"\b20\d{2}\b", lowered)
    )
    has_finance_term = any(term in lowered for term in FINANCE_TERMS)
    has_policy_term = any(term in lowered for term in LEGAL_POLICY_TERMS)

    if has_finance_term and (has_time_marker or "price" in lowered or "stock" in lowered):
        return True
    if has_policy_term and (has_time_marker or bool(LOCATION_HINT_RE.search(lowered))):
        return True
    return False


def _parse_headline_selection(selection_text: str) -> dict[str, Any] | None:
    raw = _normalize_number_words(selection_text or "")
    if not raw:
        return None
    cleaned = re.sub(r"\band\b|&|;", ",", raw, flags=re.IGNORECASE)
    tokens = [token.strip() for token in cleaned.split(",") if token.strip()]

    if len(tokens) == 1 and tokens[0].isdigit():
        return {"selection": "indices", "indices": [int(tokens[0])]}

    indices: list[int] = []
    for token in tokens:
        if not token:
            continue
        match = re.search(r"\b(\d{1,2})\b", token)
        if not match:
            continue
        value = int(match.group(1))
        if value not in indices:
            indices.append(value)

    if not indices:
        return None

    return {"selection": "indices", "indices": indices}


def _normalize_source_query(source_query: str) -> str:
    normalized = re.sub(r"\s+", " ", (source_query or "").strip())
    # Convert spaced acronyms such as "A B C" -> "ABC".
    if re.fullmatch(r"(?:[A-Za-z]\s+){1,}[A-Za-z]", normalized):
        normalized = normalized.replace(" ", "")
    return normalized


def _strip_news_summary_fillers(text: str) -> str:
    cleaned = (text or "").strip().lower()
    cleaned = re.sub(r"\b(?:category|categories|news|headlines?)\b", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _match_news_category(text: str) -> str | None:
    cleaned = _strip_news_summary_fillers(text)
    if not cleaned:
        return None

    for key, aliases in NEWS_CATEGORY_ALIASES.items():
        if cleaned == key or cleaned in aliases:
            return key

    for key, aliases in NEWS_CATEGORY_ALIASES.items():
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias)}\b", cleaned):
                return key
    return None


def _normalize_web_target(target_text: str) -> str:
    target = re.sub(r"\b(?:website|site|webpage|homepage)\b", "", (target_text or ""), flags=re.IGNORECASE)
    target = re.sub(r"\s+", " ", target).strip()
    target = re.sub(
        r"\b(?:[A-Za-z]\s+){1,}[A-Za-z]\b",
        lambda m: re.sub(r"\s+", "", m.group(0)),
        target,
    )
    target = re.sub(r"\b(abc|fox)\s+new\b", r"\1 news", target, flags=re.IGNORECASE)
    return target


def _looks_like_local_path(target: str) -> bool:
    t = (target or "").strip()
    return bool(
        re.search(r"[\\/]", t)
        or re.match(r"^[A-Za-z]:", t)
        or re.search(r"[-_]", t)
    )


def _looks_like_web_target(raw_target: str, normalized_target: str) -> bool:
    source = (raw_target or "").strip()
    target = (normalized_target or "").strip().lower()
    if "." in target:
        return True
    if re.search(r"\b(?:news|website|site|webpage)\b", source, re.IGNORECASE):
        return True
    web_aliases = {
        "google",
        "github",
        "youtube",
        "facebook",
        "twitter",
        "cnn",
        "bbc",
        "reuters",
        "npr",
        "ap",
        "abc",
        "fox",
        "pandora",
    }
    return any(token in web_aliases for token in target.split())


@dataclass(frozen=True)
class Invocation:
    capability_id: int
    params: Dict[str, Any]


@dataclass(frozen=True)
class Clarification:
    capability_id: int
    message: str


class GovernorMediator:
    @staticmethod
    def mediate(text: str) -> str:
        if not text or not text.strip():
            return "I'm not sure right now."
        return text.strip()

    @staticmethod
    def parse_governed_invocation(text: str, session_id: Optional[str] = None) -> Union[Invocation, Clarification, None]:
        t = (text or "").strip()
        preserve_terminal_punctuation = bool(
            re.match(r"^\s*(?:remember|save)\s+(?:this|that)\s*[:\-]", t, re.IGNORECASE)
            or re.match(
                r"^\s*(?:edit|update)\s+(?:(?:that|last|recent)\s+memory|memory\s+[A-Za-z0-9\-_]+)\s*:",
                t,
                re.IGNORECASE,
            )
            or re.match(r"^\s*memory\s+(?:save|supersede)\b.*:\s*.+$", t, re.IGNORECASE)
        )
        if not preserve_terminal_punctuation:
            t = re.sub(r"[.?!]+$", "", t)
        t = _normalize_spoken_request(t)
        if not t:
               return None

        _evict_expired_pending_clarifications()

        pending = _pop_pending_clarification(session_id)
        if pending is not None:
            cap_id, _created_at = pending
            if cap_id == 16:
                alt = GovernorMediator.parse_governed_invocation(t, session_id=None)
                if isinstance(alt, Invocation) and alt.capability_id != 16:
                    return alt
                if isinstance(alt, Clarification):
                    return alt
                if "\n" in t or len(t) < MIN_CLARIFICATION_QUERY_CHARS or len(t) > MAX_CLARIFICATION_QUERY_CHARS:
                    return Clarification(
                        capability_id=16,
                        message=(
                            "Please provide a short search query (2-500 characters) on a single line."
                        ),
                    )
                return _invocation_if_enabled(16, {"query": t})
            return None

        if WEATHER_RE.match(t):
            return _invocation_if_enabled(55, {})

        if NEWS_RE.match(t):
            return _invocation_if_enabled(56, {})

        if CALENDAR_RE.match(t):
            return _invocation_if_enabled(57, {})

        if SYSTEM_RE.match(t):
            return _invocation_if_enabled(32, {})

        if SCREEN_CAPTURE_RE.match(t):
            return _invocation_if_enabled(58, {"invocation_source": "text"})

        if SCREEN_ANALYSIS_RE.match(t):
            return _invocation_if_enabled(
                59,
                {
                    "invocation_source": "text",
                    "query": t.strip(),
                },
            )

        if EXPLAIN_ANYTHING_RE.match(t):
            return _invocation_if_enabled(
                60,
                {
                    "invocation_source": "text",
                    "query": t.strip(),
                },
            )

        if EXPLAIN_FOLLOWUP_RE.match(t):
            return _invocation_if_enabled(
                60,
                {
                    "invocation_source": "text",
                    "query": t.strip(),
                    "followup": True,
                },
            )

        tm = TOPIC_UPDATES_RE.match(t)
        if tm:
            topic_query = (tm.group("topic") or "").strip()
            if topic_query:
                return _invocation_if_enabled(49, {"selection": "topic", "topic_query": topic_query, "recent": True})

        m = SOURCE_RELIABILITY_RE.match(t)
        if m:
            return _invocation_if_enabled(
                48,
                {
                    "query": m.group("q").strip(),
                    "analysis_focus": "source_reliability",
                },
            )

        m = INTEL_RESEARCH_RE.match(t)
        if m:
            return _invocation_if_enabled(48, {"query": m.group("q").strip()})

        m = NATURAL_RESEARCH_RE.match(t)
        if m:
            return _invocation_if_enabled(48, {"query": m.group("q").strip()})

        m = WHY_RESEARCH_RE.match(t)
        if m:
            return _invocation_if_enabled(48, {"query": f"why {m.group('q').strip()} is changing"})

        m = LATEST_ON_RE.match(t)
        if m:
            return _invocation_if_enabled(48, {"query": m.group("q").strip()})

        if CURRENT_INFO_QUESTION_RE.match(t):
            return _invocation_if_enabled(48, {"query": t.strip()})
        if _looks_like_time_sensitive_finance_or_policy_query(t):
            return _invocation_if_enabled(48, {"query": t.strip()})

        m = SEARCH_RE.match(t)
        if m:
            search_query = m.group("q").strip()
            lowered_query = search_query.lower()
            if lowered_query.startswith(("memories for ", "memory for ", "memory ", "memories ")):
                memory_query = re.sub(r"^(?:my\s+)?memories?\s+for\s+", "", search_query, flags=re.IGNORECASE)
                memory_query = re.sub(r"^(?:my\s+)?memories?\s+", "", memory_query, flags=re.IGNORECASE)
                memory_query = re.sub(r"^memory\s+", "", memory_query, flags=re.IGNORECASE).strip()
                if memory_query:
                    return _invocation_if_enabled(61, {"action": "search", "query": memory_query})
            return _invocation_if_enabled(16, {"query": search_query})

        if DOC_LIST_RE.match(t):
            return _invocation_if_enabled(54, {"action": "list"})

        m = OPEN_FOLDER_RE.match(t) or OPEN_FOLDER_FRIENDLY_RE.match(t)
        if m:
            return _invocation_if_enabled(22, {"target": m.group("folder").strip().lower()})

        m = OPEN_FILE_RE.match(t)
        if m:
            return _invocation_if_enabled(22, {"path": m.group("path").strip()})

        m = OPEN_SOURCE_INDEX_RE.match(t)
        if m:
            return _invocation_if_enabled(17, {"source_index": int(m.group("idx"))})

        m = PREVIEW_SOURCE_INDEX_RE.match(t)
        if m:
            return _invocation_if_enabled(17, {"source_index": int(m.group("idx")), "preview": True})

        m = OPEN_WEBSITE_RE.match(t)
        if m:
            target = _normalize_web_target(m.group("target"))
            if target:
                return _invocation_if_enabled(17, {"target": target.lower()})

        m = OPEN_RE.match(t)
        if m:
            return _invocation_if_enabled(17, {"target": m.group("name").strip().lower()})

        m = PREVIEW_WEBSITE_RE.match(t)
        if m:
            target = _normalize_web_target(m.group("target"))
            if target:
                return _invocation_if_enabled(17, {"target": target.lower(), "preview": True})

        m = OPEN_NAME_RE.match(t)
        if m:
            raw_target = m.group("target")
            target = _normalize_web_target(raw_target)
            if len(target.split()) == 1 and len(target) <= 2:
                return Clarification(
                    capability_id=17,
                    message=(
                        f"I might have misheard '{target}'. "
                        "Please say the full website or file name."
                    ),
                )
            # Keep single-token website shorthand behavior (e.g., "open github").
            if re.fullmatch(r"[A-Za-z0-9_]+", target):
                return _invocation_if_enabled(17, {"target": target.lower()})
            if _looks_like_web_target(raw_target, target):
                return _invocation_if_enabled(17, {"target": target.lower()})
            if _looks_like_local_path(target):
                return _invocation_if_enabled(22, {"path": target})
            return Clarification(
                capability_id=17,
                message=(
                    f"I want to confirm: did you mean a website or a local file for '{target}'? "
                    f"Say 'open website {target}' or 'open file {target}'."
                ),
            )

        if re.match(r"^\s*(speak that|read that|say it|read this out loud|say this out loud|read that to me)\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(18, {})

        if re.match(r"^\s*(?:volume\s+up|turn(?: the)? volume up|make it louder|make the volume louder)\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(19, {"action": "up"})
        if re.match(r"^\s*(?:volume\s+down|turn(?: the)? volume down|make it quieter|make the volume quieter|make it softer)\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(19, {"action": "down"})
        if re.match(r"^\s*(?:mute|mute volume|volume mute)\s*$", t, re.IGNORECASE):
            if not _platform_supports_volume_action("mute"):
                return Clarification(
                    capability_id=19,
                    message=(
                        "Explicit mute is not available on this device yet. "
                        "Try volume up, volume down, or set volume to a level."
                    ),
                )
            return _invocation_if_enabled(19, {"action": "mute"})
        if re.match(r"^\s*(?:unmute|unmute volume|volume unmute)\s*$", t, re.IGNORECASE):
            if not _platform_supports_volume_action("unmute"):
                return Clarification(
                    capability_id=19,
                    message=(
                        "Explicit unmute is not available on this device yet. "
                        "Try volume up, volume down, or set volume to a level."
                    ),
                )
            return _invocation_if_enabled(19, {"action": "unmute"})

        m = SET_VOLUME_RE.match(t)
        if m:
            return _invocation_if_enabled(19, {"action": "set", "level": int(m.group("level"))})
        m = VOLUME_VALUE_RE.match(t)
        if m:
            return _invocation_if_enabled(19, {"action": "set", "level": int(m.group("level"))})

        if re.match(r"^\s*(?:brightness\s+up|turn(?: the)? brightness up|make(?: the screen)? brighter)\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(21, {"action": "up"})
        if re.match(r"^\s*(?:brightness\s+down|turn(?: the)? brightness down|make(?: the screen)? dimmer)\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(21, {"action": "down"})
        if re.match(r"^\s*(?:increase|raise)\s+brightness\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(21, {"action": "up"})
        if re.match(r"^\s*(?:decrease|lower|dim)\s+brightness\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(21, {"action": "down"})

        m = SET_BRIGHTNESS_RE.match(t)
        if m:
            return _invocation_if_enabled(21, {"action": "set", "level": int(m.group("level"))})
        m = BRIGHTNESS_VALUE_RE.match(t)
        if m:
            return _invocation_if_enabled(21, {"action": "set", "level": int(m.group("level"))})

        if re.match(r"^\s*(play|pause|resume)\s*$", t, re.IGNORECASE):
            if not _platform_supports_media_action(t.lower()):
                return Clarification(
                    capability_id=20,
                    message="Explicit play, pause, and resume are not available on this device yet.",
                )
            return _invocation_if_enabled(20, {"action": t.lower()})

        if INTEL_BRIEF_RE.match(t):
            return _invocation_if_enabled(50, {})

        if TODAY_NEWS_RE.match(t):
            return _invocation_if_enabled(50, {"read_sources": True})

        m = EXPAND_STORY_INDEX_RE.match(t)
        if m:
            return _invocation_if_enabled(50, {"action": "expand_cluster", "story_id": int(m.group("idx"))})

        m = COMPARE_HEADLINE_INDEX_RE.match(t)
        if m:
            return _invocation_if_enabled(
                49,
                {
                    "action": "compare_indices",
                    "left_index": int(m.group("left")),
                    "right_index": int(m.group("right")),
                },
            )

        m = STORY_PAGE_SUMMARY_RE.match(t) or STORY_PAGE_SUMMARY_ALT_RE.match(t)
        if m:
            return _invocation_if_enabled(
                49,
                {
                    "action": "story_page_summary",
                    "story_index": int(m.group("idx")),
                },
            )

        m = COMPARE_STORY_INDEX_RE.match(t)
        if m:
            return _invocation_if_enabled(
                50,
                {"action": "compare_clusters", "left_story_id": int(m.group("left")), "right_story_id": int(m.group("right"))},
            )

        m = TRACK_STORY_INDEX_RE.match(t)
        if m:
            return _invocation_if_enabled(50, {"action": "track_cluster", "story_id": int(m.group("idx"))})

        if TOPIC_MAP_RE.match(t):
            return _invocation_if_enabled(51, {})

        m = TRACK_STORY_RE.match(t)
        if m:
            return _invocation_if_enabled(52, {"action": "track", "topic": m.group("topic").strip()})

        m = FOLLOW_STORY_RE.match(t)
        if m:
            return _invocation_if_enabled(52, {"action": "track", "topic": m.group("topic").strip()})

        m = UPDATE_STORY_RE.match(t)
        if m:
            return _invocation_if_enabled(52, {"action": "update", "topic": m.group("topic").strip()})

        if UPDATE_TRACKED_STORIES_RE.match(t):
            return _invocation_if_enabled(52, {"action": "update_all"})

        if BRIEF_WITH_TRACKING_RE.match(t):
            return _invocation_if_enabled(52, {"action": "brief_with_tracking"})

        m = LINK_STORY_RE.match(t)
        if m:
            return _invocation_if_enabled(
                52,
                {"action": "link", "topics": [m.group("left").strip(), m.group("right").strip()]},
            )

        m = STOP_TRACKING_RE.match(t)
        if m:
            return _invocation_if_enabled(52, {"action": "stop", "topic": m.group("topic").strip()})

        if SHOW_REL_GRAPH_RE.match(t):
            return _invocation_if_enabled(53, {"action": "show_graph"})

        som = SECOND_OPINION_RE.match(t)
        if som:
            candidate = (som.group("text") or "").strip()
            if candidate.lower() in {"this", "that", "it"}:
                candidate = ""
            return _invocation_if_enabled(62, {"text": candidate})

        vm = VERIFY_RE.match(t)
        if vm:
            candidate = (vm.group("text") or "").strip()
            if candidate.lower() in {"this", "that", "it"}:
                candidate = ""
            return _invocation_if_enabled(31, {"text": candidate})

        m = DOC_CREATE_RE.match(t)
        if m:
            return _invocation_if_enabled(54, {"action": "create", "topic": m.group("topic").strip()})

        m = DOC_SUMMARIZE_RE.match(t)
        if m:
            return _invocation_if_enabled(54, {"action": "summarize_doc", "doc_id": int(m.group("doc_id"))})

        m = DOC_EXPLAIN_SECTION_RE.match(t)
        if m:
            params: Dict[str, Any] = {"action": "explain_section", "section_number": int(m.group("section"))}
            if m.group("doc_id"):
                params["doc_id"] = int(m.group("doc_id"))
            return _invocation_if_enabled(54, params)

        if DOC_LIST_RE.match(t):
            return _invocation_if_enabled(54, {"action": "list"})

        m = MEMORY_SAVE_THREAD_DECISION_RE.match(t)
        if m:
            return _invocation_if_enabled(
                61,
                {
                    "action": "save_thread_decision",
                    "thread_name": m.group("thread_name").strip(),
                    "decision": m.group("decision").strip(),
                },
            )

        m = MEMORY_SAVE_THREAD_SNAPSHOT_RE.match(t)
        if m:
            return _invocation_if_enabled(
                61,
                {
                    "action": "save_thread_snapshot",
                    "thread_name": m.group("thread_name").strip(),
                },
            )

        m = MEMORY_LIST_THREAD_RE.match(t)
        if m:
            return _invocation_if_enabled(
                61,
                {
                    "action": "list",
                    "thread_name": m.group("thread_name").strip(),
                },
            )

        if MEMORY_OVERVIEW_RE.match(t):
            return _invocation_if_enabled(61, {"action": "overview"})

        m = MEMORY_SAVE_FRIENDLY_RE.match(t)
        if m:
            body = m.group("body").strip()
            title = body.split(":")[0].strip()[:80] or "Saved memory"
            return _invocation_if_enabled(
                61,
                {
                    "action": "save",
                    "title": title,
                    "body": body,
                },
            )

        m = MEMORY_SAVE_RE.match(t)
        if m:
            return _invocation_if_enabled(
                61,
                {
                    "action": "save",
                    "title": m.group("title").strip(),
                    "body": m.group("body").strip(),
                },
            )

        m = MEMORY_LIST_RE.match(t)
        if m:
            params: Dict[str, Any] = {"action": "list"}
            tier = (m.group("tier") or "").strip().lower()
            if tier:
                params["tier"] = tier
            return _invocation_if_enabled(61, params)

        if MEMORY_LIST_FRIENDLY_RE.match(t):
            return _invocation_if_enabled(61, {"action": "list"})

        if MEMORY_RECENT_RE.match(t):
            return _invocation_if_enabled(61, {"action": "recent"})

        m = MEMORY_SEARCH_RE.match(t)
        if m:
            return _invocation_if_enabled(61, {"action": "search", "query": m.group("query").strip()})

        if MEMORY_RECALL_FRIENDLY_RE.match(t):
            return _invocation_if_enabled(61, {"action": "overview"})

        if MEMORY_SHOW_FRIENDLY_RE.match(t):
            return _invocation_if_enabled(61, {"action": "show", "item_id": "last"})

        if MEMORY_EXPORT_RE.match(t):
            return _invocation_if_enabled(61, {"action": "export"})

        m = MEMORY_SHOW_RE.match(t)
        if m:
            return _invocation_if_enabled(61, {"action": "show", "item_id": m.group("item_id").strip()})

        m = MEMORY_LOCK_RE.match(t)
        if m:
            return _invocation_if_enabled(61, {"action": "lock", "item_id": m.group("item_id").strip()})

        m = MEMORY_DEFER_RE.match(t)
        if m:
            return _invocation_if_enabled(61, {"action": "defer", "item_id": m.group("item_id").strip()})

        m = MEMORY_UNLOCK_RE.match(t)
        if m:
            return _invocation_if_enabled(
                61,
                {
                    "action": "unlock",
                    "item_id": m.group("item_id").strip(),
                    "confirmed": bool((m.group("confirm") or "").strip()),
                },
            )

        m = MEMORY_DELETE_RE.match(t)
        if m:
            return _invocation_if_enabled(
                61,
                {
                    "action": "delete",
                    "item_id": m.group("item_id").strip(),
                    "confirmed": bool((m.group("confirm") or "").strip()),
                },
            )

        m = MEMORY_DELETE_FRIENDLY_RE.match(t)
        if m:
            return _invocation_if_enabled(
                61,
                {
                    "action": "delete",
                    "item_id": (m.group("item_id") or "last").strip(),
                    "confirmed": bool((m.group("confirm") or "").strip()),
                },
            )

        m = MEMORY_FORGET_THIS_RE.match(t)
        if m:
            return _invocation_if_enabled(
                61,
                {
                    "action": "delete",
                    "item_id": m.group("item_ref").strip().lower(),
                    "confirmed": bool((m.group("confirm") or "").strip()),
                },
            )

        m = MEMORY_SUPERSEDE_RE.match(t)
        if m:
            return _invocation_if_enabled(
                61,
                {
                    "action": "supersede",
                    "item_id": m.group("item_id").strip(),
                    "new_title": m.group("title").strip(),
                    "new_body": m.group("body").strip(),
                    "confirmed": bool((m.group("confirm") or "").strip()),
                },
            )

        m = MEMORY_EDIT_RE.match(t)
        if m:
            return _invocation_if_enabled(
                61,
                {
                    "action": "supersede",
                    "item_id": (m.group("item_id") or "last").strip(),
                    "new_title": "",
                    "new_body": m.group("body").strip(),
                    "confirmed": bool((m.group("confirm") or "").strip()),
                },
            )

        if SHOPIFY_REPORT_RE.match(t):
            tl = t.lower()
            if any(c in tl for c in ("today", "daily")):
                period = "today"
            elif any(c in tl for c in ("last_90_days", "last 90 days", "90 days", "quarter")):
                period = "last_90_days"
            elif any(c in tl for c in ("last_30_days", "last 30 days", "30 days", "month")):
                period = "last_30_days"
            else:
                period = "last_7_days"
            return _invocation_if_enabled(65, {"period": period})

        m = SEND_EMAIL_DRAFT_RE.match(t)
        if m:
            to = (m.group("to") or "").strip()
            subject = (m.group("subject") or "").strip()
            return _invocation_if_enabled(
                64,
                {
                    "to": to,
                    "subject": subject,
                    "body_intent": subject or t,
                    "session_id": session_id or "",
                },
            )

        m = EMAIL_SHORTHAND_RE.match(t)
        if m:
            to = (m.group("to") or "").strip()
            subject = (m.group("subject") or "").strip()
            return _invocation_if_enabled(
                64,
                {
                    "to": to,
                    "subject": subject,
                    "body_intent": subject or t,
                    "session_id": session_id or "",
                },
            )

        if MORNING_BRIEF_RE.match(t):
            return _invocation_if_enabled(63, {"template_id": "morning_brief", "triggered_by": "user_command"})

        m = RUN_TEMPLATE_RE.match(t)
        if m:
            template_id = (m.group("template_id") or "").strip().lower()
            if template_id not in {"open", "search", "research", "summarize", "compare", "track", "memory"}:
                return _invocation_if_enabled(63, {"template_id": template_id, "triggered_by": "user_command"})

        m = COMPARE_STORY_RE.match(t)
        if m:
            return _invocation_if_enabled(
                53,
                {"action": "compare", "topic": m.group("topic").strip(), "days": int(m.group("days"))},
            )

        m = COMPARE_STORIES_RE.match(t)
        if m:
            return _invocation_if_enabled(
                53,
                {
                    "action": "compare_stories",
                    "topics": [m.group("left").strip(), m.group("right").strip()],
                },
            )

        m = SHOW_STORY_RE.match(t)
        if m:
            return _invocation_if_enabled(53, {"action": "show", "topic": m.group("topic").strip()})

        hm = HEADLINE_SUMMARY_RE.match(t)
        if hm:
            selection = (hm.group("sel") or "").strip().lower()
            if selection in {"all", "all headlines"}:
                return _invocation_if_enabled(49, {"selection": "all"})
            if "news headlines" in selection or "headlines on the dashboard" in selection:
                return _invocation_if_enabled(49, {"selection": "all"})
            category_key = _match_news_category(selection)
            if category_key:
                return _invocation_if_enabled(49, {"selection": "category", "category_key": category_key})
            parsed = _parse_headline_selection(selection)
            if parsed:
                return _invocation_if_enabled(49, parsed)

        gm = GENERIC_NEWS_SUMMARY_RE.match(t)
        if gm:
            topic_query = (gm.group("topic") or "").strip()
            if topic_query:
                category_key = _match_news_category(topic_query)
                if category_key:
                    return _invocation_if_enabled(49, {"selection": "category", "category_key": category_key})
                return _invocation_if_enabled(49, {"selection": "topic", "topic_query": topic_query, "recent": True})
            if re.search(r"\b(today'?s|todays|latest|recent|current)\b", t, re.IGNORECASE):
                return _invocation_if_enabled(50, {"read_sources": True})
            return _invocation_if_enabled(49, {"selection": "all"})

        sm = SOURCE_NEWS_SUMMARY_RE.match(t)
        if sm:
            source_query = _normalize_source_query(sm.group("source") or "")
            if source_query:
                if source_query.lower() in {"today", "todays", "today's", "latest", "recent", "current", "the"}:
                    return _invocation_if_enabled(49, {"selection": "all"})
                category_key = _match_news_category(source_query)
                if category_key:
                    return _invocation_if_enabled(49, {"selection": "category", "category_key": category_key})
                return _invocation_if_enabled(49, {"selection": "source", "source_query": source_query})

        m = SET_REPORT_RE.match(t)
        if m:
            return _invocation_if_enabled(48, {"query": m.group("q").strip()})

        if re.search(r"\b(search(?: for)?|look up|research)\b", t, re.IGNORECASE):
            if session_id:
                _set_pending_clarification(session_id, 16)
                _evict_expired_pending_clarifications()
                return Clarification(capability_id=16, message="What would you like to search for?")
            return None

        m = COMMAND_ONLY_RE.match(t)
        if m:
            verb = (m.group("verb") or "").strip().lower()
            prompts: dict[str, tuple[int, str]] = {
                "open": (17, "What should I open? Try 'open the github website', 'open my downloads folder', or 'open file notes.txt'."),
                "search": (16, "What should I search for? Try something like 'search for latest Michigan weather' or 'look up local tax deadline'."),
                "research": (48, "What topic should I research? You can ask naturally, like 'research AI regulation trends'."),
                "summarize": (49, "What should I summarize? Try 'summarize today's news' or 'summarize doc 2'."),
                "compare": (53, "What should I compare? Try 'compare stories AI regulation and chip exports'."),
                "track": (52, "What topic should I track? Try 'follow story AI regulation'."),
                "memory": (
                    61,
                    "Try 'memory overview', 'what do you remember', 'recent memories', "
                    "'search memories for <topic>', 'remember this: <text>', "
                    "'list memories', 'memory show <id>', or 'memory export'.",
                ),
            }
            cap_id, message = prompts.get(verb, (16, "Could you clarify that request?"))
            return Clarification(capability_id=cap_id, message=message)

        return None

    @staticmethod
    def clear_session(session_id: str) -> None:
        _pop_pending_clarification(session_id)

    @staticmethod
    def clear_stale_sessions() -> None:
        _evict_expired_pending_clarifications()
