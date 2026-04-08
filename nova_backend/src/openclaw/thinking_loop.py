"""Multi-step agent thinking loop for OpenClaw.

The LLM iteratively reasons about a goal, selects tools, executes them,
evaluates results, and decides whether to continue or stop.

Design constraints (from codebase audit):
  - llm_gateway.generate_chat() is SYNCHRONOUS — all calls wrapped
    in asyncio.to_thread() to avoid blocking the event loop.
  - mode/safety_profile params are ignored by the gateway — use "general".
  - Execution is bounded: max 10 steps with phase-based cost reduction.
  - On failure, falls back to deterministic briefing (caller handles this).
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from src.llm import llm_gateway
from src.openclaw.execution_memory import ExecutionMemory
from src.openclaw.robust_executor import RobustExecutor
from src.openclaw.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class StepPhase(Enum):
    """Execution phases with decreasing LLM cost."""
    EXPLORATION = "exploration"      # Steps 1-4: full LLM checks
    REFINEMENT = "refinement"        # Steps 5-7: LLM every other step
    FINALIZATION = "finalization"    # Steps 8-10: heuristic only


@dataclass
class ThoughtStep:
    """Record of a single step in the thinking loop."""
    step: int
    phase: StepPhase
    reasoning: str
    selected_tools: list[str]
    parameters: dict[str, dict[str, Any]]
    results: dict[str, Any] = field(default_factory=dict)
    success: bool = False
    duration_seconds: float = 0.0


# ------------------------------------------------------------------
# Parameter templates — fallback when LLM JSON parsing fails
# ------------------------------------------------------------------

TOOL_PARAMETER_DEFAULTS: dict[str, dict[str, Any]] = {
    "weather": {"location": "auto"},
    "calendar": {"days_ahead": 1},
    "news": {"category": "general", "limit": 5},
}


class ThinkingLoop:
    """Iterative LLM-guided agent loop with bounded execution."""

    MAX_STEPS = 10

    def __init__(
        self,
        *,
        registry: ToolRegistry,
        executor: RobustExecutor,
        network: Any = None,
        execution_memory: ExecutionMemory | None = None,
    ) -> None:
        self._registry = registry
        self._executor = executor
        self._network = network
        self._execution_memory = execution_memory
        self._on_progress: Callable[[int, str, list[str]], None] | None = None
        self.thoughts: list[ThoughtStep] = []

    def set_progress_callback(
        self,
        callback: Callable[[int, str, list[str]], None],
    ) -> None:
        """Set a callback invoked after each step: (step_num, status, tools)."""
        self._on_progress = callback

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def run(self, goal: str) -> dict[str, Any]:
        """Run the thinking loop to completion. Returns full execution record."""
        context: dict[str, Any] = {"goal": goal, "history": []}
        failed_tools: set[str] = set()
        t0 = time.monotonic()

        for step_num in range(1, self.MAX_STEPS + 1):
            phase = self._phase_for(step_num)

            # 1. Reason about next action
            reasoning = await self._reason(goal, context)
            if not reasoning:
                logger.warning("LLM returned empty reasoning at step %d", step_num)
                break

            # 2. Select tools (excluding those that already failed)
            tools = await self._select_tools(reasoning, failed_tools=failed_tools)
            if not tools:
                logger.info("No tools selected at step %d — terminating", step_num)
                break

            # 2b. Sort tools by historical reliability/speed
            if self._execution_memory is not None:
                tools = self._execution_memory.optimal_order(tools, task_type="goal")

            # 3. Extract parameters (with template fallback)
            parameters: dict[str, dict[str, Any]] = {}
            for tool_name in tools:
                try:
                    parameters[tool_name] = await self._extract_params(tool_name, goal)
                except Exception as exc:
                    logger.warning("Param extraction failed for '%s': %s", tool_name, exc)
                    parameters[tool_name] = dict(TOOL_PARAMETER_DEFAULTS.get(tool_name, {}))

            # 4. Execute tools
            step_t0 = time.monotonic()
            results: dict[str, Any] = {}
            for tool_name, params in parameters.items():
                if not self._registry.has(tool_name):
                    logger.warning("Tool '%s' not in registry, skipping", tool_name)
                    results[tool_name] = {"error": "not_registered"}
                    continue

                meta = self._registry.get_metadata(tool_name)
                kwargs = {"network": self._network} if meta.is_network_tool else {}
                skill = self._registry.create(tool_name, **kwargs)
                timeout = meta.timeout_seconds
                result = await self._executor.call_skill(
                    skill, params.get("query", tool_name),
                    timeout_seconds=timeout,
                    tool_name=tool_name,
                )
                results[tool_name] = result

            step_duration = time.monotonic() - step_t0

            thought = ThoughtStep(
                step=step_num,
                phase=phase,
                reasoning=reasoning,
                selected_tools=tools,
                parameters=parameters,
                results=results,
                success=any(
                    r is not None and not (isinstance(r, dict) and r.get("error"))
                    for r in results.values()
                ),
                duration_seconds=round(step_duration, 3),
            )
            self.thoughts.append(thought)

            # Track tools that failed so we don't re-select them
            for tool_name, r in results.items():
                if r is None or (isinstance(r, dict) and r.get("error")):
                    failed_tools.add(tool_name)

            context["history"].append({
                "step": step_num,
                "tools": tools,
                "success": thought.success,
                "result_keys": list(results.keys()),
            })

            # 4b. Notify progress listener
            if self._on_progress is not None:
                try:
                    status = "success" if thought.success else "partial"
                    self._on_progress(step_num, status, tools)
                except Exception as exc:
                    logger.warning("Progress callback error: %s", exc)
                    # If callback raises RunCancelledError, propagate it
                    if "cancel" in type(exc).__name__.lower():
                        raise

            # 5. Check termination
            should_stop = await self._should_terminate(goal, context, phase, step_num)
            if should_stop:
                logger.info("Goal achieved at step %d", step_num)
                break

        # Synthesize a coherent answer from tool results via LLM
        synthesis = await self._synthesize(goal)

        total_duration = time.monotonic() - t0
        return {
            "goal": goal,
            "steps": len(self.thoughts),
            "thoughts": self.thoughts,
            "synthesis": synthesis,
            "total_duration_seconds": round(total_duration, 3),
            "success": any(t.success for t in self.thoughts),
        }

    # ------------------------------------------------------------------
    # LLM interactions (all wrapped in asyncio.to_thread)
    # ------------------------------------------------------------------

    async def _reason(self, goal: str, context: dict[str, Any]) -> str:
        history = context.get("history", [])
        history_text = json.dumps(history[-3:], indent=2) if history else "None yet"

        prompt = (
            f"You are Nova's agent planning the next step to achieve a goal.\n\n"
            f"Goal: {goal}\n\n"
            f"Steps taken so far:\n{history_text}\n\n"
            f"Available tools: {', '.join(self._registry.tool_names)}\n\n"
            f"What should be done next? Be concise (1-2 sentences)."
        )

        result = await asyncio.to_thread(
            llm_gateway.generate_chat,
            prompt,
            mode="general",
            safety_profile="default",
            request_id=f"agent_reason_{len(self.thoughts) + 1}",
            max_tokens=150,
            temperature=0.3,
        )
        return str(result or "").strip()

    async def _select_tools(
        self, reasoning: str, *, failed_tools: set[str] | None = None,
    ) -> list[str]:
        available = [
            t for t in self._registry.tool_names
            if t not in (failed_tools or set())
        ]
        if not available:
            return []

        avoid_note = ""
        if failed_tools:
            avoid_note = f"\nDo NOT select these (they already failed): {', '.join(sorted(failed_tools))}\n"

        prompt = (
            f"Based on this reasoning:\n{reasoning}\n\n"
            f"Which tools should run next? Available: {', '.join(available)}\n"
            f"{avoid_note}\n"
            f"Respond with ONLY a JSON array of tool names. Example: [\"weather\", \"calendar\"]"
        )

        result = await asyncio.to_thread(
            llm_gateway.generate_chat,
            prompt,
            mode="general",
            safety_profile="default",
            request_id=f"agent_select_{len(self.thoughts) + 1}",
            max_tokens=100,
            temperature=0.1,
        )

        return self._parse_tool_list(str(result or ""), available)

    async def _extract_params(self, tool_name: str, goal: str) -> dict[str, Any]:
        """Try LLM param extraction, fall back to templates."""
        meta = self._registry.get_metadata(tool_name) if self._registry.has(tool_name) else None
        desc = meta.description if meta else tool_name

        prompt = (
            f"Tool: {tool_name} — {desc}\n"
            f"Goal: {goal}\n\n"
            f"What parameters? Respond with ONLY a JSON object. "
            f"Example: {{\"location\": \"NYC\"}}"
        )

        result = await asyncio.to_thread(
            llm_gateway.generate_chat,
            prompt,
            mode="general",
            safety_profile="default",
            request_id=f"agent_params_{tool_name}_{len(self.thoughts) + 1}",
            max_tokens=80,
            temperature=0.1,
        )

        parsed = self._parse_json_object(str(result or ""))
        if parsed:
            return parsed

        # Fall back to defaults
        return dict(TOOL_PARAMETER_DEFAULTS.get(tool_name, {}))

    async def _should_terminate(
        self,
        goal: str,
        context: dict[str, Any],
        phase: StepPhase,
        step_num: int,
    ) -> bool:
        """Phase-based termination: full LLM early, heuristic late."""

        # Finalization phase: heuristic only (no LLM cost)
        if phase == StepPhase.FINALIZATION:
            return self._heuristic_done(context)

        # Refinement phase: LLM every other step
        if phase == StepPhase.REFINEMENT and step_num % 2 == 0:
            return self._heuristic_done(context)

        # Exploration phase: full LLM check
        last_step = context["history"][-1] if context["history"] else {}
        prompt = (
            f"Goal: {goal}\n\n"
            f"Last step result: {json.dumps(last_step, indent=2)}\n\n"
            f"Has the goal been achieved? Respond with ONLY \"yes\" or \"no\"."
        )

        result = await asyncio.to_thread(
            llm_gateway.generate_chat,
            prompt,
            mode="general",
            safety_profile="default",
            request_id=f"agent_term_{step_num}",
            max_tokens=10,
            temperature=0.0,
        )

        return "yes" in str(result or "").lower()

    async def _synthesize(self, goal: str) -> str:
        """Use the LLM to produce a coherent answer from collected tool results."""
        if not self.thoughts:
            return f"I wasn't able to make progress on: {goal}"

        # Collect tool results into a compact text block
        evidence: list[str] = []
        for thought in self.thoughts:
            for tool_name, tool_result in thought.results.items():
                if tool_result is None:
                    continue
                if isinstance(tool_result, dict) and tool_result.get("error"):
                    continue
                msg = getattr(tool_result, "message", None)
                data = getattr(tool_result, "data", None)
                if msg:
                    evidence.append(f"[{tool_name}] {str(msg).strip()}")
                elif data:
                    evidence.append(f"[{tool_name}] {json.dumps(data, default=str)[:500]}")

        if not evidence:
            if any(t.success for t in self.thoughts):
                return f"Completed goal: {goal}"
            return f"Attempted but could not fully complete: {goal}"

        evidence_text = "\n".join(evidence[:10])  # cap to avoid token bloat

        prompt = (
            f"You are Nova, a personal AI assistant. "
            f"The user asked: \"{goal}\"\n\n"
            f"Here are the results from the tools you used:\n{evidence_text}\n\n"
            f"Write a concise, helpful answer (2-4 sentences) that directly "
            f"addresses the user's goal. Do not mention tool names or internal details."
        )

        try:
            result = await asyncio.to_thread(
                llm_gateway.generate_chat,
                prompt,
                mode="general",
                safety_profile="default",
                request_id="agent_synthesize",
                max_tokens=200,
                temperature=0.3,
            )
            synthesis = str(result or "").strip()
            if synthesis:
                return synthesis
        except Exception as exc:
            logger.warning("LLM synthesis failed, falling back to static: %s", exc)

        # Fallback: join the evidence messages
        return " ".join(msg.split("] ", 1)[-1] for msg in evidence[:3])

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _phase_for(step: int) -> StepPhase:
        if step <= 4:
            return StepPhase.EXPLORATION
        if step <= 7:
            return StepPhase.REFINEMENT
        return StepPhase.FINALIZATION

    @staticmethod
    def _heuristic_done(context: dict[str, Any]) -> bool:
        """Simple check: stop if the last step succeeded."""
        history = context.get("history", [])
        if not history:
            return False
        return bool(history[-1].get("success"))

    @staticmethod
    def _parse_tool_list(text: str, available: list[str]) -> list[str]:
        """Extract a JSON array of tool names from LLM output."""
        try:
            start = text.find("[")
            end = text.rfind("]") + 1
            if start >= 0 and end > start:
                parsed = json.loads(text[start:end])
                if isinstance(parsed, list):
                    return [t for t in parsed if isinstance(t, str) and t in available]
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback: look for known tool names in the text
        return [t for t in available if t in text.lower()]

    @staticmethod
    def _parse_json_object(text: str) -> dict[str, Any] | None:
        """Extract a JSON object from LLM output."""
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                parsed = json.loads(text[start:end])
                if isinstance(parsed, dict):
                    return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        return None
