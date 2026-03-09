from src.agents.base import AgentOutput, BaseAgent
from src.build_phase import BUILD_PHASE, PHASE_4_2_ENABLED
from src.personality.core import PersonalityAgent


class _StaticAgent(BaseAgent):
    name = "static"
    tier = 1
    purpose = "unit-test static output"

    def execute(self, query, context, invocation_id, context_hash):
        del query, context
        return AgentOutput(
            agent_name=self.name,
            tier=self.tier,
            purpose=self.purpose,
            raw_text="STATIC TEST OUTPUT",
            invocation_id=invocation_id,
            context_hash=context_hash,
            generated_at=self._now_iso(),
        )


def test_phase42_runtime_gate_on():
    assert BUILD_PHASE >= 5
    assert PHASE_4_2_ENABLED is True


def test_personality_agent_runs_when_phase42_enabled():
    agent = PersonalityAgent()
    out = agent.run("analyze this", [_StaticAgent()], {"input": "x"})
    assert "Invocation Results" in out
    assert "STATIC TEST OUTPUT" in out
