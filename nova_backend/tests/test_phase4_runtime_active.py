from src.governor.execute_boundary import GOVERNED_ACTIONS_ENABLED


def test_phase4_runtime_enabled():
    assert GOVERNED_ACTIONS_ENABLED is True
