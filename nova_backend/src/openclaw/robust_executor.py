"""Robust tool execution for OpenClaw — retry, fallback, parallel, and metering.

Replaces the bare ``asyncio.wait_for(...) except: return None`` pattern with
structured retry/fallback logic and budget-aware parallel execution.
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from src.openclaw.tool_registry import ToolMetadata, ToolRegistry

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------
# Execution record (per-call)
# ------------------------------------------------------------------

@dataclass
class ToolCallRecord:
    tool_name: str
    attempt: int
    success: bool
    duration_seconds: float
    error: str | None = None


# ------------------------------------------------------------------
# Robust executor
# ------------------------------------------------------------------

@dataclass
class RetryConfig:
    """Controls retry behaviour for a single tool call."""
    max_retries: int = 2  # 1 original + 2 retries = 3 attempts
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 15.0


class RobustExecutor:
    """Execute skill ``handle()`` calls with retry, fallback, and metering.

    This does NOT go through Governor — it wraps the raw skill layer.
    Governor integration lives one level up in the runner.
    """

    def __init__(self, *, retry_config: RetryConfig | None = None) -> None:
        self._config = retry_config or RetryConfig()
        self.call_log: list[ToolCallRecord] = []

    # ------------------------------------------------------------------
    # Core: call with retry
    # ------------------------------------------------------------------

    async def call_skill(
        self,
        skill: Any,
        query: str,
        *,
        timeout_seconds: float = 30.0,
        tool_name: str = "unknown",
    ) -> Any | None:
        """Call ``skill.handle(query)`` with retry on failure.

        Returns the result on success, or ``None`` if all attempts fail.
        Each failure is logged to ``self.call_log``.
        """
        last_error: Exception | None = None

        for attempt in range(1 + self._config.max_retries):
            t0 = time.monotonic()
            try:
                result = await asyncio.wait_for(
                    skill.handle(query),
                    timeout=timeout_seconds,
                )
                duration = time.monotonic() - t0
                self.call_log.append(ToolCallRecord(
                    tool_name=tool_name,
                    attempt=attempt,
                    success=True,
                    duration_seconds=round(duration, 3),
                ))
                if attempt > 0:
                    logger.info(
                        "Tool '%s' succeeded on retry %d (%.2fs)",
                        tool_name, attempt, duration,
                    )
                return result

            except Exception as exc:
                last_error = exc
                duration = time.monotonic() - t0
                error_str = str(exc).strip() or type(exc).__name__
                self.call_log.append(ToolCallRecord(
                    tool_name=tool_name,
                    attempt=attempt,
                    success=False,
                    duration_seconds=round(duration, 3),
                    error=error_str[:200],
                ))

                if attempt < self._config.max_retries:
                    delay = min(
                        self._config.base_delay_seconds * (2 ** attempt),
                        self._config.max_delay_seconds,
                    )
                    logger.warning(
                        "Tool '%s' failed (attempt %d/%d): %s — retrying in %.1fs",
                        tool_name,
                        attempt + 1,
                        1 + self._config.max_retries,
                        str(exc)[:120],
                        delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        "Tool '%s' failed after %d attempts: %s",
                        tool_name,
                        1 + self._config.max_retries,
                        str(exc)[:120],
                    )

        return None

    # ------------------------------------------------------------------
    # Parallel execution (budget-aware)
    # ------------------------------------------------------------------

    async def call_many_parallel(
        self,
        calls: list[dict[str, Any]],
        *,
        max_concurrent: int = 4,
        budget_network_remaining: int | None = None,
    ) -> dict[str, Any | None]:
        """Run multiple skill calls in parallel.

        Each entry in *calls* is ``{"skill": <skill>, "query": <str>,
        "timeout": <float>, "tool_name": <str>}``.

        If *budget_network_remaining* is set and the number of network
        tools would exceed it, falls back to sequential execution so
        each call can check the budget individually.

        Returns ``{tool_name: result_or_None}``.
        """
        if budget_network_remaining is not None:
            network_count = sum(
                1 for c in calls
                if c.get("is_network_tool", False)
            )
            if network_count > budget_network_remaining:
                logger.warning(
                    "Parallel execution would exceed network budget "
                    "(%d calls, %d remaining) — running sequentially",
                    network_count,
                    budget_network_remaining,
                )
                return await self._call_many_sequential(calls)

        sem = asyncio.Semaphore(max_concurrent)

        async def _guarded(call: dict[str, Any]) -> tuple[str, Any | None]:
            async with sem:
                result = await self.call_skill(
                    call["skill"],
                    call["query"],
                    timeout_seconds=call.get("timeout", 30.0),
                    tool_name=call["tool_name"],
                )
                return call["tool_name"], result

        pairs = await asyncio.gather(
            *[_guarded(c) for c in calls],
            return_exceptions=True,
        )

        results: dict[str, Any | None] = {}
        for item in pairs:
            if isinstance(item, Exception):
                logger.error("Parallel call raised: %s", item)
                continue
            name, result = item
            results[name] = result
        return results

    async def _call_many_sequential(
        self,
        calls: list[dict[str, Any]],
    ) -> dict[str, Any | None]:
        results: dict[str, Any | None] = {}
        for call in calls:
            result = await self.call_skill(
                call["skill"],
                call["query"],
                timeout_seconds=call.get("timeout", 30.0),
                tool_name=call["tool_name"],
            )
            results[call["tool_name"]] = result
        return results

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats_for(self, tool_name: str) -> dict[str, Any]:
        records = [r for r in self.call_log if r.tool_name == tool_name]
        if not records:
            return {}
        successes = sum(1 for r in records if r.success)
        durations = [r.duration_seconds for r in records]
        return {
            "tool_name": tool_name,
            "total_calls": len(records),
            "successes": successes,
            "failures": len(records) - successes,
            "success_rate": successes / len(records),
            "avg_duration_s": round(sum(durations) / len(durations), 3),
        }
