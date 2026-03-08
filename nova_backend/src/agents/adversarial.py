from __future__ import annotations

from typing import Any, Mapping

from src.agents._llm_agent import LLMBackedAgent


class AdversarialExternalizerAgent(LLMBackedAgent):
    name = "adversarial"
    tier = 3
    purpose = "prepare adversarial pressure points for external review"

    def build_prompt(self, query: str, context: Mapping[str, Any]) -> str:
        return (
            "Role: Adversarial Externalizer Agent\n"
            "Task: Produce external pressure points only; no internal resolution.\n"
            f"User Query: {query}\n"
            "Output sections: EXTERNAL_PRESSURE_POINTS, CROSS_MODEL_RISKS."
        )
