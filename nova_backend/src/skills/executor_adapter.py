"""Generic adapter: wraps any Governor executor into BaseSkill/SkillResult.

Allows OpenClaw's tool registry to treat executors as first-class skills
without writing a dedicated skill class for each one.

Usage:
    adapter = ExecutorSkillAdapter(
        name="volume",
        description="Control system volume",
        executor_factory=lambda: VolumeExecutor(),
        capability_id=14,
    )
    result = await adapter.handle("set volume to 50%")
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

from src.base_skill import BaseSkill, SkillResult

logger = logging.getLogger(__name__)


class _ActionRequest:
    """Minimal duck-typed ActionRequest for Governor executors."""

    def __init__(self, capability_id: int, params: dict[str, Any], request_id: str) -> None:
        self.capability_id = capability_id
        self.params = params
        self.request_id = request_id


class ExecutorSkillAdapter(BaseSkill):
    """Wraps a Governor executor into the BaseSkill/SkillResult contract."""

    def __init__(
        self,
        *,
        name: str,
        description: str,
        executor_factory: Callable[[], Any],
        capability_id: int,
        param_extractor: Callable[[str], dict[str, Any]] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self._executor_factory = executor_factory
        self._capability_id = capability_id
        self._param_extractor = param_extractor or (lambda q: {"query": q})

    def can_handle(self, query: str) -> bool:
        return bool((query or "").strip())

    async def handle(self, query: str) -> SkillResult:
        params = self._param_extractor(query)
        try:
            result = await asyncio.to_thread(self._execute_sync, params)
            return result
        except Exception as exc:
            logger.warning("%s executor failed: %s", self.name, exc)
            return SkillResult(
                success=False,
                message=f"{self.name} is unavailable right now.",
                data={"error": str(exc)[:200]},
                skill=self.name,
            )

    def _execute_sync(self, params: dict[str, Any]) -> SkillResult:
        executor = self._executor_factory()
        request = _ActionRequest(
            capability_id=self._capability_id,
            params=params,
            request_id=f"openclaw_{self.name}_{id(self)}",
        )
        action_result = executor.execute(request)

        return SkillResult(
            success=action_result.success,
            message=action_result.message,
            data=action_result.data if isinstance(action_result.data, dict) else {},
            skill=self.name,
        )
