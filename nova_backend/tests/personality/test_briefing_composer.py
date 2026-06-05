from __future__ import annotations

import time

from src.personality.briefing_composer import Briefing, BriefingComposer, BriefingSection
from src.personality.chief_of_staff_profile import ChiefOfStaffProfile


def test_compose_from_empty_session():
    composer = BriefingComposer()
    briefing = composer.compose()
    assert isinstance(briefing, Briefing)
    text = briefing.as_text()
    assert isinstance(text, str)
    assert text == "I do not see anything that needs your attention right now."


def test_compose_with_shopify_data():
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data={
            "shopify": {
                "order_count": 3,
                "revenue": 247.50,
                "timestamp": time.time(),
            },
        },
        mode="business",
    )
    text = briefing.as_text()
    assert "3 orders" in text
    assert "$247.5" in text
    assert "Shopify" in text


def test_compose_with_calendar_data():
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data={
            "calendar": {
                "events": [
                    {"time": "2pm", "title": "Team standup"},
                    {"time": "4pm", "title": "Client call"},
                ],
                "timestamp": time.time(),
            },
        },
    )
    text = briefing.as_text()
    assert "Team standup" in text
    assert "Client call" in text
    assert "Calendar" in text


def test_compose_with_thread_snapshot():
    composer = BriefingComposer()
    briefing = composer.compose(
        thread_snapshot=[
            {"name": "Nova Runtime", "status": "active", "latest_blocker": "drift issue"},
            {"name": "Shopify Integration", "status": "blocked"},
        ],
    )
    text = briefing.as_text()
    assert "Nova Runtime" in text
    assert "drift issue" in text
    assert "Project Threads" in text


def test_compose_with_notices():
    composer = BriefingComposer()
    briefing = composer.compose(
        notice_snapshot=[
            {"type": "blocked_without_next_step", "summary": "Thread blocked", "status": "active"},
        ],
    )
    text = briefing.as_text()
    assert "Thread blocked" in text
    assert "Notices" in text


def test_compose_prioritized_order():
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data={
            "shopify": {"order_count": 5, "timestamp": time.time()},
            "calendar": {
                "events": [{"time": "9am", "title": "Standup"}],
                "timestamp": time.time(),
            },
        },
        notice_snapshot=[
            {"summary": "Urgent notice", "status": "active"},
        ],
    )
    labels = [s.label for s in briefing.sections]
    assert labels.index("Notices") < labels.index("Shopify")
    assert labels.index("Shopify") < labels.index("Calendar")


def test_full_unprioritized_view():
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data={
            "shopify": {"order_count": 2, "timestamp": time.time()},
            "calendar": {
                "events": [{"time": "10am", "title": "Review"}],
                "timestamp": time.time(),
            },
        },
        thread_snapshot=[
            {"name": "Thread A"},
        ],
    )
    full = briefing.as_unprioritized_text()
    assert "Calendar" in full
    assert "Project Threads" in full
    assert "Shopify" in full


def test_compose_does_not_call_capabilities():
    """Composer receives data as arguments, never fetches."""
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data={"shopify": {"order_count": 1, "timestamp": time.time()}},
    )
    assert isinstance(briefing, Briefing)
    assert briefing.sections


def test_briefing_output_is_presentation_only():
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data={"shopify": {"order_count": 1, "timestamp": time.time()}},
    )
    text = briefing.as_text()
    assert isinstance(text, str)
    assert not hasattr(briefing, "execute")
    assert not hasattr(briefing, "invoke")
    assert not hasattr(briefing, "dispatch")


def test_briefing_cannot_create_executable_requests():
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data={"shopify": {"order_count": 1, "timestamp": time.time()}},
    )
    for section in briefing.sections:
        for line in section.lines:
            assert "confirmed" not in line.lower() or "confirmed=true" not in line.lower()
            assert "capability_id" not in line.lower()
            assert "executor" not in line.lower()


def test_briefing_section_is_frozen():
    section = BriefingSection(label="Test", priority=1, lines=("a",))
    try:
        section.label = "Changed"
        assert False, "Should be frozen"
    except (AttributeError, Exception):
        pass


def test_briefing_is_frozen():
    briefing = Briefing(sections=(), mode="home", generated_at=time.time())
    try:
        briefing.mode = "changed"
        assert False, "Should be frozen"
    except (AttributeError, Exception):
        pass


def test_stale_data_includes_age_disclosure():
    """Tier 4 / staleness: data older than threshold must show age."""
    old_ts = time.time() - 7200  # 2 hours ago
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data={
            "shopify": {
                "order_count": 5,
                "timestamp": old_ts,
            },
        },
    )
    text = briefing.as_text()
    assert "minutes ago" in text


def test_fresh_data_no_age_disclosure():
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data={
            "shopify": {
                "order_count": 5,
                "timestamp": time.time(),
            },
        },
    )
    text = briefing.as_text()
    assert "minutes ago" not in text


def test_accepts_snapshot_dicts_only():
    """Composer accepts plain dicts, not live instances."""
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data={"shopify": {"order_count": 1}},
        thread_snapshot=[{"name": "A"}],
        notice_snapshot=[{"summary": "B", "status": "active"}],
    )
    assert isinstance(briefing, Briefing)


def test_rejects_none_gracefully():
    composer = BriefingComposer()
    briefing = composer.compose(
        session_data=None,
        thread_snapshot=None,
        notice_snapshot=None,
    )
    assert briefing.as_text() == "I do not see anything that needs your attention right now."


def test_empty_briefing_copy_is_not_alarming():
    briefing = Briefing(sections=(), mode="home", generated_at=time.time())
    text = briefing.as_text()
    lowered = text.lower()
    assert "urgent" not in lowered
    assert "alert" not in lowered
    assert "critical" not in lowered
    assert "error" not in lowered


def test_empty_briefing_does_not_invent_updates():
    briefing = Briefing(sections=(), mode="home", generated_at=time.time())
    text = briefing.as_text().lower()
    invented_update_terms = (
        "new update",
        "new updates",
        "new event",
        "new alert",
        "i found",
        "i noticed",
    )
    assert not any(term in text for term in invented_update_terms)


def test_empty_briefing_remains_advisory_only():
    briefing = Briefing(sections=(), mode="home", generated_at=time.time())
    text = briefing.as_text().lower()
    assert "needs your attention" in text
    assert "i will" not in text
    assert "i ran" not in text
    assert "i executed" not in text


def test_empty_briefing_includes_no_capability_invocation_or_action():
    briefing = Briefing(sections=(), mode="home", generated_at=time.time())
    text = briefing.as_text().lower()
    forbidden = (
        "capability_id",
        "executor",
        "confirmed=true",
        "invoke",
        "execute",
        "dispatch",
    )
    assert not any(term in text for term in forbidden)
    assert briefing.as_unprioritized_text() == briefing.as_text()
