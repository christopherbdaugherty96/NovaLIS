def test_execution_flag_sealed():
    from src.governor.execute_boundary import GOVERNED_ACTIONS_ENABLED
    assert GOVERNED_ACTIONS_ENABLED is False
