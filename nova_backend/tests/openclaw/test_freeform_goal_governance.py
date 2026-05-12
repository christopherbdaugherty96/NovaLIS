"""Governance tests for the OpenClaw freeform goal execution path.

PATCH A: Confirms that run_goal() constructs ThinkingLoop with a filtered
registry that excludes mutation-capable tools (volume, brightness, media,
open_webpage) and the screen_capture tool.  The LLM therefore cannot select
or execute those tools regardless of goal content.

PATCH C: Confirms that ThinkingLoop receives a MeteredNetworkProxy rather
than a raw NetworkMediator, so network calls are budget-bounded.

PATCH D: Confirms that screen_capture is excluded by the allowlist (not by
the accidental param-extractor gap documented in PASS4 audit).

Source: docs/audits/PASS4_OPENCLAW_FREEFORM_GOAL_INSPECTION_2026-05-11.md
        docs/audits/PATCH_ROADMAP_2026-05-11.md — PATCH A, C, D
"""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.openclaw.agent_runner import (
    MeteredNetworkProxy,
    OpenClawAgentRunner,
    _FREEFORM_GOAL_ALLOWED_TOOLS,
    _FREEFORM_GOAL_MAX_NETWORK_CALLS,
)
from src.openclaw.thinking_loop import ThinkingLoop
from src.openclaw.tool_registry import ToolMetadata, ToolRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_runner() -> OpenClawAgentRunner:
    """Return a runner with mocked store and no real network."""
    store = MagicMock()
    store.set_active_run = MagicMock()
    store.update_active_run = MagicMock()
    store.finish_active_run = MagicMock()
    store.record_run = MagicMock(return_value={"envelope_id": "test"})
    store.is_cancel_requested = MagicMock(return_value=False)
    return OpenClawAgentRunner(store=store, network=None)


_THINKING_LOOP_SUCCESS: dict[str, Any] = {
    "success": True,
    "steps": 1,
    "thoughts": [],
    "synthesis": "Done.",
    "total_duration_seconds": 0.1,
}

# ---------------------------------------------------------------------------
# PATCH A — allowlist enforcement tests
# ---------------------------------------------------------------------------

class TestAllowlistConstant:
    """The frozenset itself must be correct and complete."""

    def test_allowed_tools_is_frozenset(self):
        assert isinstance(_FREEFORM_GOAL_ALLOWED_TOOLS, frozenset)

    def test_allowed_tools_contains_expected_read_only_tools(self):
        # All three read-only network tools must be present.
        assert "weather" in _FREEFORM_GOAL_ALLOWED_TOOLS
        assert "news" in _FREEFORM_GOAL_ALLOWED_TOOLS
        assert "web_search" in _FREEFORM_GOAL_ALLOWED_TOOLS

    def test_mutation_tools_not_in_allowlist(self):
        # PATCH A + D: these must never appear in the frozenset.
        for tool in ("volume", "brightness", "media", "open_webpage", "screen_capture"):
            assert tool not in _FREEFORM_GOAL_ALLOWED_TOOLS, (
                f"Mutation/sensitive tool '{tool}' must NOT be in "
                "_FREEFORM_GOAL_ALLOWED_TOOLS"
            )

    def test_all_allowlisted_tools_are_registered(self):
        """ToolRegistry.filtered() raises ValueError for unknown names.
        This test validates that every name in the allowlist exists in the
        real singleton registry — catching allowlist typos at test time.
        """
        from src.openclaw.tool_registry import get_tool_registry
        registry = get_tool_registry()
        # Should not raise — all names must be registered.
        filtered = registry.filtered(allowed=_FREEFORM_GOAL_ALLOWED_TOOLS)
        assert set(filtered.tool_names) == _FREEFORM_GOAL_ALLOWED_TOOLS


class TestRunGoalReceivesFilteredRegistry:
    """run_goal() must pass a filtered registry to ThinkingLoop."""

    @pytest.mark.asyncio
    async def test_thinking_loop_registry_excludes_mutation_tools(self):
        """ThinkingLoop is constructed with a registry that has no mutation tools."""
        runner = _make_runner()
        captured: dict[str, Any] = {}

        original_init = ThinkingLoop.__init__

        def spy_init(self, *, registry, **kwargs):
            captured["registry"] = registry
            original_init(self, registry=registry, **kwargs)

        with patch.object(ThinkingLoop, "__init__", spy_init):
            with patch.object(
                ThinkingLoop, "run", new_callable=AsyncMock,
                return_value=_THINKING_LOOP_SUCCESS,
            ):
                await runner.run_goal("check the weather")

        assert "registry" in captured, "ThinkingLoop.__init__ spy was never called"
        registry: ToolRegistry = captured["registry"]
        tool_names = set(registry.tool_names)

        # Mutation-capable tools must be absent from the registry the LLM sees.
        for excluded in ("volume", "brightness", "media", "open_webpage"):
            assert excluded not in tool_names, (
                f"PATCH A FAILURE: mutation tool '{excluded}' is visible to "
                "ThinkingLoop — it must be excluded by the filtered registry"
            )

    @pytest.mark.asyncio
    async def test_thinking_loop_registry_excludes_screen_capture(self):
        """PATCH D: screen_capture excluded by allowlist, not param-extractor gap."""
        runner = _make_runner()
        captured: dict[str, Any] = {}

        original_init = ThinkingLoop.__init__

        def spy_init(self, *, registry, **kwargs):
            captured["registry"] = registry
            original_init(self, registry=registry, **kwargs)

        with patch.object(ThinkingLoop, "__init__", spy_init):
            with patch.object(
                ThinkingLoop, "run", new_callable=AsyncMock,
                return_value=_THINKING_LOOP_SUCCESS,
            ):
                await runner.run_goal("take a screenshot")

        registry: ToolRegistry = captured["registry"]
        assert "screen_capture" not in set(registry.tool_names), (
            "PATCH D FAILURE: screen_capture must be excluded by the allowlist, "
            "not by the accidental param-extractor gap"
        )

    @pytest.mark.asyncio
    async def test_thinking_loop_registry_contains_allowed_tools(self):
        """Allowlisted tools must still be available to ThinkingLoop."""
        runner = _make_runner()
        captured: dict[str, Any] = {}

        original_init = ThinkingLoop.__init__

        def spy_init(self, *, registry, **kwargs):
            captured["registry"] = registry
            original_init(self, registry=registry, **kwargs)

        with patch.object(ThinkingLoop, "__init__", spy_init):
            with patch.object(
                ThinkingLoop, "run", new_callable=AsyncMock,
                return_value=_THINKING_LOOP_SUCCESS,
            ):
                await runner.run_goal("what is the weather in Seattle?")

        registry: ToolRegistry = captured["registry"]
        tool_names = set(registry.tool_names)

        for allowed in _FREEFORM_GOAL_ALLOWED_TOOLS:
            assert allowed in tool_names, (
                f"PATCH A regression: allowed tool '{allowed}' is missing from "
                "the filtered registry passed to ThinkingLoop"
            )

    @pytest.mark.asyncio
    async def test_thinking_loop_registry_is_exact_allowlist(self):
        """Filtered registry must contain exactly the allowlisted tools — no extras."""
        runner = _make_runner()
        captured: dict[str, Any] = {}

        original_init = ThinkingLoop.__init__

        def spy_init(self, *, registry, **kwargs):
            captured["registry"] = registry
            original_init(self, registry=registry, **kwargs)

        with patch.object(ThinkingLoop, "__init__", spy_init):
            with patch.object(
                ThinkingLoop, "run", new_callable=AsyncMock,
                return_value=_THINKING_LOOP_SUCCESS,
            ):
                await runner.run_goal("find some news")

        registry: ToolRegistry = captured["registry"]
        assert set(registry.tool_names) == _FREEFORM_GOAL_ALLOWED_TOOLS, (
            "Filtered registry tool set does not exactly match "
            "_FREEFORM_GOAL_ALLOWED_TOOLS"
        )


# ---------------------------------------------------------------------------
# PATCH C — MeteredNetworkProxy enforcement tests
# ---------------------------------------------------------------------------

class TestRunGoalReceivesMeteredNetwork:
    """run_goal() must wrap self._network in MeteredNetworkProxy."""

    @pytest.mark.asyncio
    async def test_thinking_loop_network_is_metered_proxy(self):
        """ThinkingLoop.network must be a MeteredNetworkProxy, not the raw network."""
        runner = _make_runner()
        captured: dict[str, Any] = {}

        original_init = ThinkingLoop.__init__

        def spy_init(self, *, network, **kwargs):
            captured["network"] = network
            original_init(self, network=network, **kwargs)

        with patch.object(ThinkingLoop, "__init__", spy_init):
            with patch.object(
                ThinkingLoop, "run", new_callable=AsyncMock,
                return_value=_THINKING_LOOP_SUCCESS,
            ):
                await runner.run_goal("check the weather")

        assert "network" in captured, "ThinkingLoop.__init__ spy was never called"
        assert isinstance(captured["network"], MeteredNetworkProxy), (
            "PATCH C FAILURE: ThinkingLoop received a raw network object instead "
            "of MeteredNetworkProxy — network calls are not budget-bounded"
        )

    def test_freeform_goal_max_network_calls_is_positive_int(self):
        assert isinstance(_FREEFORM_GOAL_MAX_NETWORK_CALLS, int)
        assert _FREEFORM_GOAL_MAX_NETWORK_CALLS > 0, (
            "_FREEFORM_GOAL_MAX_NETWORK_CALLS must be a positive integer"
        )

    def test_freeform_goal_max_network_calls_is_conservative(self):
        """Budget must be conservative (≤ 10) for the freeform goal path."""
        assert _FREEFORM_GOAL_MAX_NETWORK_CALLS <= 10, (
            "_FREEFORM_GOAL_MAX_NETWORK_CALLS should be conservative (≤ 10) "
            f"for the freeform goal path; got {_FREEFORM_GOAL_MAX_NETWORK_CALLS}"
        )


# ---------------------------------------------------------------------------
# ToolRegistry.filtered() unit tests (PATCH A implementation)
# ---------------------------------------------------------------------------

class TestToolRegistryFiltered:
    """Unit tests for the ToolRegistry.filtered() method itself."""

    def _make_registry(self) -> ToolRegistry:
        """Return a small registry with one read-only and one mutation tool."""
        reg = ToolRegistry()
        reg.register(
            "read_tool",
            lambda: "read_instance",
            ToolMetadata(name="read_tool", description="reads stuff", category="collection"),
        )
        reg.register(
            "mutate_tool",
            lambda: "mutate_instance",
            ToolMetadata(name="mutate_tool", description="mutates stuff", category="mutation"),
        )
        return reg

    def test_filtered_returns_subset(self):
        reg = self._make_registry()
        view = reg.filtered(allowed=frozenset({"read_tool"}))
        assert set(view.tool_names) == {"read_tool"}

    def test_filtered_excludes_tools_not_in_allowlist(self):
        reg = self._make_registry()
        view = reg.filtered(allowed=frozenset({"read_tool"}))
        assert not view.has("mutate_tool")

    def test_filtered_preserves_metadata(self):
        reg = self._make_registry()
        view = reg.filtered(allowed=frozenset({"read_tool"}))
        meta = view.get_metadata("read_tool")
        assert meta.description == "reads stuff"
        assert meta.category == "collection"

    def test_filtered_can_create_tool_instances(self):
        reg = self._make_registry()
        view = reg.filtered(allowed=frozenset({"read_tool"}))
        assert view.create("read_tool") == "read_instance"

    def test_filtered_raises_on_unknown_name(self):
        reg = self._make_registry()
        with pytest.raises(ValueError, match="unregistered"):
            reg.filtered(allowed=frozenset({"nonexistent_tool"}))

    def test_filtered_with_empty_allowlist_returns_empty_registry(self):
        reg = self._make_registry()
        view = reg.filtered(allowed=frozenset())
        assert view.tool_names == []

    def test_filtered_does_not_mutate_original(self):
        reg = self._make_registry()
        view = reg.filtered(allowed=frozenset({"read_tool"}))
        # Original registry still has both tools.
        assert reg.has("read_tool")
        assert reg.has("mutate_tool")
        # View is independent.
        assert not view.has("mutate_tool")

    def test_filtered_partial_allowlist_mix(self):
        reg = self._make_registry()
        # Allowlist includes only one of two tools.
        view = reg.filtered(allowed=frozenset({"mutate_tool"}))
        assert set(view.tool_names) == {"mutate_tool"}
        assert not view.has("read_tool")

    def test_filtered_categories_are_correct(self):
        reg = self._make_registry()
        view = reg.filtered(allowed=frozenset({"read_tool"}))
        assert view.find_by_category("collection") == ["read_tool"]
        assert view.find_by_category("mutation") == []


# ---------------------------------------------------------------------------
# RunBudgetMeter.record_network_call() — URL-gating behaviour (PATCH C fix)
#
# url_allowed() returns False when allowed_hostnames=[] because
# TaskEnvelope.hostname_allowed() uses `any(...)` over an empty list.
# RunBudgetMeter must treat an empty hostnames list as "any host allowed"
# rather than "all hosts blocked", so that the freeform goal path's
# MeteredNetworkProxy can count calls without blocking legitimate tool
# network requests that are already SSRF-protected by NetworkMediator.
# ---------------------------------------------------------------------------

class TestRunBudgetMeterNetworkGating:
    """RunBudgetMeter.record_network_call() URL-gating corner cases."""

    def _make_budget_meter(self, allowed_hostnames: list[str], max_calls: int = 5):
        from src.openclaw.agent_runner import RunBudgetMeter
        from src.openclaw.task_envelope import TaskEnvelope

        env = TaskEnvelope(
            id="test-budget",
            title="test",
            template_id="test",
            tools_allowed=[],
            allowed_hostnames=allowed_hostnames,
            max_steps=10,
            max_duration_s=120,
            max_network_calls=max_calls,
            max_files_touched=0,
            max_bytes_read=524_288,
            max_bytes_written=0,
            triggered_by="test",
        )
        return RunBudgetMeter(env)

    def test_empty_hostnames_allows_any_url(self):
        """PATCH C fix: empty allowed_hostnames must not block network calls.

        url_allowed() returns False when allowed_hostnames=[].  The budget meter
        must skip URL gating in this case so that freeform goal network tools
        (weather, news, web_search) can make calls without being blocked.
        SSRF protection is delegated to NetworkMediator in the goal path.
        """
        meter = self._make_budget_meter(allowed_hostnames=[])
        # Must not raise — any URL is allowed when hostnames list is empty.
        meter.record_network_call("https://api.weather.example.com/current")
        meter.record_network_call("https://feeds.news.example.com/rss")
        meter.record_network_call("https://search.brave.com/api/v1/search")
        assert meter.network_calls_used == 3

    def test_explicit_hostnames_blocks_unallowed_url(self):
        """When allowed_hostnames is set, urls outside it must be blocked."""
        meter = self._make_budget_meter(allowed_hostnames=["api.weather.example.com"])
        # Allowed host — must pass.
        meter.record_network_call("https://api.weather.example.com/current")
        assert meter.network_calls_used == 1
        # Unallowed host — must raise.
        with pytest.raises(RuntimeError, match="outside the envelope"):
            meter.record_network_call("https://malicious.example.com/steal")

    def test_budget_cap_enforced_regardless_of_hostname_policy(self):
        """Call-count cap must be enforced even when URL gating is skipped."""
        meter = self._make_budget_meter(allowed_hostnames=[], max_calls=2)
        meter.record_network_call("https://example.com/a")
        meter.record_network_call("https://example.com/b")
        with pytest.raises(RuntimeError, match="budget"):
            meter.record_network_call("https://example.com/c")  # 3 > max_calls=2

    def test_explicit_hostnames_cap_also_enforced(self):
        """Call-count cap is still enforced when hostname filtering is active."""
        meter = self._make_budget_meter(
            allowed_hostnames=["example.com"], max_calls=1
        )
        meter.record_network_call("https://example.com/first")
        with pytest.raises(RuntimeError, match="budget"):
            meter.record_network_call("https://example.com/second")
