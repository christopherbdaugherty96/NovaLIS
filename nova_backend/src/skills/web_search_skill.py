"""
NovaLIS Web Search Skill – Phase‑3.5 Freeze Compliant

Constitutional Status:      FROZEN
Authority:                  READ-ONLY, STATELESS, DETERMINISTIC
Execution:                  PROHIBITED
Synthesis:                  PROHIBITED
Memory:                     PROHIBITED
Background:                 PROHIBITED
Implicit Invocation:        PROHIBITED

Invocation:                 User MUST use explicit online phrases:
                            "search for", "search the web for",
                            "look up", "find online", "check online for"

Online Disclosure:          ALWAYS – "I'm checking online."
Return Format:              Structured links (title, URL) – NO snippet, NO summary
Config Flag:                ONLINE_ACCESS_ALLOWED – must be True to run
"""

from __future__ import annotations

import logging
import re
from typing import Optional

from ..base_skill import BaseSkill, SkillResult
from ..nova_config import ONLINE_ACCESS_ALLOWED, WEB_SEARCH_TRIGGERS, WEB_SEARCH_MAX_RESULTS

log = logging.getLogger("nova.skills.web_search")


class WebSearchSkill(BaseSkill):
    """Deterministic, read‑only web lookup – explicit invocation only."""

    name = "web_search"
    description = "Search the web for current information (explicit online request)."

    # ------------------------------------------------------------------
    # Phase‑3.5: can_handle returns True ONLY for explicit online triggers
    #            with word‑boundary protection AND the online guard.
    # ------------------------------------------------------------------
    def can_handle(self, query: str) -> bool:
        """Return True iff query contains an explicit online trigger phrase (whole word)."""
        if not ONLINE_ACCESS_ALLOWED:
            return False

        if not query or not isinstance(query, str):
            return False

        q_lower = query.lower()
        # Word‑boundary enforcement prevents accidental substring matches.
        for phrase in WEB_SEARCH_TRIGGERS:
            pattern = r"\b" + re.escape(phrase) + r"\b"
            if re.search(pattern, q_lower):
                return True
        return False

    # ------------------------------------------------------------------
    # Handle – Phase‑4 compliant stub
    # Web search is now governed and must pass through the Governor.
    # ------------------------------------------------------------------
    async def handle(self, query: str) -> Optional[SkillResult]:
        """
        Execute a single web search.

        Constitutional enforcement:
        - No execution (ActionRequest / execute_action)
        - No synthesis (returns only title + URL)
        - No memory writes
        - No background activity
        - Online disclosure always prepended
        """
        if not self.can_handle(query):
            return None

        # Phase‑4: web search is now handled by the Governor via capability 16.
        # The skill layer no longer performs the search directly.
        return SkillResult(
            success=False,
            message=(
                "Web search is handled through governed execution. "
                "Please use: 'search for <query>'."
            ),
            skill=self.name,
        )

    # ------------------------------------------------------------------
    # Pure function – deterministic, side‑effect free
    # Now uses the EXACT SAME word‑boundary matching as can_handle.
    # Extracts the substring immediately after the matched phrase.
    # (Unused in Phase‑4 stub, but kept for compatibility.)
    # ------------------------------------------------------------------
    def _extract_search_term(self, query: str) -> str:
        """
        Remove the first matching trigger phrase from the query.
        Uses word‑boundary regex to locate the exact match position,
        then removes it and strips leading punctuation/spaces.
        """
        q_lower = query.lower()
        # Sort triggers by length descending – longest match first
        triggers = sorted(WEB_SEARCH_TRIGGERS, key=len, reverse=True)

        for phrase in triggers:
            pattern = r"\b" + re.escape(phrase) + r"\b"
            match = re.search(pattern, q_lower)
            if match:
                # match spans the phrase in the lowercased query.
                # We need the same span in the original case query.
                start, end = match.span()
                # Remove the phrase from the original query
                after = query[end:].strip()
                # Strip leading punctuation, symbols, etc.
                after = re.sub(r"^[^\w]+", "", after)
                return after

        # Fallback – should never be reached because can_handle already matched
        return query.strip()