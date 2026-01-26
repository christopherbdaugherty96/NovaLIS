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

log = logging.getLogger("nova")


class SkillRegistry:
    def __init__(self) -> None:
        self.skills: List[BaseSkill] = [
            SystemSkill(),
            WeatherSkill(),
            NewsSkill(),
            GeneralChatSkill(),
        ]

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
