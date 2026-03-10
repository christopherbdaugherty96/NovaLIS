from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
from uuid import uuid4

from src.agents.base import AgentOutput, BaseAgent
from src.agents.context import AgentContextSnapshot
from src.build_phase import PHASE_4_2_ENABLED


@dataclass(frozen=True)
class AgentInvocationResult:
    invocation_id: str
    context_hash: str
    outputs: list[AgentOutput]


class AgentOrchestrator:
    """Deterministic non-authorizing orchestrator for Phase 4.2 agent surfaces."""

    @staticmethod
    def _serialize_outputs(outputs: list[AgentOutput]) -> list[dict[str, Any]]:
        serialized: list[dict[str, Any]] = []
        for item in outputs:
            serialized.append(
                {
                    "agent_name": item.agent_name,
                    "tier": item.tier,
                    "purpose": item.purpose,
                    "raw_text": item.raw_text,
                    "generated_at": item.generated_at,
                }
            )
        return serialized

    def run(self, query: str, agents: Iterable[BaseAgent], context_payload: dict) -> AgentInvocationResult:
        if not PHASE_4_2_ENABLED:
            raise RuntimeError("Phase 4.2 runtime is locked by build profile.")

        snapshot = AgentContextSnapshot.from_dict(context_payload or {})
        invocation_id = str(uuid4())
        ordered_agents = sorted(list(agents), key=lambda agent: (int(getattr(agent, "tier", 99)), str(getattr(agent, "name", ""))))

        outputs: list[AgentOutput] = []
        base_context = snapshot.to_plain_dict()
        for agent in ordered_agents:
            context_with_outputs = dict(base_context)
            context_with_outputs["agent_outputs"] = self._serialize_outputs(outputs)
            outputs.append(agent.execute(query, context_with_outputs, invocation_id, snapshot.context_hash))

        return AgentInvocationResult(
            invocation_id=invocation_id,
            context_hash=snapshot.context_hash,
            outputs=outputs,
        )