from __future__ import annotations


def test_orchestrator_passes_prior_outputs_to_later_agents():
    from src.agents.base import AgentOutput, BaseAgent
    from src.governor.agent_orchestrator import AgentOrchestrator

    class _CaptureAgent(BaseAgent):
        def __init__(self, name: str, tier: int, text: str) -> None:
            self.name = name
            self.tier = tier
            self.purpose = f"{name}-purpose"
            self._text = text
            self.seen_outputs = None

        def execute(self, query, context, invocation_id, context_hash):
            del query
            self.seen_outputs = list(context.get("agent_outputs") or [])
            return AgentOutput(
                agent_name=self.name,
                tier=self.tier,
                purpose=self.purpose,
                raw_text=self._text,
                invocation_id=invocation_id,
                context_hash=context_hash,
                generated_at=self._now_iso(),
            )

    orchestrator = AgentOrchestrator()
    first = _CaptureAgent(name="builder", tier=1, text="Builder draft")
    contradiction = _CaptureAgent(name="contradiction", tier=3, text="Contradiction list")

    result = orchestrator.run(
        "analyze this",
        [contradiction, first],
        {"session_id": "abc", "turn_count": 7},
    )

    assert len(result.outputs) == 2
    assert first.seen_outputs == []
    assert contradiction.seen_outputs is not None
    assert len(contradiction.seen_outputs) == 1
    prior = contradiction.seen_outputs[0]
    assert prior.get("agent_name") == "builder"
    assert prior.get("raw_text") == "Builder draft"


def test_contradiction_agent_prompt_includes_prior_outputs():
    from src.agents.contradiction import ContradictionAggregatorAgent

    agent = ContradictionAggregatorAgent()
    prompt = agent.build_prompt(
        "audit this",
        {
            "agent_outputs": [
                {"agent_name": "builder", "raw_text": "Initial draft statement."},
                {"agent_name": "memory", "raw_text": "Canonical memory warning."},
            ]
        },
    )
    assert "Prior Agent Outputs" in prompt
    assert "- builder:" in prompt
    assert "- memory:" in prompt