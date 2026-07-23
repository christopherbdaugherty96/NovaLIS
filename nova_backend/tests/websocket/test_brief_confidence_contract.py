from src.conversation.brief_followup_grounding import store_active_news_surface
from src.websocket.session_handler import (
    _apply_news_synthesis_ready_state,
    _brief_message_confidence,
)


def test_brief_message_confidence_matches_rendered_report_value():
    report = """TODAY'S INTELLIGENCE BRIEF

1. Global Security
Summary text.

Confidence: Medium-Low
Sources used: 4
"""

    assert _brief_message_confidence(report) == "Medium-Low"


def test_brief_message_confidence_does_not_invent_standard_default():
    assert _brief_message_confidence("Headline summary without a confidence field.") == ""


def test_synthesis_ready_replaces_brief_in_place_without_stealing_category_focus():
    old_brief = [{"title": "Old brief", "placeholder": True}]
    category = [{"title": "Active category story", "source": "NPR"}]
    state = {"last_brief_clusters": old_brief}
    store_active_news_surface(state, "category", category, category_key="global")

    updated = [{"title": "Updated brief", "placeholder": False}]
    _apply_news_synthesis_ready_state(state, {"brief_clusters": updated})

    assert state["last_brief_clusters"] == updated
    assert state["active_news_surface"]["surface_type"] == "category"
    assert state["active_news_surface"]["stories"] == category


def test_synthesis_ready_updates_active_brief_surface_atomically():
    state = {"last_brief_clusters": [{"title": "Old brief", "placeholder": True}]}
    store_active_news_surface(state, "brief", state["last_brief_clusters"])
    old_surface_id = state["active_news_surface"]["surface_id"]

    updated = [{"title": "Updated brief", "placeholder": False}]
    _apply_news_synthesis_ready_state(state, {"brief_clusters": updated})

    assert state["last_brief_clusters"] == updated
    assert state["active_news_surface"]["stories"] == updated
    assert state["active_news_surface"]["surface_id"] != old_surface_id
