def test_volume_media_brightness_parsing():
    from src.governor.governor_mediator import GovernorMediator, Invocation, Clarification

    inv = GovernorMediator.parse_governed_invocation("volume up")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 19

    inv = GovernorMediator.parse_governed_invocation("pause")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 20
    assert inv.params["action"] == "pause"

    inv = GovernorMediator.parse_governed_invocation("set brightness 70")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 21
    assert inv.params["action"] == "set"
    assert inv.params["level"] == 70

    inv = GovernorMediator.parse_governed_invocation("volume 50")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 19
    assert inv.params["action"] == "set"
    assert inv.params["level"] == 50

    inv = GovernorMediator.parse_governed_invocation("open Nova-Project")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 22
    assert inv.params["path"] == "Nova-Project"

    inv = GovernorMediator.parse_governed_invocation("open abc news site")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 17
    assert inv.params["target"] == "abc news"

    inv = GovernorMediator.parse_governed_invocation("open a b c news")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 17
    assert inv.params["target"] == "abc news"

    inv = GovernorMediator.parse_governed_invocation("open abc new")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 17
    assert inv.params["target"] == "abc news"

    inv = GovernorMediator.parse_governed_invocation("open project notes")
    assert isinstance(inv, Clarification)
    assert "confirm" in inv.message.lower()

    inv = GovernorMediator.parse_governed_invocation("open result 2")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 17
    assert inv.params["source_index"] == 2

    inv = GovernorMediator.parse_governed_invocation("preview source 1")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 17
    assert inv.params["source_index"] == 1
    assert inv.params["preview"] is True

    inv = GovernorMediator.parse_governed_invocation("system")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 32



def test_news_intelligence_parsing():
    from src.governor.governor_mediator import GovernorMediator, Invocation
    from src.governor.governor_mediator import Clarification

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

    inv = GovernorMediator.parse_governed_invocation("summarize the news headlines on the dashboard")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["selection"] == "all"

    inv = GovernorMediator.parse_governed_invocation("summarize ABC News")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["selection"] == "source"
    assert inv.params["source_query"] == "ABC"

    inv = GovernorMediator.parse_governed_invocation("summarize today's news")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 50
    assert inv.params["read_sources"] is True

    inv = GovernorMediator.parse_governed_invocation("today's news")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 50
    assert inv.params["read_sources"] is True

    inv = GovernorMediator.parse_governed_invocation("expand story 2")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 50
    assert inv.params["action"] == "expand_cluster"
    assert inv.params["story_id"] == 2

    inv = GovernorMediator.parse_governed_invocation("compare 1 and 3")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 50
    assert inv.params["action"] == "compare_clusters"
    assert inv.params["left_story_id"] == 1
    assert inv.params["right_story_id"] == 3

    inv = GovernorMediator.parse_governed_invocation("compare headlines 1 and 3")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["action"] == "compare_indices"
    assert inv.params["left_index"] == 1
    assert inv.params["right_index"] == 3

    inv = GovernorMediator.parse_governed_invocation("track story 2")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 50
    assert inv.params["action"] == "track_cluster"
    assert inv.params["story_id"] == 2

    inv = GovernorMediator.parse_governed_invocation("summarize latest news about war")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["selection"] == "topic"
    assert inv.params["topic_query"] == "war"

    inv = GovernorMediator.parse_governed_invocation("give me details Fox News")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["selection"] == "source"

    inv = GovernorMediator.parse_governed_invocation("most recent updates with the war")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["selection"] == "topic"
    assert inv.params["topic_query"] == "the war"

    inv = GovernorMediator.parse_governed_invocation("search for most recent updates with the war")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["selection"] == "topic"

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

    inv = GovernorMediator.parse_governed_invocation("research AI regulation trends")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 48
    assert "AI regulation trends" in inv.params["query"]

    inv = GovernorMediator.parse_governed_invocation("create an intelligence brief on lithium supply chains")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 48

    inv = GovernorMediator.parse_governed_invocation("tell me about ai regulation")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 48

    inv = GovernorMediator.parse_governed_invocation("open")
    assert isinstance(inv, Clarification)
    assert "what should i open" in inv.message.lower()

    inv = GovernorMediator.parse_governed_invocation("verify this")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 31
    assert inv.params["text"] == ""

    inv = GovernorMediator.parse_governed_invocation("fact check The moon has an atmosphere")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 31
    assert "moon has an atmosphere" in inv.params["text"].lower()

    inv = GovernorMediator.parse_governed_invocation("create analysis report on AI geopolitics")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 54
    assert inv.params["action"] == "create"

    inv = GovernorMediator.parse_governed_invocation("summarize doc 2")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 54
    assert inv.params["action"] == "summarize_doc"
    assert inv.params["doc_id"] == 2

    inv = GovernorMediator.parse_governed_invocation("explain section 3 of doc 2")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 54
    assert inv.params["action"] == "explain_section"
    assert inv.params["section_number"] == 3
    assert inv.params["doc_id"] == 2
