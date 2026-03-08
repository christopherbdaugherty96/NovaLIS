from __future__ import annotations

from typing import Any, Mapping

from src.agents._llm_agent import LLMBackedAgent


class BuilderAgent(LLMBackedAgent):
    name = "builder"
    tier = 1
    purpose = "create initial structure from ambiguous intent"

    def build_prompt(self, query: str, context: Mapping[str, Any]) -> str:
        return (
            "Role: Builder/Generator Agent\n"
            "Task: Convert ambiguity into a structured draft without recommendations.\n"
            f"User Query: {query}\n"
            f"Context Keys: {sorted(context.keys())}\n"
            "Output sections: PROPOSAL, DRAFT, STRUCTURE."
        )
