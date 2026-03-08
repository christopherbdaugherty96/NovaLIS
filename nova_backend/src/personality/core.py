from __future__ import annotations

from typing import Iterable

from src.agents.base import BaseAgent
from src.build_phase import PHASE_4_2_ENABLED
from src.governor.agent_orchestrator import AgentOrchestrator
from src.personality.announce import deep_mode_activation_notice
from src.personality.deep_mode import DeepModeState
from src.personality.presenter import present_raw_outputs
from src.personality.validate import PersonalityValidator


class PersonalityAgent:
    """Phase 4.2 facade for non-synthesizing raw output presentation."""

    def __init__(self) -> None:
        self._orchestrator = AgentOrchestrator()
        self._validator = PersonalityValidator()
        self._deep_mode = DeepModeState()

    def arm_deep_mode(self) -> str:
        self._deep_mode.activate_once()
        return deep_mode_activation_notice()

    def run(self, query: str, agents: Iterable[BaseAgent], context_payload: dict) -> str:
        if not PHASE_4_2_ENABLED:
            raise RuntimeError("Phase 4.2 runtime is locked by build profile.")

        result = self._orchestrator.run(query, agents, context_payload)
        presented = present_raw_outputs(result.outputs)
        raw_joined = "\n\n".join(output.raw_text for output in result.outputs)
        validation = self._validator.validate(raw_joined, presented)
        if not validation.ok:
            return f"Output blocked by {validation.stage}: {validation.reason}"

        if self._deep_mode.consume():
            return f"{deep_mode_activation_notice()}\n\n{presented}"
        return presented
