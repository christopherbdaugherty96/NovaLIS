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
