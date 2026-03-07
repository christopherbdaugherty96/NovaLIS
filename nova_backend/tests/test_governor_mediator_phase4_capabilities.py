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


def test_news_intelligence_parsing():
    from src.governor.governor_mediator import GovernorMediator, Invocation

    inv = GovernorMediator.parse_governed_invocation("summarize headline 2")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["indices"] == [2]

    inv = GovernorMediator.parse_governed_invocation("summarize headlines 1 and 4")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["indices"] == [1, 4]

    inv = GovernorMediator.parse_governed_invocation("summarize all headlines")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["selection"] == "all"

    inv = GovernorMediator.parse_governed_invocation("daily brief")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 50

    inv = GovernorMediator.parse_governed_invocation("show topic memory map")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 51

    inv = GovernorMediator.parse_governed_invocation("track story AI regulation")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 52
    assert inv.params["action"] == "track"

    inv = GovernorMediator.parse_governed_invocation("update story AI regulation")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 52
    assert inv.params["action"] == "update"

    inv = GovernorMediator.parse_governed_invocation("show story AI regulation")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 53
    assert inv.params["action"] == "show"

    inv = GovernorMediator.parse_governed_invocation("compare story AI regulation last 7 days")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 53
    assert inv.params["action"] == "compare"
    assert inv.params["days"] == 7

    inv = GovernorMediator.parse_governed_invocation(
        "compare stories AI regulation and semiconductor export controls"
    )
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 53
    assert inv.params["action"] == "compare_stories"
    assert inv.params["topics"] == ["AI regulation", "semiconductor export controls"]

    inv = GovernorMediator.parse_governed_invocation(
        "link story AI regulation to semiconductor export controls"
    )
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 52
    assert inv.params["action"] == "link"
    assert inv.params["topics"] == ["AI regulation", "semiconductor export controls"]

    inv = GovernorMediator.parse_governed_invocation("show relationship graph")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 53
    assert inv.params["action"] == "show_graph"
