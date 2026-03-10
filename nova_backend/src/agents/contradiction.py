from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from src.agents._llm_agent import LLMBackedAgent


class ContradictionAggregatorAgent(LLMBackedAgent):
    name = "contradiction"
    tier = 3
    purpose = "surface cross-output contradictions without reconciliation"

    def build_prompt(self, query: str, context: Mapping[str, Any]) -> str:
        prior_outputs = context.get("agent_outputs") or []
        lines = []
        if isinstance(prior_outputs, list):
            for item in prior_outputs[:8]:
                if not isinstance(item, Mapping):
                    continue
                agent_name = str(item.get("agent_name") or "unknown").strip()
                raw_text = str(item.get("raw_text") or "").strip()
                excerpt = raw_text[:450]
                if len(raw_text) > 450:
                    excerpt += "..."
                lines.append(f"- {agent_name}: {excerpt}")

        source_block = "\n".join(lines) if lines else "- No prior agent outputs available."

        return (
            "Role: Contradiction Aggregator Agent\n"
            "Task: Identify contradictions across prior agent outputs only; do not resolve or rank them.\n"
            f"User Query: {query}\n"
            "Prior Agent Outputs:\n"
            f"{source_block}\n"
            "Output sections: CONTRADICTION_REGISTER, CROSS_AGENT_CONFLICTS."
        )
