"""
NovaLIS Skill Registry — Phase 3 Canonical
"""

from __future__ import annotations

import inspect
import logging
from typing import List, Optional

from .base_skill import BaseSkill, SkillResult
from .skills.news import NewsSkill
from .skills.weather import WeatherSkill
from .skills.system import SystemSkill
from .skills.general_chat import GeneralChatSkill

# Phase‑3.5 governed web search – conditional on config flag
from .nova_config import ONLINE_ACCESS_ALLOWED

log = logging.getLogger("nova")


class SkillRegistry:
    def __init__(self) -> None:
        # Base skills – always present
        skills: List[BaseSkill] = [
            SystemSkill(),
            WeatherSkill(),
            NewsSkill(),
        ]

        # ----------------------------------------------------------------
        # Constitutional web search – registered BEFORE GeneralChatSkill
        # so that explicit online queries are not swallowed by fallback chat.
        # Only added if explicitly enabled in config.
        # ----------------------------------------------------------------
        if ONLINE_ACCESS_ALLOWED:
            try:
                from .skills.web_search_skill import WebSearchSkill
                skills.append(WebSearchSkill())
            except ImportError:
                log.debug("WebSearchSkill not available – skipping registration.")

        # General chat is the final fallback – never steals explicit triggers.
        skills.append(GeneralChatSkill())

        self.skills = skills

    async def handle_query(self, query: str) -> Optional[SkillResult]:
        for skill in self.skills:
            try:
                if not skill.can_handle(query):
                    continue

                result = skill.handle(query)
                if inspect.iscoroutine(result):
                    result = await result

                if not isinstance(result, SkillResult):
                    return None

                return result

            except Exception as e:
                log.exception(f"[registry] skill error in {skill.name}: {e}")
                return SkillResult(
                    success=False,
                    message="Something went wrong.",
                    data={},
                    widget_data=None,
                    skill=skill.name,
                )

        return None


# -------------------------------------------------
# Phase-3 singleton registry
# -------------------------------------------------
skill_registry = SkillRegistry()
