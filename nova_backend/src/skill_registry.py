# src/skill_registry.py

"""
NovaLIS Skill Registry — Phase 3 Canonical
"""

from __future__ import annotations

import inspect
import logging
from typing import List, Optional

from src.base_skill import BaseSkill, SkillResult
from src.skills.system import SystemSkill
from src.skills.weather import WeatherSkill
from src.skills.news import NewsSkill
from src.skills.general_chat import GeneralChatSkill
from src.governor.network_mediator import NetworkMediator

log = logging.getLogger("nova")


class SkillRegistry:
    def __init__(self, network: NetworkMediator | None = None) -> None:
        """
        network is the governor-scoped mediator injected into all networked skills.
        """
        self.network = network or NetworkMediator()

        # Base skills – always present (original Phase‑3 implementations)
        skills: List[BaseSkill] = [
            SystemSkill(),
            WeatherSkill(network=self.network),
            NewsSkill(network=self.network),
        ]

        # General chat is the final fallback
        skills.append(GeneralChatSkill(network=self.network))

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