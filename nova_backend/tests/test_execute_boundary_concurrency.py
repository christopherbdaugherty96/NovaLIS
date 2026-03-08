from __future__ import annotations


def test_execute_boundary_enforces_concurrency_cap():
    import src.governor.execute_boundary.execute_boundary as eb

    boundary = eb.ExecuteBoundary()
    original_cap = eb.MAX_CONCURRENT_EXECUTIONS
    eb.MAX_CONCURRENT_EXECUTIONS = 1
    try:
        boundary.enter_execution()
        try:
            raised = False
            try:
                boundary.enter_execution()
            except RuntimeError:
                raised = True
            assert raised, "Expected concurrency cap RuntimeError on second enter_execution()"
        finally:
            boundary.exit_execution()
    finally:
        eb.MAX_CONCURRENT_EXECUTIONS = original_cap


def test_execute_boundary_allows_execution_when_slot_available():
    import src.governor.execute_boundary.execute_boundary as eb

    boundary = eb.ExecuteBoundary()
    assert boundary.allow_execution() is True
