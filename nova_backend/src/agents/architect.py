from __future__ import annotations

from typing import Any, Mapping

from src.agents._llm_agent import LLMBackedAgent


class StructuralArchitectAgent(LLMBackedAgent):
    name = "architect"
    tier = 2
    purpose = "validate structure, shape, and boundary coherence"

    def build_prompt(self, query: str, context: Mapping[str, Any]) -> str:
        return (
            "Role: Structural Architect Agent\n"
            "Task: Evaluate structural coherence and boundary violations only.\n"
            f"User Query: {query}\n"
            "Output sections: STRUCTURAL_MAP, BOUNDARY_VIOLATIONS."
        )
