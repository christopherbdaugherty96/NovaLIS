import json
import platform
from pathlib import Path


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

    inv = GovernorMediator.parse_governed_invocation("set brightness to 72")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 21
    assert inv.params["action"] == "set"
    assert inv.params["level"] == 72

    inv = GovernorMediator.parse_governed_invocation("volume 50")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 19
    assert inv.params["action"] == "set"
    assert inv.params["level"] == 50

    inv = GovernorMediator.parse_governed_invocation("set volume to 33")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 19
    assert inv.params["action"] == "set"
    assert inv.params["level"] == 33

    inv = GovernorMediator.parse_governed_invocation("mute volume")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 19
    assert inv.params["action"] == "mute"

    inv = GovernorMediator.parse_governed_invocation("unmute")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 19
    assert inv.params["action"] == "unmute"

    inv = GovernorMediator.parse_governed_invocation("brightness 35")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 21
    assert inv.params["action"] == "set"
    assert inv.params["level"] == 35

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

    inv = GovernorMediator.parse_governed_invocation("what is the system status")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 32

    inv = GovernorMediator.parse_governed_invocation("weather")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 55

    inv = GovernorMediator.parse_governed_invocation("analyze source reliability for semiconductor policy updates")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 48
    assert inv.params["query"] == "semiconductor policy updates"
    assert inv.params["analysis_focus"] == "source_reliability"

    inv = GovernorMediator.parse_governed_invocation("what is the weather in ann arbor today")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 55

    inv = GovernorMediator.parse_governed_invocation("news")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 56

    inv = GovernorMediator.parse_governed_invocation("what's the news today")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 56

    inv = GovernorMediator.parse_governed_invocation("calendar")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 57

    inv = GovernorMediator.parse_governed_invocation("my calendar")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 57

    inv = GovernorMediator.parse_governed_invocation("show my calendar")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 57

    inv = GovernorMediator.parse_governed_invocation("tomorrow's schedule")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 57

    inv = GovernorMediator.parse_governed_invocation("what do i have tomorrow")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 57

    inv = GovernorMediator.parse_governed_invocation("upcoming events")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 57

    inv = GovernorMediator.parse_governed_invocation("what's coming up")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 57

    inv = GovernorMediator.parse_governed_invocation("agenda for tomorrow")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 57

    inv = GovernorMediator.parse_governed_invocation("take a screenshot")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 58
    assert inv.params["invocation_source"] == "text"

    inv = GovernorMediator.parse_governed_invocation("analyze screen")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 59
    assert inv.params["invocation_source"] == "text"

    inv = GovernorMediator.parse_governed_invocation("explain this")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 60

    inv = GovernorMediator.parse_governed_invocation("what is this")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 60

    inv = GovernorMediator.parse_governed_invocation("what am I looking at")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 60

    inv = GovernorMediator.parse_governed_invocation("view screen")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 60

    inv = GovernorMediator.parse_governed_invocation("help me do this")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 60
    assert inv.params.get("followup") is True

    inv = GovernorMediator.parse_governed_invocation("what should I click next")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 60
    assert inv.params.get("followup") is True

    inv = GovernorMediator.parse_governed_invocation("memory list")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "list"

    inv = GovernorMediator.parse_governed_invocation("what do you remember")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "overview"

    inv = GovernorMediator.parse_governed_invocation("recent memories")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "recent"

    inv = GovernorMediator.parse_governed_invocation("search memories for pour social alcohol")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "search"
    assert inv.params["query"] == "pour social alcohol"

    inv = GovernorMediator.parse_governed_invocation("memory overview")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "overview"

    inv = GovernorMediator.parse_governed_invocation("memory status")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "overview"

    inv = GovernorMediator.parse_governed_invocation("memory save deployment note: verify PYTHONPATH in container")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "save"
    assert "deployment note" in inv.params["title"].lower()

    inv = GovernorMediator.parse_governed_invocation("memory save thread Deployment Issue")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "save_thread_snapshot"
    assert inv.params["thread_name"] == "Deployment Issue"

    inv = GovernorMediator.parse_governed_invocation(
        "memory save decision for Deployment Issue: verify PYTHONPATH in container"
    )
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "save_thread_decision"
    assert inv.params["thread_name"] == "Deployment Issue"
    assert "PYTHONPATH" in inv.params["decision"]

    inv = GovernorMediator.parse_governed_invocation("memory list thread deployment issue")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "list"
    assert inv.params["thread_name"] == "deployment issue"

    inv = GovernorMediator.parse_governed_invocation("memory lock MEM-ABC123")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "lock"
    assert inv.params["item_id"] == "MEM-ABC123"

    inv = GovernorMediator.parse_governed_invocation("memory unlock MEM-ABC123 confirm")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "unlock"
    assert inv.params["confirmed"] is True

    inv = GovernorMediator.parse_governed_invocation("memory export")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "export"

    inv = GovernorMediator.parse_governed_invocation("export memory")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "export"

    inv = GovernorMediator.parse_governed_invocation("forget this")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "delete"
    assert inv.params["item_id"] == "this"
    assert inv.params["confirmed"] is False

    inv = GovernorMediator.parse_governed_invocation("forget this confirm")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "delete"
    assert inv.params["item_id"] == "this"
    assert inv.params["confirmed"] is True

    inv = GovernorMediator.parse_governed_invocation("memory")
    assert isinstance(inv, Clarification)
    assert inv.capability_id == 61
    assert "memory overview" in inv.message



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

    inv = GovernorMediator.parse_governed_invocation("summarize tech news")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["selection"] == "category"
    assert inv.params["category_key"] == "tech"

    inv = GovernorMediator.parse_governed_invocation("summarize category global")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["selection"] == "category"
    assert inv.params["category_key"] == "global"

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

    inv = GovernorMediator.parse_governed_invocation("summary of story #2")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["action"] == "story_page_summary"
    assert inv.params["story_index"] == 2

    inv = GovernorMediator.parse_governed_invocation("more on story 3")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 49
    assert inv.params["action"] == "story_page_summary"
    assert inv.params["story_index"] == 3

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

    inv = GovernorMediator.parse_governed_invocation("what are the latest updates on ai regulation")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 48
    assert "latest updates" in inv.params["query"].lower()

    inv = GovernorMediator.parse_governed_invocation("show me current updates about semiconductor exports")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 48
    assert "semiconductor exports" in inv.params["query"].lower()

    inv = GovernorMediator.parse_governed_invocation("what is the price of bitcoin right now")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 48
    assert "bitcoin" in inv.params["query"].lower()

    inv = GovernorMediator.parse_governed_invocation("how is tesla stock doing today")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 48
    assert "tesla" in inv.params["query"].lower()

    inv = GovernorMediator.parse_governed_invocation("is sports betting legal in california")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 48
    assert "legal in california" in inv.params["query"].lower()

    inv = GovernorMediator.parse_governed_invocation("what are the latest SEC crypto regulation updates")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 48
    assert "regulation updates" in inv.params["query"].lower()

    inv = GovernorMediator.parse_governed_invocation("is the sky blue")
    assert inv is None

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


def test_governor_mediator_accepts_more_natural_capability_phrases():
    from src.governor.governor_mediator import GovernorMediator, Invocation, Clarification

    inv = GovernorMediator.parse_governed_invocation("Hey Nova, can you show me the weather please?")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 55

    inv = GovernorMediator.parse_governed_invocation("catch me up on the news")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 56

    inv = GovernorMediator.parse_governed_invocation("what do I have today")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 57

    inv = GovernorMediator.parse_governed_invocation("how is Nova doing")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 32

    inv = GovernorMediator.parse_governed_invocation("open my downloads folder")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 22
    assert inv.params["target"] == "downloads"

    inv = GovernorMediator.parse_governed_invocation("go to the website github")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 17
    assert inv.params["target"] == "github"

    inv = GovernorMediator.parse_governed_invocation("read this out loud")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 18

    inv = GovernorMediator.parse_governed_invocation("make it louder")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 19
    assert inv.params["action"] == "up"

    inv = GovernorMediator.parse_governed_invocation("set volume to 45 percent")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 19
    assert inv.params["action"] == "set"
    assert inv.params["level"] == 45

    inv = GovernorMediator.parse_governed_invocation("make the screen dimmer")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 21
    assert inv.params["action"] == "down"

    inv = GovernorMediator.parse_governed_invocation("set screen brightness to 60 percent")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 21
    assert inv.params["action"] == "set"
    assert inv.params["level"] == 60

    inv = GovernorMediator.parse_governed_invocation("look at this")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 60

    inv = GovernorMediator.parse_governed_invocation("help me understand this")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 60

    inv = GovernorMediator.parse_governed_invocation("make a write-up about AI geopolitics")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 54
    assert inv.params["action"] == "create"

    inv = GovernorMediator.parse_governed_invocation("sum up doc 2")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 54
    assert inv.params["action"] == "summarize_doc"

    inv = GovernorMediator.parse_governed_invocation("walk me through section 3 of doc 2")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 54
    assert inv.params["action"] == "explain_section"

    inv = GovernorMediator.parse_governed_invocation("open my analysis reports")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 54
    assert inv.params["action"] == "list"

    inv = GovernorMediator.parse_governed_invocation("remember this: client prefers warm tone and short headlines")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "save"
    assert "client prefers warm tone" in inv.params["body"].lower()

    inv = GovernorMediator.parse_governed_invocation("what have you saved")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 61
    assert inv.params["action"] == "list"

    inv = GovernorMediator.parse_governed_invocation("follow AI regulation")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 52
    assert inv.params["action"] == "track"

    inv = GovernorMediator.parse_governed_invocation("stop following AI regulation")
    assert isinstance(inv, Invocation)
    assert inv.capability_id == 52
    assert inv.params["action"] == "stop"

    clar = GovernorMediator.parse_governed_invocation("open")
    assert isinstance(clar, Clarification)
    assert "github website" in clar.message.lower()


def test_governor_mediator_uses_capability_registry_profile_overrides(monkeypatch, tmp_path: Path):
    from src.governor import capability_registry as capability_registry_module
    from src.governor import governor_mediator as governor_mediator_module

    registry_path = tmp_path / "registry.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "phase": "8",
                "profiles": {
                    "default": {"groups": [], "enabled_overrides": {}},
                    "local-control": {"groups": [], "enabled_overrides": {"22": True}},
                },
                "capability_groups": {},
                "capabilities": [
                    {
                        "id": 22,
                        "name": "Open Local Path",
                        "status": "active",
                        "phase_introduced": "4",
                        "risk_level": "low",
                        "data_exfiltration": False,
                        "enabled": False,
                        "description": "Open a local path.",
                        "authority_scope": "suggest",
                        "authority_class": "read_only_local",
                        "requires_confirmation": False,
                        "reversible": True,
                        "external_effect": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(capability_registry_module, "REGISTRY_PATH", registry_path)
    monkeypatch.setattr(
        capability_registry_module.CapabilityRegistry,
        "_emit_profile_lifecycle_events",
        lambda self: None,
    )

    governor_mediator_module._enabled_capability_ids_cache = None
    governor_mediator_module._enabled_capability_ids_cache_at = 0.0
    governor_mediator_module._enabled_capability_ids_cache_profile = ""
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "default")

    assert governor_mediator_module.GovernorMediator.parse_governed_invocation("open documents") is None

    governor_mediator_module._enabled_capability_ids_cache = None
    governor_mediator_module._enabled_capability_ids_cache_at = 0.0
    governor_mediator_module._enabled_capability_ids_cache_profile = ""
    monkeypatch.setenv("NOVA_RUNTIME_PROFILE", "local-control")

    invocation = governor_mediator_module.GovernorMediator.parse_governed_invocation("open documents")

    assert isinstance(invocation, governor_mediator_module.Invocation)
    assert invocation.capability_id == 22
    assert invocation.params["target"] == "documents"


def test_search_clarification_roundtrip_by_session():
    from src.governor.governor_mediator import GovernorMediator, Invocation, Clarification

    session_id = "unit-session-search-clarification"
    GovernorMediator.clear_session(session_id)

    first = GovernorMediator.parse_governed_invocation("search", session_id=session_id)
    assert isinstance(first, Clarification)
    assert "what would you like to search for" in first.message.lower()

    second = GovernorMediator.parse_governed_invocation("latest weather in Detroit", session_id=session_id)
    assert isinstance(second, Invocation)
    assert second.capability_id == 16
    assert second.params["query"] == "latest weather in Detroit"


def test_mediator_allows_windows_media_and_mute(monkeypatch):
    from src.governor.governor_mediator import GovernorMediator, Invocation

    monkeypatch.setattr("src.governor.governor_mediator.platform.system", lambda: "Windows")

    mute = GovernorMediator.parse_governed_invocation("mute")
    assert isinstance(mute, Invocation)
    assert mute.capability_id == 19

    pause = GovernorMediator.parse_governed_invocation("pause")
    assert isinstance(pause, Invocation)
    assert pause.capability_id == 20


def test_mediator_keeps_supported_volume_and_media_actions_on_supported_platforms(monkeypatch):
    from src.governor.governor_mediator import GovernorMediator, Invocation

    monkeypatch.setattr("src.governor.governor_mediator.platform.system", lambda: "Linux")

    mute = GovernorMediator.parse_governed_invocation("mute volume")
    assert isinstance(mute, Invocation)
    assert mute.capability_id == 19
    assert mute.params["action"] == "mute"

    pause = GovernorMediator.parse_governed_invocation("pause")
    assert isinstance(pause, Invocation)
    assert pause.capability_id == 20
    assert pause.params["action"] == "pause"
