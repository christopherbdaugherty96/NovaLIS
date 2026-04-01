# tests/openclaw/test_openclaw_execute_executor.py
"""
End-to-end tests for OpenClawExecuteExecutor (cap 63).

Tests cover:
- Missing template_id returns failure
- inbox_check (RuntimeError) returns failure with message preserved
- Unknown template (KeyError) returns failure with helpful message
- Successful run returns ActionResult.ok with correct fields
- Governor mediator maps "morning brief" and "run <template>" to cap 63
- Registry has cap 63 registered and enabled
"""
from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.actions.action_request import ActionRequest
from src.actions.action_result import ActionResult
from src.executors.openclaw_execute_executor import OpenClawExecuteExecutor
from src.governor.governor_mediator import GovernorMediator, Invocation


# ---------------------------------------------------------------------------
# Executor unit tests
# ---------------------------------------------------------------------------

def _make_req(params: dict) -> ActionRequest:
    return ActionRequest(capability_id=63, params=params)


def test_missing_template_id_returns_failure():
    req = _make_req({})
    result = OpenClawExecuteExecutor().execute(req)
    assert not result.success
    assert "template_id" in result.message.lower()


def test_blank_template_id_returns_failure():
    req = _make_req({"template_id": "   "})
    result = OpenClawExecuteExecutor().execute(req)
    assert not result.success


def test_inbox_check_runtime_error_returns_failure():
    req = _make_req({"template_id": "inbox_check", "triggered_by": "test"})
    with patch.object(
        OpenClawExecuteExecutor,
        "_run_template",
        new=AsyncMock(side_effect=RuntimeError("inbox_check is not ready: email connector unavailable")),
    ):
        result = OpenClawExecuteExecutor().execute(req)
    assert not result.success
    assert "inbox_check" in result.message


def test_unknown_template_key_error_returns_failure():
    req = _make_req({"template_id": "nonexistent_xyz"})
    with patch.object(
        OpenClawExecuteExecutor,
        "_run_template",
        new=AsyncMock(side_effect=KeyError("nonexistent_xyz")),
    ):
        result = OpenClawExecuteExecutor().execute(req)
    assert not result.success
    assert "nonexistent_xyz" in result.message


def test_generic_exception_returns_failure():
    req = _make_req({"template_id": "morning_brief"})
    with patch.object(
        OpenClawExecuteExecutor,
        "_run_template",
        new=AsyncMock(side_effect=Exception("network timeout")),
    ):
        result = OpenClawExecuteExecutor().execute(req)
    assert not result.success
    assert "morning_brief" in result.message


def test_successful_run_returns_ok_with_summary():
    req = _make_req({"template_id": "morning_brief", "triggered_by": "user_command"})
    fake_result = {
        "summary": "Good morning. Weather: sunny. Top stories: ...",
        "template_label": "Morning Brief",
        "token_count": 312,
        "route": "morning_brief",
        "started_at": "2026-04-01T07:00:00+00:00",
        "completed_at": "2026-04-01T07:00:04+00:00",
    }
    with patch.object(
        OpenClawExecuteExecutor,
        "_run_template",
        new=AsyncMock(return_value=fake_result),
    ):
        result = OpenClawExecuteExecutor().execute(req)
    assert result.success
    assert "Good morning" in result.message
    assert result.data["template_id"] == "morning_brief"
    assert result.data["triggered_by"] == "user_command"
    assert result.data["template_label"] == "Morning Brief"
    assert result.data["token_count"] == 312


def test_successful_run_falls_back_to_content_key():
    req = _make_req({"template_id": "evening_digest"})
    fake_result = {"content": "Evening wrap-up: markets closed up."}
    with patch.object(
        OpenClawExecuteExecutor,
        "_run_template",
        new=AsyncMock(return_value=fake_result),
    ):
        result = OpenClawExecuteExecutor().execute(req)
    assert result.success
    assert "Evening wrap-up" in result.message


def test_successful_run_with_empty_summary_gets_fallback_message():
    req = _make_req({"template_id": "market_watch"})
    fake_result = {}
    with patch.object(
        OpenClawExecuteExecutor,
        "_run_template",
        new=AsyncMock(return_value=fake_result),
    ):
        result = OpenClawExecuteExecutor().execute(req)
    assert result.success
    assert "market_watch" in result.message


def test_default_triggered_by_is_governed_invocation():
    req = _make_req({"template_id": "morning_brief"})
    mock = AsyncMock(return_value={"summary": "ok"})
    with patch.object(OpenClawExecuteExecutor, "_run_template", new=mock):
        result = OpenClawExecuteExecutor().execute(req)
    assert result.success
    _args, _kwargs = mock.call_args
    assert _kwargs.get("triggered_by") == "governed_invocation"


# ---------------------------------------------------------------------------
# Mediator routing tests
# ---------------------------------------------------------------------------

def test_morning_brief_routes_to_cap_63():
    inv = GovernorMediator.parse_governed_invocation("morning brief")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 63
    assert inv.params["template_id"] == "morning_brief"


def test_run_morning_brief_routes_to_cap_63():
    inv = GovernorMediator.parse_governed_invocation("run morning brief")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 63


def test_run_template_generic_routes_to_cap_63():
    inv = GovernorMediator.parse_governed_invocation("run evening_digest")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 63
    assert inv.params["template_id"] == "evening_digest"


def test_run_template_with_home_agent_prefix():
    inv = GovernorMediator.parse_governed_invocation("run home agent morning_brief")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 63


def test_reserved_verbs_not_routed_to_cap_63():
    """Common verbs like 'run open', 'run search' must not leak into cap 63."""
    for text in ("run open", "run search", "run memory"):
        result = GovernorMediator.parse_governed_invocation(text)
        if isinstance(result, Invocation):
            assert result.capability_id != 63, f"'{text}' should not route to cap 63"


# ---------------------------------------------------------------------------
# Registry integration test
# ---------------------------------------------------------------------------

def test_cap_63_registered_and_enabled():
    import json
    from pathlib import Path

    registry_path = Path(__file__).resolve().parents[2] / "src" / "config" / "registry.json"
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    caps = {c["id"]: c for c in payload.get("capabilities", [])}
    assert 63 in caps, "Cap 63 must be in registry capabilities"
    cap = caps[63]
    assert cap["name"] == "openclaw_execute"
    assert cap["enabled"] is True
    assert cap["authority_class"] == "read_only_network"
    assert cap["external_effect"] is True
    assert cap["reversible"] is True
    assert cap["requires_confirmation"] is False

    # Must appear in home_agent group
    groups = payload.get("capability_groups", {})
    assert 63 in groups.get("home_agent", [])

    # Must be reachable from both profiles that expose home_agent
    for profile_name in ("local-control", "analyst"):
        profile = payload["profiles"][profile_name]
        assert "home_agent" in profile["groups"], (
            f"Profile '{profile_name}' must include home_agent group"
        )
