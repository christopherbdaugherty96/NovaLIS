"""Per-tool budget tracking for OpenClaw.

Extends envelope-level budget metering with per-tool granularity:
  - Track calls, duration, network usage, and cost per tool
  - Enforce per-tool call limits and duration caps
  - Provide per-tool breakdowns alongside the aggregate RunBudgetMeter

This sits alongside (not replacing) RunBudgetMeter — the aggregate
envelope budget remains the hard boundary; per-tool limits are
additional guardrails.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolBudgetConfig:
    """Per-tool budget limits. -1 means unlimited."""
    max_calls: int = -1
    max_duration_seconds: float = -1.0
    max_network_calls: int = -1


@dataclass
class ToolUsageRecord:
    """Running totals for a single tool."""
    calls: int = 0
    total_duration_seconds: float = 0.0
    network_calls: int = 0
    successes: int = 0
    failures: int = 0


class PerToolBudgetExceeded(RuntimeError):
    """Raised when a per-tool budget limit is breached."""

    def __init__(self, tool_name: str, metric: str, used: float, limit: float) -> None:
        self.tool_name = tool_name
        self.metric = metric
        self.used = used
        self.limit = limit
        super().__init__(
            f"Tool '{tool_name}' exceeded {metric} budget ({used}/{limit})"
        )


class PerToolBudgetTracker:
    """Track and enforce per-tool resource budgets.

    Usage:
        tracker = PerToolBudgetTracker()
        tracker.set_limit("weather", ToolBudgetConfig(max_calls=5))
        tracker.record_call("weather", duration=1.2, success=True, network_calls=1)
    """

    def __init__(self) -> None:
        self._limits: dict[str, ToolBudgetConfig] = {}
        self._usage: dict[str, ToolUsageRecord] = {}

    def set_limit(self, tool_name: str, config: ToolBudgetConfig) -> None:
        self._limits[tool_name] = config

    def set_limits(self, configs: dict[str, ToolBudgetConfig]) -> None:
        self._limits.update(configs)

    def record_call(
        self,
        tool_name: str,
        *,
        duration_seconds: float = 0.0,
        success: bool = True,
        network_calls: int = 0,
    ) -> None:
        """Record a tool call and check limits."""
        usage = self._usage.setdefault(tool_name, ToolUsageRecord())
        usage.calls += 1
        usage.total_duration_seconds += duration_seconds
        usage.network_calls += network_calls
        if success:
            usage.successes += 1
        else:
            usage.failures += 1

        self._check_limits(tool_name, usage)

    def _check_limits(self, tool_name: str, usage: ToolUsageRecord) -> None:
        config = self._limits.get(tool_name)
        if config is None:
            return

        if config.max_calls >= 0 and usage.calls > config.max_calls:
            raise PerToolBudgetExceeded(
                tool_name, "calls", usage.calls, config.max_calls,
            )
        if config.max_duration_seconds >= 0 and usage.total_duration_seconds > config.max_duration_seconds:
            raise PerToolBudgetExceeded(
                tool_name, "duration_seconds",
                round(usage.total_duration_seconds, 2),
                config.max_duration_seconds,
            )
        if config.max_network_calls >= 0 and usage.network_calls > config.max_network_calls:
            raise PerToolBudgetExceeded(
                tool_name, "network_calls",
                usage.network_calls, config.max_network_calls,
            )

    def can_call(self, tool_name: str) -> bool:
        """Check if a tool still has budget remaining (without recording)."""
        config = self._limits.get(tool_name)
        if config is None:
            return True

        usage = self._usage.get(tool_name, ToolUsageRecord())

        if config.max_calls >= 0 and usage.calls >= config.max_calls:
            return False
        if config.max_duration_seconds >= 0 and usage.total_duration_seconds >= config.max_duration_seconds:
            return False
        if config.max_network_calls >= 0 and usage.network_calls >= config.max_network_calls:
            return False
        return True

    def usage(self, tool_name: str) -> dict[str, Any]:
        """Get usage summary for a single tool."""
        record = self._usage.get(tool_name)
        if record is None:
            return {}
        return {
            "tool_name": tool_name,
            "calls": record.calls,
            "successes": record.successes,
            "failures": record.failures,
            "total_duration_seconds": round(record.total_duration_seconds, 3),
            "network_calls": record.network_calls,
            "has_budget": self.can_call(tool_name),
        }

    def all_usage(self) -> dict[str, dict[str, Any]]:
        """Get usage summaries for all tracked tools."""
        return {name: self.usage(name) for name in self._usage}

    def snapshot(self) -> dict[str, Any]:
        """Full snapshot suitable for inclusion in run results."""
        return {
            "per_tool": self.all_usage(),
            "tools_tracked": len(self._usage),
            "tools_over_budget": [
                name for name in self._usage if not self.can_call(name)
            ],
        }
