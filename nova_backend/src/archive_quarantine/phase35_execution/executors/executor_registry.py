"""
Executor Registry (Phase-2 Scaffold)

This registry tracks *known executors* and their declared capabilities.

IMPORTANT:
- Registry does NOT select executors
- Registry does NOT execute actions
- Registry does NOT discover devices
- Registry does NOT auto-register anything

Phase-2:
- Manual population only (if at all)
- Safe to keep empty
"""

from dataclasses import dataclass
from typing import Dict, Set

from .executor_types import ExecutorType


@dataclass(frozen=True)
class ExecutorInfo:
    """
    Declarative description of an executor.

    This is metadata only.
    """
    executor_id: str
    name: str
    executor_type: ExecutorType
    capabilities: Set[str]


class ExecutorRegistry:
    """
    Inert executor registry.

    Exists to support Phase-3 executor routing without refactor.
    """

    def __init__(self) -> None:
        self._executors: Dict[str, ExecutorInfo] = {}

    def register(self, executor: ExecutorInfo) -> None:
        """
        Manually register an executor.

        Phase-2 note:
        - This should not be called automatically
        """
        self._executors[executor.executor_id] = executor

    def list_executors(self) -> Dict[str, ExecutorInfo]:
        """
        Return a copy of all registered executors.
        """
        return dict(self._executors)

    def clear(self) -> None:
        """
        Clear registry (manual / testing only).
        """
        self._executors.clear()


# Phase-2: global empty registry instance
executor_registry = ExecutorRegistry()
