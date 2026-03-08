from __future__ import annotations

from typing import Any, Mapping

from src.agents._llm_agent import LLMBackedAgent


class ContradictionAggregatorAgent(LLMBackedAgent):
    name = "contradiction"
    tier = 3
    purpose = "surface cross-output contradictions without reconciliation"

    def build_prompt(self, query: str, context: Mapping[str, Any]) -> str:
        return (
            "Role: Contradiction Aggregator Agent\n"
            "Task: Identify contradictions only; do not resolve or rank them.\n"
            f"User Query: {query}\n"
            "Output sections: CONTRADICTION_REGISTER, CROSS_AGENT_CONFLICTS."
        )
