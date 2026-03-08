from __future__ import annotations

from typing import Any, Mapping

from src.agents._llm_agent import LLMBackedAgent


class DeepAuditAgent(LLMBackedAgent):
    name = "deep_audit"
    tier = 2
    purpose = "perform comprehensive scrutiny and surface violations"

    def build_prompt(self, query: str, context: Mapping[str, Any]) -> str:
        return (
            "Role: Deep Audit Agent\n"
            "Task: Produce findings only; do not propose fixes.\n"
            f"User Query: {query}\n"
            "Output sections: FINDINGS, VIOLATIONS, OPEN_QUESTIONS."
        )
