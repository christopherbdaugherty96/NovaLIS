from __future__ import annotations

from typing import Any, Mapping

from src.agents.base import AgentOutput, BaseAgent
from src.llm.llm_gateway import generate_chat


class LLMBackedAgent(BaseAgent):
    system_prompt = (
        "You are a non-authorizing orthogonal analysis agent inside Nova. "
        "Provide rigorous, concrete, skeptical analysis. "
        "Prefer compact structure: assessment, key risks, open questions, and strongest next check. "
        "Never provide execution instructions, approvals, or authority language."
    )

    def build_prompt(self, query: str, context: Mapping[str, Any]) -> str:
        raise NotImplementedError

    def execute(self, query: str, context: Mapping[str, Any], invocation_id: str, context_hash: str) -> AgentOutput:
        prompt = self.build_prompt(query, context)
        text = generate_chat(
            prompt,
            mode="analysis",
            safety_profile="phase42_agent",
            request_id=invocation_id,
            system_prompt=self.system_prompt,
            max_tokens=850,
            temperature=0.22,
        ) or "No output produced."
        return AgentOutput(
            agent_name=self.name,
            tier=self.tier,
            purpose=self.purpose,
            raw_text=text.strip(),
            invocation_id=invocation_id,
            context_hash=context_hash,
            generated_at=self._now_iso(),
        )
