"""Tool chaining and composition for OpenClaw.

Allows multi-tool workflows where:
- Tools run sequentially with data flowing between them
- Tools run in parallel and results merge
- Steps execute conditionally based on prior results
- Failed steps fall back to alternative tools
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from src.openclaw.robust_executor import RobustExecutor

logger = logging.getLogger(__name__)


@dataclass
class ChainStep:
    """A single step in a tool chain."""

    tool_name: str
    skill: Any
    query: str
    timeout_seconds: float = 30.0
    condition: Callable[[dict[str, Any]], bool] | None = None
    fallback_skill: Any | None = None
    param_builder: Callable[[dict[str, Any]], str] | None = None


class ToolChain:
    """Compose multi-tool workflows with sequential, parallel, and conditional execution."""

    def __init__(self, executor: RobustExecutor) -> None:
        self._executor = executor
        self._steps: list[ChainStep] = []
        self.results: dict[str, Any | None] = {}

    def add(
        self,
        tool_name: str,
        skill: Any,
        query: str,
        *,
        timeout_seconds: float = 30.0,
        condition: Callable[[dict[str, Any]], bool] | None = None,
        fallback_skill: Any | None = None,
        param_builder: Callable[[dict[str, Any]], str] | None = None,
    ) -> "ToolChain":
        """Add a step. Returns self for fluent chaining."""
        self._steps.append(ChainStep(
            tool_name=tool_name,
            skill=skill,
            query=query,
            timeout_seconds=timeout_seconds,
            condition=condition,
            fallback_skill=fallback_skill,
            param_builder=param_builder,
        ))
        return self

    # ------------------------------------------------------------------
    # Execution modes
    # ------------------------------------------------------------------

    async def run_sequential(self) -> dict[str, Any | None]:
        """Run steps one-by-one. Each step can see prior results."""
        self.results = {}
        for step in self._steps:
            if step.condition and not step.condition(self.results):
                logger.debug("Skipping %s — condition not met", step.tool_name)
                continue

            query = step.query
            if step.param_builder:
                query = step.param_builder(self.results)

            result = await self._executor.call_skill(
                step.skill,
                query,
                timeout_seconds=step.timeout_seconds,
                tool_name=step.tool_name,
            )

            if result is None and step.fallback_skill is not None:
                logger.info("Primary %s failed, trying fallback", step.tool_name)
                result = await self._executor.call_skill(
                    step.fallback_skill,
                    query,
                    timeout_seconds=step.timeout_seconds,
                    tool_name=f"{step.tool_name}_fallback",
                )

            self.results[step.tool_name] = result

        return self.results

    async def run_parallel(self, *, max_concurrent: int = 4) -> dict[str, Any | None]:
        """Run all eligible steps in parallel."""
        self.results = {}
        sem = asyncio.Semaphore(max_concurrent)

        async def _run_one(step: ChainStep) -> tuple[str, Any | None]:
            if step.condition and not step.condition(self.results):
                return step.tool_name, None

            query = step.query
            if step.param_builder:
                query = step.param_builder(self.results)

            async with sem:
                result = await self._executor.call_skill(
                    step.skill,
                    query,
                    timeout_seconds=step.timeout_seconds,
                    tool_name=step.tool_name,
                )

            if result is None and step.fallback_skill is not None:
                async with sem:
                    result = await self._executor.call_skill(
                        step.fallback_skill,
                        query,
                        timeout_seconds=step.timeout_seconds,
                        tool_name=f"{step.tool_name}_fallback",
                    )

            return step.tool_name, result

        pairs = await asyncio.gather(
            *[_run_one(s) for s in self._steps],
            return_exceptions=True,
        )

        for item in pairs:
            if isinstance(item, Exception):
                logger.error("Chain step raised: %s", item)
                continue
            name, result = item
            self.results[name] = result

        return self.results

    async def run_phased(self, *, max_concurrent: int = 4) -> dict[str, Any | None]:
        """Run steps in two phases: parallel collection, then sequential
        conditional steps that depend on phase-1 results."""
        self.results = {}
        independent: list[ChainStep] = []
        dependent: list[ChainStep] = []

        for step in self._steps:
            if step.condition is not None or step.param_builder is not None:
                dependent.append(step)
            else:
                independent.append(step)

        # Phase 1: parallel (with fallback support)
        if independent:
            sem = asyncio.Semaphore(max_concurrent)

            async def _run(s: ChainStep) -> tuple[str, Any | None]:
                async with sem:
                    r = await self._executor.call_skill(
                        s.skill, s.query,
                        timeout_seconds=s.timeout_seconds,
                        tool_name=s.tool_name,
                    )
                if r is None and s.fallback_skill is not None:
                    async with sem:
                        r = await self._executor.call_skill(
                            s.fallback_skill, s.query,
                            timeout_seconds=s.timeout_seconds,
                            tool_name=f"{s.tool_name}_fallback",
                        )
                return s.tool_name, r

            pairs = await asyncio.gather(*[_run(s) for s in independent], return_exceptions=True)
            for item in pairs:
                if isinstance(item, Exception):
                    logger.error("Phased step raised: %s", item)
                    continue
                name, result = item
                self.results[name] = result

        # Phase 2: sequential with conditions
        for step in dependent:
            if step.condition and not step.condition(self.results):
                continue

            query = step.query
            if step.param_builder:
                query = step.param_builder(self.results)

            result = await self._executor.call_skill(
                step.skill, query,
                timeout_seconds=step.timeout_seconds,
                tool_name=step.tool_name,
            )

            if result is None and step.fallback_skill is not None:
                result = await self._executor.call_skill(
                    step.fallback_skill, query,
                    timeout_seconds=step.timeout_seconds,
                    tool_name=f"{step.tool_name}_fallback",
                )

            self.results[step.tool_name] = result

        return self.results
