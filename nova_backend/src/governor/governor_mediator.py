# src/governor/governor_mediator.py

from __future__ import annotations

import re
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Union

_pending_clarification: Dict[str, int] = {}


def _load_enabled_capability_ids() -> set[int]:
    registry_path = Path(__file__).resolve().parents[1] / "config" / "registry.json"
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    return {
        int(item.get("id"))
        for item in payload.get("capabilities", [])
        if item.get("enabled") is True and item.get("id") is not None
    }


def _invocation_if_enabled(capability_id: int, params: Dict[str, Any]) -> Invocation | None:
    if capability_id in _load_enabled_capability_ids():
        return Invocation(capability_id=capability_id, params=params)
    return None

SEARCH_RE = re.compile(r"^\s*(search(?: for)?|look up|research)\s+(?P<q>.+?)\s*$", re.IGNORECASE)
OPEN_RE = re.compile(r"^\s*open\s+(?P<name>\w+)\s*$", re.IGNORECASE)
OPEN_FOLDER_RE = re.compile(r"^\s*open\s+(?P<folder>documents|downloads|desktop|pictures)\s*$", re.IGNORECASE)
SET_VOLUME_RE = re.compile(r"^\s*set\s+volume\s+(?P<level>\d{1,3})\s*$", re.IGNORECASE)
SET_BRIGHTNESS_RE = re.compile(r"^\s*set\s+brightness\s+(?P<level>\d{1,3})\s*$", re.IGNORECASE)
SET_REPORT_RE = re.compile(r"^\s*(report|summarize)\s+(?P<q>.+?)\s*$", re.IGNORECASE)
HEADLINE_SUMMARY_RE = re.compile(
    r"^\s*summarize\s+(?:(?:headline|headlines)\s+)?(?P<sel>all|[\w\s,;&]+)\s*$",
    re.IGNORECASE,
)
INTEL_BRIEF_RE = re.compile(
    r"^\s*(?:daily|intelligence|news)\s+brief\s*$|^\s*give me (?:the )?(?:daily|intelligence)\s+brief\s*$",
    re.IGNORECASE,
)
TOPIC_MAP_RE = re.compile(
    r"^\s*(?:show|open|view)?\s*(?:the\s+)?topic(?:\s+memory)?\s+map\s*$",
    re.IGNORECASE,
)
TRACK_STORY_RE = re.compile(r"^\s*track\s+story\s+(?P<topic>.+?)\s*$", re.IGNORECASE)
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
STOP_TRACKING_RE = re.compile(r"^\s*stop\s+tracking\s+(?P<topic>.+?)\s*$", re.IGNORECASE)
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


def _normalize_number_words(text: str) -> str:
    out = text
    for word, digit in _NUMBER_WORDS.items():
        out = re.sub(rf"\b{word}\b", digit, out, flags=re.IGNORECASE)
    return out


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
        t = re.sub(r"[.?!]+$", "", t)
        if not t:
               return None

        if session_id and session_id in _pending_clarification:
            cap_id = _pending_clarification.pop(session_id)
            if cap_id == 16:
                return _invocation_if_enabled(16, {"query": t})
            return None

        m = SEARCH_RE.match(t)
        if m:
            return _invocation_if_enabled(16, {"query": m.group("q").strip()})

        m = OPEN_FOLDER_RE.match(t)
        if m:
            return _invocation_if_enabled(22, {"target": m.group("folder").strip().lower()})

        m = OPEN_RE.match(t)
        if m:
            return _invocation_if_enabled(17, {"target": m.group("name").strip().lower()})

        if re.match(r"^\s*(speak that|read that|say it)\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(18, {})

        if re.match(r"^\s*volume\s+up\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(19, {"action": "up"})
        if re.match(r"^\s*volume\s+down\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(19, {"action": "down"})

        m = SET_VOLUME_RE.match(t)
        if m:
            return _invocation_if_enabled(19, {"action": "set", "level": int(m.group("level"))})

        if re.match(r"^\s*brightness\s+up\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(21, {"action": "up"})
        if re.match(r"^\s*brightness\s+down\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(21, {"action": "down"})

        m = SET_BRIGHTNESS_RE.match(t)
        if m:
            return _invocation_if_enabled(21, {"action": "set", "level": int(m.group("level"))})

        if re.match(r"^\s*(play|pause|resume)\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(20, {"action": t.lower()})

        if re.match(r"^\s*(system check|system status)\s*$", t, re.IGNORECASE):
            return _invocation_if_enabled(32, {})

        if INTEL_BRIEF_RE.match(t):
            return _invocation_if_enabled(50, {})

        if TOPIC_MAP_RE.match(t):
            return _invocation_if_enabled(51, {})

        m = TRACK_STORY_RE.match(t)
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
            parsed = _parse_headline_selection(selection)
            if parsed:
                return _invocation_if_enabled(49, parsed)

        m = SET_REPORT_RE.match(t)
        if m:
            return _invocation_if_enabled(48, {"query": m.group("q").strip()})

        if re.search(r"\b(search(?: for)?|look up|research)\b", t, re.IGNORECASE):
            if session_id:
                _pending_clarification[session_id] = 16
                return Clarification(capability_id=16, message="What would you like to search for?")
            return None

        return None

    @staticmethod
    def clear_session(session_id: str) -> None:
        _pending_clarification.pop(session_id, None)
