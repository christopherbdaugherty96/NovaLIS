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

# Session‑scoped clarification state (process‑wide, ephemeral).
# Key: session_id (provided by caller, e.g., websocket handler)
# Value: capability_id that is awaiting clarification.
# Note: This is a simple in‑memory dict; sessions must call clear_session()
#       on disconnect to avoid memory leaks.
_pending_clarification: Dict[str, int] = {}

# Pattern for full web search invocation – now accepts "search" with optional "for"
SEARCH_RE = re.compile(
    r"^\s*(search(?: for)?|look up|research)\s+(?P<q>.+?)\s*$",
    re.IGNORECASE
)

# Pattern for opening a preset website – matches "open <name>"
OPEN_RE = re.compile(
    r"^\s*open\s+(?P<name>\w+)\s*$",
    re.IGNORECASE
)


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
        """Phase‑3 behavior preserved: sanitize only."""
        if not text or not text.strip():
            return "I'm not sure right now."
        return text.strip()

    @staticmethod
    def parse_governed_invocation(
        text: str,
        session_id: Optional[str] = None,
    ) -> Union[Invocation, Clarification, None]:
        """
        Returns:
          - Invocation if a full, valid invocation is detected.
          - Clarification if an incomplete but clearly intended invocation is detected
            and a session_id is provided (to enable one‑strike clarification).
          - None if no invocation is detected.
        """
        t = (text or "").strip()
        t = re.sub(r"[.?!]+$", "", t)
        if not t:
               return None

        # --- Step 1: Check if this session has a pending clarification ---
        if session_id and session_id in _pending_clarification:
            cap_id = _pending_clarification.pop(session_id)
            if cap_id == 16:  # Only web search supports clarification now
                # Treat the entire input as the query
                return Invocation(capability_id=16, params={"query": t})
            else:
                # Unknown pending capability – clear and treat as none
                return None

        # --- Step 2: Try to match a full, valid invocation ---
        m = SEARCH_RE.match(t)
        if m:
            query = m.group("q").strip()
            if query:
                return Invocation(capability_id=16, params={"query": query})

        # Check for "open <name>" invocation
        m = OPEN_RE.match(t)
        if m:
            name = m.group("name").strip().lower()
            return Invocation(capability_id=17, params={"target": name})

        # TTS manual invocation
        if re.match(r"^\s*(speak that|read that|say it)\s*$", t, re.IGNORECASE):
            return Invocation(capability_id=18, params={})

        # --- Step 3: Detect incomplete but clearly intended invocation ---
        # This now matches "search", "search for", "look up", "research"
        if re.search(r"\b(search(?: for)?|look up|research)\b", t, re.IGNORECASE):
            # Incomplete invocation – ask exactly one clarifying question
            if session_id:
                _pending_clarification[session_id] = 16
                return Clarification(
                    capability_id=16,
                    message="What would you like to search for?"
                )
            else:
                # No session – cannot track state, so treat as none
                return None

        # No invocation detected
        return None

    @staticmethod
    def clear_session(session_id: str) -> None:
        """Clear any pending clarification for a session (e.g., on session end)."""
        _pending_clarification.pop(session_id, None)