import pytest

from src.agents.builder import BuilderAgent
from src.build_phase import BUILD_PHASE, PHASE_4_2_ENABLED
from src.personality.core import PersonalityAgent


def test_phase42_default_runtime_lock_off():
    assert BUILD_PHASE == 4
    assert PHASE_4_2_ENABLED is False


def test_personality_agent_refuses_when_phase42_locked():
    agent = PersonalityAgent()
    with pytest.raises(RuntimeError):
        agent.run("analyze this", [BuilderAgent()], {"input": "x"})
