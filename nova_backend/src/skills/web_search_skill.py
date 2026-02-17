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
    # Handle – single, synchronous, read‑only web fetch
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

        # ----------------------------------------------------------------
        # Lazy import – never crash startup if ddgs is missing
        # ----------------------------------------------------------------
        try:
            from ..tools.web_search import run_web_search
        except ImportError as e:
            log.debug(f"Web search tool not available: {e}")
            return SkillResult(
                success=False,
                message="Web search is not available right now.",
                skill=self.name,
            )

        # Extract the actual search term by removing the matched trigger phrase.
        search_term = self._extract_search_term(query)
        if len(search_term) < 2:
            return SkillResult(
                success=False,
                message="Please provide a more specific search term.",
                skill=self.name,
            )

        # ------------------------------------------------------------------
        # Single fetch – no retries, no follow‑up, no caching
        # Results count governed by central configuration.
        # ------------------------------------------------------------------
        try:
            raw_results = run_web_search(
                query=search_term,
                max_results=WEB_SEARCH_MAX_RESULTS
            )

            if not raw_results:
                return SkillResult(
                    success=False,
                    message="I couldn't find any results for that.",
                    skill=self.name,
                )

            # ------------------------------------------------------------------
            # Strict Phase‑3.5: strip snippet, keep only title + url
            # No synthesis, no ranking, no interpretation
            # ------------------------------------------------------------------


            structured = [
                {"title": r["title"], "url": r["url"]}
                for r in raw_results
                if r.get("title") and r.get("url")
            ]

            if not structured:
                return SkillResult(
                    success=False,
                    message="Found results, but they lacked usable titles or links.",
                    skill=self.name,
                )

            # ------------------------------------------------------------------
            # Online disclosure – mandatory
            # ------------------------------------------------------------------
            count = len(structured)
            message = (
                "I'm checking online. "
                f"I found {count} result{'s' if count != 1 else ''}. "
                "You can view the links below."
            )

            # ------------------------------------------------------------------
            # Canonical widget payload – Phase‑3 UI contract
            # ------------------------------------------------------------------
            widget_data = {
                "type": "web_search_results",
                "items": structured,
            }

            return SkillResult(
                success=True,
                message=message,
                skill=self.name,
                widget_data=widget_data,
                data={},  # unused in Phase‑3
            )

        except Exception as e:
            log.debug(f"Web search failed: {e}")
            return SkillResult(
                success=False,
                message="I'm unable to search right now.",
                skill=self.name,
            )

    # ------------------------------------------------------------------
    # Pure function – deterministic, side‑effect free
    # Now uses the EXACT SAME word‑boundary matching as can_handle.
    # Extracts the substring immediately after the matched phrase.
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