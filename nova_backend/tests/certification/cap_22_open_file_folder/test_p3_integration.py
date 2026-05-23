# tests/certification/cap_22_open_file_folder/test_p3_integration.py
"""
Phase 3 — Integration certification for capability 22 (open_file_folder).

Tests the full Governor spine:
  GovernorMediator → CapabilityRegistry → ExecuteBoundary
  → LedgerWriter → OpenFolderExecutor → ActionResult

Cap 22 requires confirmation (risk_level=confirm), so integration
tests that exercise execution pass confirmed=True. The confirmation-
gate itself is tested separately in the approval-gate regression suite.

System-control open_path is mocked; no real folder opens.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from src.governor.governor import Governor


_CAPABILITY_ID = 22
_CAPABILITY_NAME = "open_file_folder"


def _make_governor() -> Governor:
    return Governor()


# ---------------------------------------------------------------------------
# Registry / capability checks
# ---------------------------------------------------------------------------

def test_cap_22_is_registered():
    gov = _make_governor()
    cap = gov.registry.get(_CAPABILITY_ID)
    assert cap is not None
    assert cap.name == _CAPABILITY_NAME


def test_cap_22_is_enabled():
    gov = _make_governor()
    assert gov.registry.is_enabled(_CAPABILITY_ID) is True


def test_cap_22_requires_confirmation():
    gov = _make_governor()
    cap = gov.registry.get(_CAPABILITY_ID)
    assert cap.requires_confirmation is True


# ---------------------------------------------------------------------------
# Confirmation gate — unconfirmed requests are refused
# ---------------------------------------------------------------------------

def test_unconfirmed_request_is_refused():
    gov = _make_governor()
    result = gov.handle_governed_invocation(
        _CAPABILITY_ID, {"target": "downloads"}
    )
    assert result.success is False


# ---------------------------------------------------------------------------
# Preset folder — happy path through full spine (confirmed)
# ---------------------------------------------------------------------------

def test_preset_folder_passes_through_spine(tmp_path: Path):
    gov = _make_governor()
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    with patch(
        "src.executors.open_folder_executor.PRESET_FOLDERS",
        {"downloads": downloads},
    ), patch(
        "src.system_control.system_control_executor"
        ".SystemControlExecutor.open_path",
        return_value=True,
    ):
        result = gov.handle_governed_invocation(
            _CAPABILITY_ID,
            {"target": "downloads", "confirmed": True},
        )
    assert result.success is True


def test_missing_path_returns_failure():
    gov = _make_governor()
    result = gov.handle_governed_invocation(
        _CAPABILITY_ID,
        {
            "path": "/nonexistent/path/that/does/not/exist_cert22",
            "confirmed": True,
        },
    )
    assert result.success is False


# ---------------------------------------------------------------------------
# Ledger events
# ---------------------------------------------------------------------------

def test_spine_logs_action_attempted(tmp_path: Path):
    gov = _make_governor()
    logged: list[str] = []
    original = gov.ledger.log_event

    def _capture(event_type, payload):
        logged.append(event_type)
        return original(event_type, payload)

    gov.ledger.log_event = _capture
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    with patch(
        "src.executors.open_folder_executor.PRESET_FOLDERS",
        {"downloads": downloads},
    ), patch(
        "src.system_control.system_control_executor"
        ".SystemControlExecutor.open_path",
        return_value=True,
    ):
        gov.handle_governed_invocation(
            _CAPABILITY_ID,
            {"target": "downloads", "confirmed": True},
        )
    assert "ACTION_ATTEMPTED" in logged


# ---------------------------------------------------------------------------
# Governance fence
# ---------------------------------------------------------------------------

def test_unknown_capability_still_refused():
    gov = _make_governor()
    result = gov.handle_governed_invocation(9999, {})
    assert result.success is False
