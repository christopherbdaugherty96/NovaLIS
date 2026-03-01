# src/governor/governor_mediator.py

"""
GovernorMediator – Phase‑4 ready parser shim with one‑strike clarification.
- Detects explicit governed invocations (deterministic).
- Maintains ephemeral clarification state per session.
- Returns structured dataclass instances to disambiguate invocation, clarification, or none.
- Never creates ActionRequests. Never executes actions.
- Conversation-layer initiative may shape language only; authority stays with Governor routing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union

from src.conversation.response_style_router import InputNormalizer

# Session‑scoped clarification state (process‑wide, ephemeral).
# Key: session_id (provided by caller, e.g., websocket handler)
# Value: pending clarification payload.
_pending_clarification: Dict[str, Dict[str, Any]] = {}

SEARCH_RE = re.compile(
    r"^\s*(search(?: for)?|look up|research)\s+(?P<q>.+?)\s*$",
    re.IGNORECASE,
)

OPEN_RE = re.compile(
    r"^\s*open\s+(?P<name>[\w.-]+)\s*$",
    re.IGNORECASE,
)

OPEN_ONLY_RE = re.compile(r"^\s*open\s*$", re.IGNORECASE)

YES_RE = re.compile(r"^(yes|y|confirm)$", re.IGNORECASE)
NO_RE = re.compile(r"^(no|n|cancel)$", re.IGNORECASE)


@dataclass(frozen=True)
class Invocation:
    """A fully resolved governed action invocation."""

    capability_id: int
    params: Dict[str, Any]


@dataclass(frozen=True)
class Clarification:
    """A request for more information to complete an invocation."""

    capability_id: int
    message: str


class GovernorMediator:
    @staticmethod
    def mediate(text: str) -> str:
        """Deterministic, grammar-tolerant sanitization only."""
        clean = InputNormalizer.normalize(text)
        if not clean:
            return "I'm here when you're ready."
        return clean

    @staticmethod
    def parse_governed_invocation(
        text: str,
        session_id: Optional[str] = None,
    ) -> Union[Invocation, Clarification, None]:
        t = (text or "").strip().rstrip(".?!")
        if not t:
            return None

        if session_id and session_id in _pending_clarification:
            pending = _pending_clarification.pop(session_id)
            cap_id = int(pending.get("capability_id", 0))

            if cap_id == 16:
                return Invocation(capability_id=16, params={"query": t})

            if cap_id == 17:
                target = str(pending.get("target", "")).strip()
                if YES_RE.match(t):
                    return Invocation(capability_id=17, params={"target": target})
                if NO_RE.match(t):
                    return Clarification(capability_id=17, message="Okay, I won't open it.")
                return Clarification(capability_id=17, message="Please answer yes or no.")

            return None

        m = SEARCH_RE.match(t)
        if m:
            query = m.group("q").strip()
            if query:
                return Invocation(capability_id=16, params={"query": query})

        if OPEN_ONLY_RE.match(t):
            if session_id:
                _pending_clarification[session_id] = {"capability_id": 17}
                return Clarification(capability_id=17, message="Which site should I open?")
            return None

        m = OPEN_RE.match(t)
        if m:
            name = m.group("name").strip().lower()
            if not name:
                return None
            if session_id:
                _pending_clarification[session_id] = {"capability_id": 17, "target": name}
                display = name if "." in name else f"{name}.com"
                return Clarification(capability_id=17, message=f"Did you want me to open {display}?")
            return Invocation(capability_id=17, params={"target": name})

        if re.match(r"^\s*(speak that|read that|say it)\s*$", t, re.IGNORECASE):
            return Invocation(capability_id=18, params={})

        if re.search(r"\b(search(?: for)?|look up|research)\b", t, re.IGNORECASE):
            if session_id:
                _pending_clarification[session_id] = {"capability_id": 16}
                return Clarification(capability_id=16, message="What would you like me to search for?")
            return None

        return None

    @staticmethod
    def clear_session(session_id: str) -> None:
        _pending_clarification.pop(session_id, None)
