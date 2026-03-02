def test_volume_media_brightness_parsing():
    from src.governor.governor_mediator import GovernorMediator, Invocation

    inv = GovernorMediator.parse_governed_invocation("volume up")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 19

    inv = GovernorMediator.parse_governed_invocation("pause")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 20

    inv = GovernorMediator.parse_governed_invocation("set brightness 70")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 21
    assert inv.params["level"] == 70
