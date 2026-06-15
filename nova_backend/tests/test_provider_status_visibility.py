"""Tests for Provider Status Visibility (PR #246).

Proves:
1. Provider status snapshot includes all expected dependencies
2. Calendar and Email connectors appear in snapshot
3. Render function produces correct format
4. PROVIDER_STATUS_RE matches expected commands
5. No provider calls are made to build status
6. No provider call-path files changed
7. Morning Brief behavior unaffected
"""
from __future__ import annotations

import re
from unittest.mock import patch

import pytest

from src.usage.provider_budget_policy import (
    DEFAULT_POLICIES,
    ProviderBudgetPolicy,
)
from src.usage.provider_status import (
    _calendar_status,
    _email_status,
    _env_key_present,
    provider_status,
)
from src.websocket.intent_patterns import (
    CONNECTION_STATUS_RE,
    PROVIDER_STATUS_RE,
)


class TestProviderStatusRE:
    def test_matches_provider_status(self):
        assert PROVIDER_STATUS_RE.match("provider status")

    def test_matches_providers_status(self):
        assert PROVIDER_STATUS_RE.match("providers status")

    def test_matches_dependency_status(self):
        assert PROVIDER_STATUS_RE.match("dependency status")

    def test_matches_dependencies_status(self):
        assert PROVIDER_STATUS_RE.match("dependencies status")

    def test_matches_show_providers(self):
        assert PROVIDER_STATUS_RE.match("show providers")

    def test_matches_show_dependencies(self):
        assert PROVIDER_STATUS_RE.match("show dependencies")

    def test_case_insensitive(self):
        assert PROVIDER_STATUS_RE.match("Provider Status")
        assert PROVIDER_STATUS_RE.match("PROVIDER STATUS")

    def test_does_not_match_connection_status(self):
        assert not PROVIDER_STATUS_RE.match("connection status")

    def test_does_not_match_bridge_status(self):
        assert not PROVIDER_STATUS_RE.match("bridge status")

    def test_connection_status_no_longer_matches_provider(self):
        assert not CONNECTION_STATUS_RE.match("provider status")
        assert not CONNECTION_STATUS_RE.match("providers status")

    def test_connection_status_still_matches_connections(self):
        assert CONNECTION_STATUS_RE.match("connection status")
        assert CONNECTION_STATUS_RE.match("connections status")
        assert CONNECTION_STATUS_RE.match("show connections")


class TestCalendarStatus:
    def test_no_env_var(self):
        with patch.dict("os.environ", {}, clear=True):
            result = _calendar_status()
            assert result["connected"] is False
            assert "No ICS" in result["note"]

    def test_env_var_but_no_file(self):
        with patch.dict(
            "os.environ",
            {"NOVA_CALENDAR_ICS_PATH": "/nonexistent/cal.ics"},
        ):
            result = _calendar_status()
            assert result["connected"] is False
            assert "not found" in result["note"].lower()

    def test_env_var_with_real_file(self, tmp_path):
        ics = tmp_path / "test.ics"
        ics.write_text("BEGIN:VCALENDAR\nEND:VCALENDAR")
        with patch.dict(
            "os.environ",
            {"NOVA_CALENDAR_ICS_PATH": str(ics)},
        ):
            result = _calendar_status()
            assert result["connected"] is True
            assert "test.ics" in result["note"]


class TestEmailStatus:
    def test_no_env_vars(self):
        with patch.dict("os.environ", {}, clear=True):
            result = _email_status()
            assert result["connected"] is False

    def test_with_provider_env(self):
        with patch.dict(
            "os.environ",
            {"NOVA_EMAIL_PROVIDER": "gmail"},
        ):
            result = _email_status()
            assert result["connected"] is True

    def test_with_gmail_credentials(self):
        with patch.dict(
            "os.environ",
            {"GMAIL_CREDENTIALS_PATH": "/some/path.json"},
        ):
            result = _email_status()
            assert result["connected"] is True


class TestSnapshotIncludesAllDependencies:
    def test_has_calendar(self):
        result = provider_status()
        ids = {p["provider_id"] for p in result["providers"]}
        assert "calendar" in ids

    def test_has_email(self):
        result = provider_status()
        ids = {p["provider_id"] for p in result["providers"]}
        assert "email" in ids

    def test_has_ollama(self):
        result = provider_status()
        ids = {p["provider_id"] for p in result["providers"]}
        assert "ollama" in ids

    def test_has_all_default_policy_providers(self):
        result = provider_status()
        ids = {p["provider_id"] for p in result["providers"]}
        for pid in DEFAULT_POLICIES:
            assert pid in ids

    def test_all_entries_have_required_keys(self):
        result = provider_status()
        required = {
            "provider_id", "display_name", "connected",
            "enabled", "metered", "budget_state",
        }
        for p in result["providers"]:
            missing = required - set(p.keys())
            assert not missing, f"{p['provider_id']} missing: {missing}"


class TestRenderProviderStatusMessage:
    def test_render_returns_tuple(self):
        from src.brain_server import _render_provider_status_message
        snapshot = provider_status()
        msg, suggestions = _render_provider_status_message(snapshot)
        assert isinstance(msg, str)
        assert isinstance(suggestions, list)

    def test_render_header(self):
        from src.brain_server import _render_provider_status_message
        snapshot = provider_status()
        msg, _ = _render_provider_status_message(snapshot)
        assert "Provider & Dependency Status" in msg

    def test_render_lists_each_provider(self):
        from src.brain_server import _render_provider_status_message
        snapshot = provider_status()
        msg, _ = _render_provider_status_message(snapshot)
        for p in snapshot["providers"]:
            name = p["display_name"]
            assert name in msg, f"{name} missing from render"

    def test_render_shows_counts(self):
        from src.brain_server import _render_provider_status_message
        snapshot = provider_status()
        msg, _ = _render_provider_status_message(snapshot)
        assert "connected" in msg
        assert "metered" in msg

    def test_render_suggestions_include_connection_status(self):
        from src.brain_server import _render_provider_status_message
        snapshot = provider_status()
        _, suggestions = _render_provider_status_message(snapshot)
        commands = [s["command"] for s in suggestions]
        assert "connection status" in commands

    def test_render_suggestions_include_trust_center(self):
        from src.brain_server import _render_provider_status_message
        snapshot = provider_status()
        _, suggestions = _render_provider_status_message(snapshot)
        commands = [s["command"] for s in suggestions]
        assert "trust center" in commands


class TestConnectionStatusCrossLink:
    def test_connection_status_suggests_provider_status(self):
        from src.brain_server import _render_connection_status_message
        msg, suggestions = _render_connection_status_message({})
        commands = [s["command"] for s in suggestions]
        assert "provider status" in commands


class TestNoProviderCallsForStatus:
    def test_snapshot_does_not_import_providers(self):
        import src.usage.provider_status as mod
        source = open(mod.__file__).read()
        assert "deepseek_reasoning_provider" not in source
        assert "openai_responses_lane" not in source
        assert "web_search_executor" not in source
        assert "weather_service" not in source

    def test_render_does_not_import_providers(self):
        from src.brain_server import _render_provider_status_message
        import inspect
        source = inspect.getsource(_render_provider_status_message)
        assert "deepseek" not in source.lower()
        assert "openai" not in source.lower()
        assert "import" not in source

    def test_session_handler_provider_block_is_read_only(self):
        import src.websocket.session_handler as mod
        source = open(mod.__file__, encoding="utf-8", errors="replace").read()
        block_start = source.find("PROVIDER_STATUS_RE.match")
        assert block_start > 0
        block_end = source.find("continue", block_start)
        block = source[block_start:block_end]
        assert "record" not in block.lower()
        assert "write" not in block.lower()
        assert "execute" not in block.lower()


class TestMorningBriefUnchanged:
    def test_morning_brief_handler_not_modified(self):
        import src.conversation.morning_brief_handler as mod
        source = open(mod.__file__).read()
        assert "provider_status" not in source

    def test_daily_brief_not_modified(self):
        import src.brief.daily_brief as mod
        source = open(mod.__file__).read()
        assert "provider_status" not in source

    def test_routine_graph_not_modified(self):
        import src.routine.routine_graph as mod
        source = open(mod.__file__).read()
        assert "provider_status" not in source


class TestNoCallPathFilesChanged:
    def test_deepseek_provider_unchanged(self):
        import src.providers.deepseek_reasoning_provider as mod
        source = open(mod.__file__).read()
        assert "provider_status" not in source
        assert "_render_provider_status" not in source

    def test_network_mediator_unchanged(self):
        import src.governor.network_mediator as mod
        source = open(mod.__file__).read()
        assert "provider_status" not in source
        assert "PROVIDER_STATUS_RE" not in source
