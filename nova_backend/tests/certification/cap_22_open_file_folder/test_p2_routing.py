# tests/certification/cap_22_open_file_folder/test_p2_routing.py
"""
Phase 2 — Routing certification for capability 22 (open_file_folder).

Verifies GovernorMediator routes folder-open intents to cap 22 and
does NOT route unrelated intents to it.

No canonical routing test file exists for cap 22 — these tests are
written directly rather than re-exported.
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse(text: str, session_id: str | None = None):
    from src.governor.governor_mediator import GovernorMediator
    return GovernorMediator.parse_governed_invocation(
        text, session_id=session_id
    )


def _invocation(text: str):
    from src.governor.governor_mediator import Invocation
    result = _parse(text)
    assert isinstance(result, Invocation), (
        f"Expected Invocation for {text!r}, got {type(result).__name__}"
    )
    return result


# ---------------------------------------------------------------------------
# Folder-open intents → cap 22
# ---------------------------------------------------------------------------

def test_open_downloads_routes_to_cap22():
    inv = _invocation("open my downloads folder")
    assert inv.capability_id == 22


def test_open_documents_routes_to_cap22():
    inv = _invocation("open my documents folder")
    assert inv.capability_id == 22


def test_open_pictures_routes_to_cap22():
    inv = _invocation("open my pictures folder")
    assert inv.capability_id == 22


# ---------------------------------------------------------------------------
# Non-folder intents → NOT cap 22
# ---------------------------------------------------------------------------

def test_search_does_not_route_to_cap22():
    result = _parse("search for latest AI news")
    from src.governor.governor_mediator import Invocation
    if isinstance(result, Invocation):
        assert result.capability_id != 22, (
            "Search intent should not route to cap 22"
        )


def test_email_does_not_route_to_cap22():
    result = _parse("send an email to test@example.com")
    from src.governor.governor_mediator import Invocation
    if isinstance(result, Invocation):
        assert result.capability_id != 22, (
            "Email intent should not route to cap 22"
        )
