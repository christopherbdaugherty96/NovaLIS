"""Dynamic tool registry for OpenClaw agent intelligence layer.

Replaces the hardcoded template→skill mapping with a metadata-driven
registry that supports runtime discovery, capability querying, and
per-tool configuration.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ToolMetadata:
    """Describes a registered tool's capabilities and constraints."""

    name: str
    description: str
    category: str  # "collection", "mutation", "control"
    tags: tuple[str, ...] = ()
    timeout_seconds: float = 30.0
    cost_per_call: float = 0.0
    rate_limit_per_hour: int | None = None
    is_network_tool: bool = False


class ToolRegistry:
    """Registry for tools available to OpenClaw agents.

    Tools are registered with metadata and a factory callable that
    produces a skill instance ready to call ``handle(query)``.
    """

    def __init__(self) -> None:
        self._factories: dict[str, Callable[..., Any]] = {}
        self._metadata: dict[str, ToolMetadata] = {}
        self._categories: dict[str, list[str]] = {}

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self,
        name: str,
        factory: Callable[..., Any],
        metadata: ToolMetadata,
    ) -> None:
        if name in self._factories:
            raise ValueError(f"Tool '{name}' already registered")
        self._factories[name] = factory
        self._metadata[name] = metadata
        self._categories.setdefault(metadata.category, []).append(name)
        logger.debug("Registered tool %s [%s]", name, metadata.category)

    # ------------------------------------------------------------------
    # Querying
    # ------------------------------------------------------------------

    @property
    def tool_names(self) -> list[str]:
        return list(self._factories)

    def has(self, name: str) -> bool:
        return name in self._factories

    def get_metadata(self, name: str) -> ToolMetadata:
        if name not in self._metadata:
            raise KeyError(f"Tool '{name}' not registered")
        return self._metadata[name]

    def find_by_tags(self, goal: str) -> list[str]:
        """Return tool names whose tags overlap with words in *goal*."""
        words = set(goal.lower().split())
        hits: list[str] = []
        for name, meta in self._metadata.items():
            if words & set(meta.tags):
                hits.append(name)
        return hits

    def find_by_category(self, category: str) -> list[str]:
        return list(self._categories.get(category, []))

    def all_capabilities(self) -> dict[str, dict[str, Any]]:
        return {
            name: {
                "name": m.name,
                "description": m.description,
                "category": m.category,
                "tags": list(m.tags),
                "timeout_seconds": m.timeout_seconds,
                "cost_per_call": m.cost_per_call,
                "is_network_tool": m.is_network_tool,
            }
            for name, m in self._metadata.items()
        }

    # ------------------------------------------------------------------
    # Instantiation
    # ------------------------------------------------------------------

    def create(self, name: str, **kwargs: Any) -> Any:
        """Create a skill instance from the registered factory."""
        if name not in self._factories:
            raise KeyError(f"Tool '{name}' not registered")
        return self._factories[name](**kwargs)


# ======================================================================
# Bootstrap — populate registry with the skills that already exist
# ======================================================================

def _bootstrap() -> ToolRegistry:
    """Create and populate the global tool registry."""
    from src.skills.calendar import CalendarSkill
    from src.skills.news import NewsSkill
    from src.skills.weather import WeatherSkill

    registry = ToolRegistry()

    registry.register(
        "weather",
        lambda network=None: WeatherSkill(network=network),
        ToolMetadata(
            name="weather",
            description="Fetch current weather and short-term forecast",
            category="collection",
            tags=("weather", "forecast", "temperature", "conditions"),
            timeout_seconds=8.0,
            cost_per_call=0.0,
            is_network_tool=True,
        ),
    )

    registry.register(
        "calendar",
        lambda: CalendarSkill(),
        ToolMetadata(
            name="calendar",
            description="Read today's schedule and upcoming events from the local calendar",
            category="collection",
            tags=("calendar", "events", "schedule", "meetings"),
            timeout_seconds=3.0,
            cost_per_call=0.0,
            is_network_tool=False,
        ),
    )

    registry.register(
        "news",
        lambda network=None: NewsSkill(network=network),
        ToolMetadata(
            name="news",
            description="Fetch latest news headlines from RSS feeds",
            category="collection",
            tags=("news", "headlines", "stories", "current"),
            timeout_seconds=10.0,
            cost_per_call=0.0,
            is_network_tool=True,
        ),
    )

    return registry


# Module-level singleton — lazy init on first import
_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    global _registry
    if _registry is None:
        _registry = _bootstrap()
    return _registry
