# tests/certification/conftest.py
"""
Shared fixtures and helpers for capability certification tests.

All certification tests use these to avoid boilerplate duplication and to
ensure every phase tests the same interface in the same way.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_HERE = Path(__file__).resolve()
# Walk up to find nova_backend root (works in git worktrees too)
NOVA_BACKEND_ROOT = next(
    (p for p in _HERE.parents if p.name == "nova_backend"),
    _HERE.parents[2],
)
LOCKS_FILE = NOVA_BACKEND_ROOT / "src" / "config" / "capability_locks.json"
REGISTRY_FILE = NOVA_BACKEND_ROOT / "src" / "config" / "registry.json"


# ---------------------------------------------------------------------------
# Lock file helpers
# ---------------------------------------------------------------------------

def load_locks() -> dict:
    """Return the parsed capability_locks.json."""
    return json.loads(LOCKS_FILE.read_text(encoding="utf-8"))


def load_registry() -> dict:
    """Return the parsed registry.json."""
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def locked_capability_ids() -> list[int]:
    """Return the IDs of all capabilities whose 'locked' flag is True."""
    locks = load_locks()
    return [int(cap_id) for cap_id, entry in locks["capabilities"].items() if entry.get("locked")]


# ---------------------------------------------------------------------------
# Shared test doubles
# ---------------------------------------------------------------------------

class FakeLedger:
    """Drop-in ledger that records events without touching the filesystem."""

    def __init__(self) -> None:
        self.events: list[tuple[str, dict]] = []

    def log_event(self, event_type: str, payload: dict) -> None:
        self.events.append((event_type, payload))

    def event_names(self) -> list[str]:
        return [name for name, _ in self.events]

    def payloads_for(self, event_type: str) -> list[dict]:
        return [payload for name, payload in self.events if name == event_type]


def make_request(capability_id: int, params: dict[str, Any], request_id: str = "cert-req-1"):
    """Build a minimal ActionRequest-compatible SimpleNamespace."""
    return SimpleNamespace(
        capability_id=capability_id,
        params=params,
        request_id=request_id,
    )


# ---------------------------------------------------------------------------
# Governor factory for integration tests
# ---------------------------------------------------------------------------

def make_governor():
    """Return a Governor instance with a real registry and ledger."""
    from src.governor.governor import Governor
    return Governor()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def fake_ledger() -> FakeLedger:
    return FakeLedger()


@pytest.fixture
def governor():
    return make_governor()


@pytest.fixture
def locks() -> dict:
    return load_locks()


@pytest.fixture
def registry() -> dict:
    return load_registry()
