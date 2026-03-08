from __future__ import annotations

from typing import Any, Mapping

from src.agents._llm_agent import LLMBackedAgent


class MemoryAgent(LLMBackedAgent):
    name = "memory"
    tier = 2
    purpose = "surface canonical status and duplication warnings"

    def build_prompt(self, query: str, context: Mapping[str, Any]) -> str:
        return (
            "Role: Memory Agent\n"
            "Task: Report memory/canon state and duplication risk.\n"
            f"User Query: {query}\n"
            "Output sections: MEMORY_MAP, CANON_STATUS, DUPLICATION_WARNINGS."
        )
