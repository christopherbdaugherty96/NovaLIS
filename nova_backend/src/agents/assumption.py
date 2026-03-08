from __future__ import annotations

from typing import Any, Mapping

from src.agents._llm_agent import LLMBackedAgent


class AssumptionRiskAgent(LLMBackedAgent):
    name = "assumption"
    tier = 3
    purpose = "expose assumptions and failure risk"

    def build_prompt(self, query: str, context: Mapping[str, Any]) -> str:
        return (
            "Role: Assumption & Risk Agent\n"
            "Task: Expose load-bearing assumptions and failure modes only.\n"
            f"User Query: {query}\n"
            "Output sections: ASSUMPTIONS, RISK_REGISTER, FAILURE_MODES."
        )
