from src.governor.governor_mediator import GovernorMediator, Invocation


def test_parse_speak_that_invocation():
    inv = GovernorMediator.parse_governed_invocation("speak that")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 18
    assert inv.params == {}
