def test_governor_refuses_when_sealed():
    from src.governor.governor import Governor
    from src.actions.action_request import ActionRequest

    gov = Governor()

    req = ActionRequest(
        request_id="test",
        capability_id=16,
        params={"query": "test"}
    )

    result = gov._execute(req)

    assert result.success is False
