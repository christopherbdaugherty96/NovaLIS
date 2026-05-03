"""
Core RoutineGraph objects: RoutineBlock, RoutineGraph, RoutineRun, RoutineReceipt.

Planning and record-keeping vocabulary only.

They do not:
- execute capabilities
- authorize actions
- call an LLM
- create external effects
- mutate session state
"""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# ID / timestamp helpers
# ---------------------------------------------------------------------------

def _run_id() -> str:
    return f"RUN-{uuid.uuid4().hex[:8].upper()}"


def _receipt_id() -> str:
    return f"RR-{uuid.uuid4().hex[:8].upper()}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Core objects
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RoutineBlock:
    """A named step definition within a RoutineGraph."""

    name: str
    description: str
    output_label: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("RoutineBlock name must not be empty.")
        if not self.output_label.strip():
            raise ValueError("RoutineBlock output_label must not be empty.")


@dataclass(frozen=True)
class RoutineGraph:
    """Ordered sequence of RoutineBlocks defining a routine."""

    name: str
    blocks: tuple[RoutineBlock, ...]
    description: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("RoutineGraph name must not be empty.")
        if not self.blocks:
            raise ValueError("RoutineGraph must have at least one block.")

    @property
    def block_names(self) -> tuple[str, ...]:
        return tuple(b.name for b in self.blocks)


@dataclass(frozen=True)
class RoutineRun:
    """
    Record of a single execution of a RoutineGraph.

    Non-authorizing: execution_performed and authorization_granted are
    enforced False via __post_init__ and cannot be overridden by callers.

    Note: `outputs` is a dict (shallow mutable). The field reference is
    frozen (cannot be replaced), but Python does not prevent mutation of
    the dict's contents. This is a record/snapshot — callers must not
    mutate it after construction. to_dict() returns a deep copy so
    serialised output is independent of the original.
    """

    run_id: str
    graph_name: str
    started_at: str
    completed_at: str
    blocks_run: tuple[str, ...]
    outputs: dict[str, Any]
    warnings: tuple[str, ...]
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "execution_performed", False)
        object.__setattr__(self, "authorization_granted", False)
        if not self.run_id.strip():
            raise ValueError("RoutineRun run_id must not be empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "graph_name": self.graph_name,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "blocks_run": list(self.blocks_run),
            "outputs": copy.deepcopy(self.outputs),
            "warnings": list(self.warnings),
            "execution_performed": False,
            "authorization_granted": False,
        }


@dataclass(frozen=True)
class RoutineReceipt:
    """
    Non-authorizing proof artifact for a completed RoutineRun.

    Suitable for storing in a ledger or surfacing in a Trust Panel.
    Carries provenance and source information but not the full output —
    use RoutineRun for that.

    execution_performed and authorization_granted are enforced False via
    __post_init__ and cannot be overridden by callers.
    """

    receipt_id: str
    run_id: str
    graph_name: str
    completed_at: str
    blocks_run: tuple[str, ...]
    sources_consulted: tuple[str, ...]
    warnings: tuple[str, ...]
    execution_performed: bool = False
    authorization_granted: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "execution_performed", False)
        object.__setattr__(self, "authorization_granted", False)
        if not self.receipt_id.strip():
            raise ValueError("RoutineReceipt receipt_id must not be empty.")
        if not self.run_id.strip():
            raise ValueError("RoutineReceipt run_id must not be empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "run_id": self.run_id,
            "graph_name": self.graph_name,
            "completed_at": self.completed_at,
            "blocks_run": list(self.blocks_run),
            "sources_consulted": list(self.sources_consulted),
            "warnings": list(self.warnings),
            "execution_performed": False,
            "authorization_granted": False,
        }
