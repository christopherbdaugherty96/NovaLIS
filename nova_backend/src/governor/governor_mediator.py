# src/governor/governor_mediator.py

"""
GovernorMediator – Phase‑4 ready parser shim.
- Detect explicit governed invocations (deterministic).
- Never creates ActionRequests.
- Never executes actions.
"""

from __future__ import annotations

import re
from typing import Optional, Dict, Any, Tuple

# Example deterministic phrase patterns (expand via static phrase bank)
# "search for X" -> capability 16
SEARCH_RE = re.compile(r"^\s*(search for|look up|research)\s+(?P<q>.+?)\s*$", re.IGNORECASE)


class GovernorMediator:
    @staticmethod
    def mediate(text: str) -> str:
        # Phase‑3 behavior preserved: sanitize only.
        if not text or not text.strip():
            return "I'm not sure right now."
        return text.strip()

    @staticmethod
    def parse_governed_invocation(text: str) -> Optional[Tuple[int, Dict[str, Any]]]:
        """
        Returns (capability_id, params) if explicit invocation detected.
        Otherwise returns None.
        """
        t = (text or "").strip()

        m = SEARCH_RE.match(t)
        if m:
            query = m.group("q").strip()
            if query:                          # ensure non‑empty query
                return (16, {"query": query})

        return None