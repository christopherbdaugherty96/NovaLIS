from __future__ import annotations

from copy import deepcopy

import pytest
from src.conversation.brief_followup_grounding import (
    active_news_surface_clusters,
    answer_grounded_brief_followup,
    build_grounded_brief_context,
    is_discussion_shaped_brief_followup,
    is_explicit_news_reference_action,
    is_fetch_shaped_brief_request,
    is_schedule_commitment_question,
    schedule_commitment_guard,
    store_active_news_surface,
    store_awareness_brief_surface,
    store_brief_widget,
)


def _news_state() -> dict:
    state: dict = {}
    store_brief_widget(
        state,
        "news",
        {
            "type": "news",
            "items": [
                {"title": "Alvarez wins in extra innings", "source": "NPR", "summary": "Walk-off."},
                {"title": "Budget vote delayed", "source": "BBC News", "summary": "Recess called."},
            ],
        },
        set_focus=True,
    )
    return state


class TestSlice2CoverageAndGuard:
    # --- Audit failure 1: "top story" follow-up after news must ground to loaded news ---
    def test_top_story_followup_grounds_to_loaded_news(self):
        state = _news_state()
        assert is_discussion_shaped_brief_followup(
            "what do you think about the top story?", state
        ) is True
        answer = answer_grounded_brief_followup("what do you think about the top story?", state)
        assert "Alvarez wins in extra innings" in answer

    # --- Audit failure 2: schedule question with NO loaded calendar must refuse safely ---
    def test_meetings_question_without_calendar_refuses_safely(self):
        assert is_schedule_commitment_question("what meetings do I have tomorrow?") is True
        guard = schedule_commitment_guard("what meetings do I have tomorrow?", {})
        assert guard  # non-empty refusal
        assert "don't have your calendar loaded" in guard.lower()
        assert "won't guess" in guard.lower()

    def test_what_do_i_have_tomorrow_without_calendar_refuses(self):
        guard = schedule_commitment_guard("what do I have tomorrow?", {})
        assert guard and "calendar" in guard.lower()

    # --- Guard yields to grounded routing when calendar IS loaded ---
    # --- Loaded-but-empty calendar: answer deterministically from the source, never fabricate ---
    def test_schedule_guard_answers_from_loaded_empty_calendar_not_model(self):
        state: dict = {}
        store_brief_widget(
            state,
            "calendar",
            {"type": "calendar", "summary": "Nothing on your calendar today.", "events": []},
            set_focus=True,
        )
        answer = schedule_commitment_guard("what meetings do I have tomorrow?", state)
        assert answer  # never an empty yield that would let the model fabricate
        assert "Nothing on your calendar today" in answer
        assert "won't add commitments" in answer.lower()

    # --- Loaded calendar with events: the guard surfaces the sourced events, not the model ---
    def test_schedule_guard_lists_loaded_calendar_events(self):
        state: dict = {}
        store_brief_widget(
            state,
            "calendar",
            {
                "type": "calendar",
                "summary": "One event today.",
                "events": [{"title": "Dentist", "start": "2026-07-12T14:00"}],
            },
            set_focus=True,
        )
        answer = schedule_commitment_guard("do I have any appointments?", state)
        assert "Sourced calendar facts" in answer
        assert "Dentist" in answer

    # --- Not over-captured: ordinary unrelated chat is neither schedule nor grounded ---
    def test_ordinary_prompt_is_not_overcaptured(self):
        assert is_schedule_commitment_question("what's a good book to read?") is False
        assert schedule_commitment_guard("what's a good book to read?", {}) == ""
        assert is_discussion_shaped_brief_followup("what's a good book to read?", _news_state()) is False

    # --- Review point 3: bare schedule words must not over-capture non-schedule prompts ---
    def test_schedule_guard_does_not_overcapture_domain_word_prompts(self):
        for prompt in (
            "what do you think of my calendar logo?",
            "create a calendar event",
            "write a news-themed advertisement",
            "design a meeting agenda template",
        ):
            assert is_schedule_commitment_question(prompt) is False, prompt
            assert schedule_commitment_guard(prompt, {}) == "", prompt

    def test_schedule_question_shapes_are_detected(self):
        for prompt in (
            "what meetings do I have tomorrow?",
            "do I have any appointments?",
            "what's on my calendar today?",
            "what's my schedule?",
            "am I free tomorrow?",
        ):
            assert is_schedule_commitment_question(prompt) is True, prompt


def test_fetch_shaped_weather_stays_deterministic():
    assert is_fetch_shaped_brief_request("weather") is True
    assert is_fetch_shaped_brief_request("what's the weather?") is True
    assert is_discussion_shaped_brief_followup(
        "weather",
        {"brief_weather": {"type": "weather", "data": {"summary": "72F"}}},
    ) is False


def test_weather_followup_uses_sourced_weather_fact_block():
    state: dict = {}
    store_brief_widget(
        state,
        "weather",
        {
            "type": "weather",
            "data": {
                "summary": "72 degrees F and Partially cloudy in Ann Arbor.",
                "status": "ok",
                "provider": "Visual Crossing",
                "forecast": {"today": "87F/63F, Partially cloudy"},
            },
        },
    )

    assert is_discussion_shaped_brief_followup("Will it rain later?", state) is True
    block = build_grounded_brief_context("Will it rain later?", state)

    assert "Weather [source: Visual Crossing/weather widget; status: sourced]" in block
    assert "72 degrees F" in block
    assert "Use only these sourced facts" in block
    assert "The loaded source does not say" in block
    assert "Do not infer a yes/no answer" in block

    answer = answer_grounded_brief_followup("Will it rain later?", state)
    assert "The loaded source does not say whether it will rain later" in answer
    assert "cloud cover alone" in answer


def test_second_news_story_selects_second_loaded_headline():
    state: dict = {}
    store_brief_widget(
        state,
        "news",
        {
            "type": "news",
            "items": [
                {"title": "First headline", "source": "NPR", "summary": "First summary"},
                {"title": "Second headline", "source": "BBC News", "summary": "Second summary"},
            ],
        },
        set_focus=True,
    )

    assert is_discussion_shaped_brief_followup("Tell me more about the second story.", state) is True
    block = build_grounded_brief_context("Tell me more about the second story.", state)

    assert "Second headline" in block
    assert "BBC News" in block
    assert "First headline" not in block

    answer = answer_grounded_brief_followup("Tell me more about the second story.", state)
    assert "Second headline" in answer
    assert "First headline" not in answer
    assert "should not add unstated facts" in answer


def test_news_followup_stays_attached_to_selected_story():
    state: dict = {}
    store_brief_widget(
        state,
        "news",
        {
            "type": "news",
            "items": [
                {"title": "First headline", "source": "NPR", "summary": "First summary"},
                {"title": "Second headline", "source": "BBC News", "summary": "Second summary"},
            ],
        },
        set_focus=True,
    )

    first_answer = answer_grounded_brief_followup("Tell me more about the second story.", state)
    second_answer = answer_grounded_brief_followup("Why does that matter?", state)

    assert "Second headline" in first_answer
    assert "Second headline" in second_answer
    assert "First headline" not in second_answer
    assert state["active_news_story_index"] == 1


def test_broad_awareness_followup_does_not_bind_to_selected_story():
    state: dict = {}
    store_brief_widget(
        state,
        "news",
        {
            "type": "news",
            "items": [
                {"title": "First headline", "source": "NPR", "summary": "First summary"},
                {"title": "Selected headline", "source": "BBC News", "summary": "Selected summary"},
                {"title": "Third headline", "source": "AP", "summary": "Third summary"},
            ],
        },
        set_focus=True,
    )

    answer_grounded_brief_followup("Tell me more about the second story.", state)

    prompt = "anything else ongoing that I should be aware of?"
    assert is_discussion_shaped_brief_followup(prompt, state) is True
    answer = answer_grounded_brief_followup(prompt, state)

    assert "Other sourced headlines" in answer
    assert "First headline" in answer
    assert "Third headline" in answer
    assert "Selected headline" not in answer
    assert "not additional claims about the selected story" in answer


def test_broad_awareness_followup_prefers_available_awareness_surface_over_selected_story():
    state: dict = {}
    store_awareness_brief_surface(
        state,
        {
            "sections": [
                {
                    "key": "calendar_today",
                    "title": "Calendar",
                    "items": ["Dentist appointment at 3 PM."],
                    "source": "local calendar",
                    "status": "ok",
                },
                {
                    "key": "weather_today",
                    "title": "Weather",
                    "items": ["Rain is possible this afternoon."],
                    "source": "weather provider",
                    "status": "ok",
                },
            ]
        },
    )
    store_brief_widget(
        state,
        "news",
        {
            "type": "news",
            "items": [
                {"title": "First headline", "source": "NPR", "summary": "First summary"},
                {"title": "Selected headline", "source": "BBC News", "summary": "Selected summary"},
            ],
        },
        set_focus=True,
    )
    answer_grounded_brief_followup("Tell me more about the second story.", state)

    prompt = "anything else ongoing that I should be aware of?"
    assert is_discussion_shaped_brief_followup(prompt, state) is True
    answer = answer_grounded_brief_followup(prompt, state)

    assert "Current rendered brief" in answer
    assert "Dentist appointment at 3 PM" in answer
    assert "Rain is possible this afternoon" in answer
    assert "Selected headline" not in answer
    assert "I do not have a rendered intelligence brief" not in answer


def test_explicit_story_reference_remains_attached_to_selected_story():
    state = _news_state()
    answer_grounded_brief_followup("Tell me more about the second story.", state)

    for prompt in (
        "anything else current that I should know about that story?",
        "anything else current that I should know about it?",
    ):
        assert is_discussion_shaped_brief_followup(prompt, state) is True
        answer = answer_grounded_brief_followup(prompt, state)

        assert "Budget vote delayed" in answer
        assert "Alvarez wins" not in answer


def test_unrelated_prompts_are_not_captured_after_brief_loads():
    state: dict = {}
    store_brief_widget(
        state,
        "weather",
        {
            "type": "weather",
            "data": {"summary": "72 degrees F and Partially cloudy in Ann Arbor."},
        },
    )
    state["active_brief_item"] = "weather"

    assert is_discussion_shaped_brief_followup("write a product description", state) is False
    assert is_discussion_shaped_brief_followup("Tell me a story", state) is False
    assert is_discussion_shaped_brief_followup("What is the status of my order?", state) is False
    assert is_discussion_shaped_brief_followup("What events caused the recession?", state) is False
    assert build_grounded_brief_context("write a product description", state) == ""


def test_explicit_domain_unrelated_prompts_are_not_captured():
    state: dict = {}
    store_brief_widget(
        state,
        "weather",
        {
            "type": "weather",
            "data": {"summary": "72 degrees F and Partially cloudy in Ann Arbor."},
        },
    )
    store_brief_widget(
        state,
        "news",
        {
            "type": "news",
            "items": [{"title": "Loaded headline", "source": "NPR"}],
        },
    )
    store_brief_widget(
        state,
        "calendar",
        {
            "type": "calendar",
            "summary": "Two events today.",
            "events": [{"title": "Meeting", "date": "2026-07-11", "time": "2:00 PM"}],
        },
    )
    state["active_brief_item"] = "weather"

    assert is_discussion_shaped_brief_followup("write a weather-themed product description", state) is False
    assert is_discussion_shaped_brief_followup("write a news-themed advertisement", state) is False
    assert is_discussion_shaped_brief_followup("create a calendar event", state) is False
    assert is_discussion_shaped_brief_followup("Should I create a weather-themed product?", state) is False
    assert is_discussion_shaped_brief_followup("Why does my news-themed advertisement look bad?", state) is False
    assert is_discussion_shaped_brief_followup("What do you think of my calendar logo?", state) is False
    assert is_discussion_shaped_brief_followup("tell me more about story 2", state) is False
    assert is_discussion_shaped_brief_followup("what sources support story 1?", state) is False


def test_background_widget_refresh_does_not_change_conversation_focus():
    state: dict = {"active_brief_item": "news"}

    store_brief_widget(
        state,
        "weather",
        {
            "type": "weather",
            "data": {"summary": "72 degrees F and Partially cloudy in Ann Arbor."},
        },
    )

    assert state["active_brief_item"] == "news"


def test_exact_news_aliases_remain_explicit_typed_references():
    for prompt in (
        "tell me more about the second one",
        "compare the first and third stories",
        "open the first one",
        "what was story 1 again?",
    ):
        assert is_explicit_news_reference_action(prompt) is True


def test_negative_rain_wording_is_not_inverted():
    state: dict = {}
    store_brief_widget(
        state,
        "weather",
        {
            "type": "weather",
            "data": {
                "summary": "No rain expected today.",
                "status": "ok",
                "provider": "Visual Crossing",
                "precip_probability": 0,
            },
        },
        set_focus=True,
    )

    answer = answer_grounded_brief_followup("Will it rain later?", state)

    assert "does not indicate rain" in answer
    assert "rain is possible" not in answer


def test_news_selection_clears_when_refresh_replaces_story_identity():
    state: dict = {}
    store_brief_widget(
        state,
        "news",
        {
            "type": "news",
            "items": [
                {"title": "First headline", "source": "NPR", "url": "https://example.test/1"},
                {"title": "Second headline", "source": "BBC News", "url": "https://example.test/2"},
            ],
        },
        set_focus=True,
    )

    answer_grounded_brief_followup("Tell me more about the second story.", state)
    store_brief_widget(
        state,
        "news",
        {
            "type": "news",
            "items": [
                {"title": "Different first", "source": "NPR", "url": "https://example.test/a"},
                {"title": "Different second", "source": "BBC News", "url": "https://example.test/b"},
            ],
        },
    )

    assert "active_news_story_id" not in state
    answer = answer_grounded_brief_followup("Why does that matter?", state)
    assert "Different second" not in answer
    assert "selected headline" in answer


def test_calendar_followup_uses_ics_event_context():
    state: dict = {}
    store_brief_widget(
        state,
        "calendar",
        {
            "type": "calendar",
            "summary": "Two events today.",
            "events": [{"summary": "Dentist", "start": "2026-07-11T14:00:00"}],
        },
        set_focus=True,
    )

    answer_grounded_brief_followup("Tell me more about the first event.", state)

    assert is_discussion_shaped_brief_followup("What do I have after that?", state) is True
    block = build_grounded_brief_context("What do I have after that?", state)

    assert "Calendar [source: local .ics/calendar widget; status: sourced]" in block
    assert "Dentist" in block


def test_unqualified_after_that_requires_selected_calendar_event():
    state: dict = {}
    store_brief_widget(
        state,
        "calendar",
        {
            "type": "calendar",
            "summary": "Two events today.",
            "events": [
                {"title": "Zebra Meeting", "date": "2026-07-11", "time": "2:00 PM"},
                {"title": "Alpha Meeting", "date": "2026-07-11", "time": "3:00 PM"},
            ],
        },
        set_focus=True,
    )

    assert is_discussion_shaped_brief_followup(
        "I finished the product description. What should I do after that?",
        state,
    ) is False

    answer_grounded_brief_followup("Tell me more about the first event.", state)

    assert is_discussion_shaped_brief_followup("What do I have after that?", state) is True


@pytest.mark.parametrize(
    "prompt",
    [
        "is there anything on the local server today?",
        "is there anything written on this document today?",
        "is there any note on my desk today?",
    ],
)
def test_active_calendar_does_not_capture_explicit_non_calendar_targets(prompt: str):
    state: dict = {}
    store_brief_widget(
        state,
        "calendar",
        {
            "type": "calendar",
            "summary": "One event today.",
            "events": [
                {"title": "Dentist", "date": "2026-07-11", "time": "2:00 PM"},
            ],
        },
        set_focus=True,
    )
    answer_grounded_brief_followup("Tell me more about the first event.", state)

    assert is_discussion_shaped_brief_followup(prompt, state) is False


def test_active_calendar_keeps_explicit_event_reference():
    state: dict = {}
    store_brief_widget(
        state,
        "calendar",
        {
            "type": "calendar",
            "summary": "One event today.",
            "events": [
                {"title": "Dentist", "date": "2026-07-11", "time": "2:00 PM"},
            ],
        },
        set_focus=True,
    )
    answer_grounded_brief_followup("Tell me more about the first event.", state)

    assert is_discussion_shaped_brief_followup("What time is that?", state) is True


def test_calendar_after_that_returns_next_sorted_event():
    state: dict = {}
    store_brief_widget(
        state,
        "calendar",
        {
            "type": "calendar",
            "summary": "Two events today.",
            "events": [
                {"summary": "Second event", "start": "2026-07-11T15:00:00"},
                {"summary": "First event", "start": "2026-07-11T14:00:00"},
            ],
        },
        set_focus=True,
    )

    selected = answer_grounded_brief_followup("Tell me more about the first event.", state)
    next_event = answer_grounded_brief_followup("What do I have after that?", state)

    assert "First event" in selected
    assert "Second event" in next_event
    assert "First event" not in next_event


def test_calendar_after_that_uses_real_calendar_skill_event_shape():
    state: dict = {}
    store_brief_widget(
        state,
        "calendar",
        {
            "type": "calendar",
            "summary": "Two events today.",
            "events": [
                {"title": "Zebra Meeting", "date": "2026-07-11", "time": "2:00 PM", "day_label": "Saturday"},
                {"title": "Alpha Meeting", "date": "2026-07-11", "time": "3:00 PM", "day_label": "Saturday"},
            ],
        },
        set_focus=True,
    )

    selected = answer_grounded_brief_followup("Tell me more about the first event.", state)
    next_event = answer_grounded_brief_followup("What do I have after that?", state)

    assert "Zebra Meeting" in selected
    assert "Alpha Meeting" in next_event
    assert "Zebra Meeting" not in next_event


def _rendered_brief_state(*, placeholder: bool = False) -> dict:
    clusters = [
        {
            "id": 1,
            "title": "Global Security",
            "summary": "Regional tensions increased after new strikes.",
            "implication": "Watch for changes to shipping and energy risk.",
            "sources": ["BBC News", "NPR"],
            "items": [{"title": "Security story", "source": "BBC News"}],
            "placeholder": placeholder,
            "synthesis_status": "placeholder" if placeholder else "fresh",
        },
        {
            "id": 2,
            "title": "Technology",
            "summary": "Chip investment continued.",
            "implication": "Capacity plans remain the key signal.",
            "sources": ["TechCrunch"],
            "items": [{"title": "Chip story", "source": "TechCrunch"}],
            "placeholder": False,
            "synthesis_status": "fresh",
        },
    ]
    state = {"last_brief_clusters": clusters}
    store_active_news_surface(state, "brief", clusters)
    return state


def test_what_matters_uses_rendered_clusters_not_broad_dashboard_facts():
    state = _rendered_brief_state()
    state["brief_weather"] = {"data": {"summary": "Unrelated weather"}}
    state["last_calendar_summary"] = "Unrelated calendar"

    assert is_discussion_shaped_brief_followup("What matters most?", state) is True
    answer = answer_grounded_brief_followup("What matters most?", state)

    assert "Global Security" in answer
    assert "Regional tensions increased" in answer
    assert "Unrelated weather" not in answer
    assert "Unrelated calendar" not in answer
    assert "Sourced brief facts" not in answer


def test_rendered_brief_completeness_reports_partial_deterministically():
    state = _rendered_brief_state(placeholder=True)

    assert is_discussion_shaped_brief_followup("Is this brief complete or partial?", state) is True
    answer = answer_grounded_brief_followup("Is this brief complete or partial?", state)

    assert "partial" in answer.lower()
    assert "1 of 2" in answer


def test_active_category_surface_replaces_old_brief_for_numeric_commands():
    state = _rendered_brief_state()
    category_items = [
        {"title": "First category story", "source": "NPR", "summary": "First category summary"},
        {"title": "Second category story", "source": "BBC News", "summary": "Second category summary"},
    ]

    store_active_news_surface(state, "category", category_items, category_key="global")
    clusters = active_news_surface_clusters(state)
    answer = answer_grounded_brief_followup("Tell me more about the second story.", state)

    assert clusters[1]["title"] == "Second category story"
    assert "Second category story" in answer
    assert "Technology" not in answer


def test_what_matters_after_category_uses_active_category_not_old_brief():
    state = _rendered_brief_state()
    category_items = [
        {"title": "Active category lead", "source": "NPR", "summary": "Visible lead summary"},
        {"title": "Active category second", "source": "BBC News", "summary": "Visible second summary"},
    ]
    store_active_news_surface(state, "category", category_items, category_key="global")

    assert is_discussion_shaped_brief_followup("What matters most?", state) is True
    answer = answer_grounded_brief_followup("What matters most?", state)

    assert "Active category lead" in answer
    assert "Global Security" not in answer
    assert "deterministic ranking" in answer


def _awareness_payload() -> dict:
    return {
        "type": "awareness_brief",
        "sections": [
            {
                "key": "weather",
                "title": "Weather",
                "items": ["Rain starts after 3 PM."],
                "status": "ok",
                "source": "weather",
            },
            {
                "key": "news",
                "title": "News",
                "items": ["Markets await the rate decision."],
                "status": "ok",
                "source": "news",
            },
        ],
    }


def _awareness_payload_with_auralis(
    *,
    owner_blocker: str = "Owner blocker: Meta business verification",
    best_move: str = "Best move: Open Meta Business Suite and click Verify account",
    status: str = "ok",
) -> dict:
    payload = _awareness_payload()
    payload["sections"].append(
        {
            "key": "auralis_today",
            "title": "Auralis Today",
            "items": [
                "Store status unavailable (Shopify not connected).",
                owner_blocker,
                best_move,
                "Watch: July 9 Google Merchant review",
            ],
            "status": status,
            "source": "auralis:inputs_partial",
        }
    )
    return payload


def test_awareness_overview_phrasings_use_first_rendered_sourced_fact():
    for phrase in (
        "What matters most?",
        "What stands out?",
        "What should I watch?",
        "Keep an eye on",
    ):
        state: dict = {}
        store_awareness_brief_surface(state, _awareness_payload(), set_focus=True)

        assert is_discussion_shaped_brief_followup(phrase, state) is True
        answer = answer_grounded_brief_followup(phrase, state)

        assert "Rain starts after 3 PM." in answer
        assert "source: weather" in answer
        assert "Markets await the rate decision." not in answer


def test_active_awareness_decision_followup_returns_only_auralis_decision_contract():
    state: dict = {}
    payload = _awareness_payload_with_auralis()
    auralis_items = payload["sections"][-1]["items"]
    displayed_owner = next(item for item in auralis_items if item.startswith("Owner blocker:"))
    displayed_best = next(item for item in auralis_items if item.startswith("Best move:"))
    store_awareness_brief_surface(
        state,
        payload,
        set_focus=True,
    )
    before = deepcopy(state)

    assert is_discussion_shaped_brief_followup(
        "What decision requires my attention?",
        state,
    ) is True
    answer = answer_grounded_brief_followup(
        "What decision requires my attention?",
        state,
    )

    lines = answer.splitlines()
    owner_lines = [line for line in lines if line.startswith("- Owner blocker:")]
    best_lines = [line for line in lines if line.startswith("- Best move:")]
    provenance_lines = [line for line in lines if line.startswith("[source:")]

    assert len(owner_lines) == 1
    assert len(best_lines) == 1
    assert owner_lines[0].removeprefix("- ") == displayed_owner
    assert best_lines[0].removeprefix("- ") == displayed_best
    assert "source:" not in owner_lines[0]
    assert "status:" not in owner_lines[0]
    assert "source:" not in best_lines[0]
    assert "status:" not in best_lines[0]
    assert provenance_lines == ["[source: auralis:inputs_partial; status: ok]"]
    assert "Watch: July 9 Google Merchant review" not in answer
    assert "These are displayed recommendations, not approval or permission to act." in lines
    assert state == before


def test_active_awareness_decision_followup_surfaces_explicit_none_as_truth():
    state: dict = {}
    displayed_owner = "Owner blocker: none gating revenue right now."
    displayed_best = "Best move: promote hooded sherpas - top of the promotion queue, channels ready."
    store_awareness_brief_surface(
        state,
        _awareness_payload_with_auralis(
            owner_blocker=displayed_owner,
            best_move=displayed_best,
        ),
        set_focus=True,
    )

    answer = answer_grounded_brief_followup("What do I need to decide?", state)

    lines = answer.splitlines()
    owner_line = next(line for line in lines if line.startswith("- Owner blocker:"))
    best_line = next(line for line in lines if line.startswith("- Best move:"))
    assert owner_line.removeprefix("- ") == displayed_owner
    assert best_line.removeprefix("- ") == displayed_best
    assert "source:" not in owner_line
    assert "status:" not in owner_line
    assert "source:" not in best_line
    assert "status:" not in best_line
    assert "[source: auralis:inputs_partial; status: ok]" in lines
    assert "unavailable" not in answer.lower()


def test_active_awareness_decision_followup_degrades_for_unavailable_auralis():
    state: dict = {}
    store_awareness_brief_surface(
        state,
        _awareness_payload_with_auralis(
            owner_blocker="Not enough trusted inputs to recommend today.",
            best_move="Connect Shopify (read-only) or seed owner-action/promotion items.",
            status="not_configured",
        ),
        set_focus=True,
    )

    answer = answer_grounded_brief_followup(
        "Is there a decision I need to make?",
        state,
    )

    assert "decision information is unavailable" in answer
    assert "status: not_configured" in answer
    assert "Best move:" not in answer


def test_exact_decision_intent_uses_silently_hydrated_awareness_without_setting_focus():
    state: dict = {}
    payload = _awareness_payload_with_auralis()
    auralis_items = payload["sections"][-1]["items"]
    displayed_owner = next(item for item in auralis_items if item.startswith("Owner blocker:"))
    displayed_best = next(item for item in auralis_items if item.startswith("Best move:"))
    store_awareness_brief_surface(state, payload, set_focus=False)
    before = deepcopy(state)

    assert is_discussion_shaped_brief_followup(
        "What decision requires my attention?",
        state,
    ) is True
    answer = answer_grounded_brief_followup(
        "What decision requires my attention?",
        state,
    )

    lines = answer.splitlines()
    assert f"- {displayed_owner}" in lines
    assert f"- {displayed_best}" in lines
    assert "Watch: July 9 Google Merchant review" not in answer
    assert "active_brief_item" not in state
    assert state == before


def test_empty_focus_decision_fallback_requires_complete_auralis_contract():
    state: dict = {}
    payload = _awareness_payload_with_auralis()
    payload["sections"][-1]["items"] = ["Owner blocker: Meta business verification"]
    store_awareness_brief_surface(state, payload, set_focus=False)

    assert is_discussion_shaped_brief_followup(
        "What decision requires my attention?",
        state,
    ) is False
    assert answer_grounded_brief_followup(
        "What decision requires my attention?",
        state,
    ) == ""


def test_empty_focus_decision_fallback_preserves_unavailable_response():
    state: dict = {}
    store_awareness_brief_surface(
        state,
        _awareness_payload_with_auralis(
            owner_blocker="Not enough trusted inputs to recommend today.",
            status="not_configured",
        ),
        set_focus=False,
    )
    before = deepcopy(state)

    assert is_discussion_shaped_brief_followup(
        "What decision requires my attention?",
        state,
    ) is True
    answer = answer_grounded_brief_followup(
        "What decision requires my attention?",
        state,
    )

    assert "decision information is unavailable" in answer
    assert "status: not_configured" in answer
    assert state == before


def test_non_decision_vague_wording_does_not_use_empty_focus_awareness():
    state: dict = {}
    store_awareness_brief_surface(state, _awareness_payload_with_auralis(), set_focus=False)

    assert is_discussion_shaped_brief_followup("Tell me more about that", state) is False
    assert answer_grounded_brief_followup("Tell me more about that", state) == ""


def test_active_news_surface_keeps_decision_phrasing_out_of_awareness():
    state = _rendered_brief_state()
    store_awareness_brief_surface(
        state,
        _awareness_payload_with_auralis(),
        set_focus=False,
    )
    store_active_news_surface(
        state,
        "category",
        [{"title": "Active news lead", "source": "NPR"}],
        category_key="global",
    )

    assert state["active_brief_item"] == "news"
    assert is_discussion_shaped_brief_followup(
        "What decision requires my attention?",
        state,
    ) is False


def test_any_non_awareness_explicit_focus_blocks_empty_focus_decision_fallback():
    for active_key in ("weather", "calendar", "runtime", "future_surface"):
        state: dict = {}
        store_awareness_brief_surface(state, _awareness_payload_with_auralis(), set_focus=False)
        state["active_brief_item"] = active_key

        assert is_discussion_shaped_brief_followup(
            "What decision requires my attention?",
            state,
        ) is False
        assert answer_grounded_brief_followup(
            "What decision requires my attention?",
            state,
        ) == ""


def test_awareness_overview_degrades_honestly_without_live_content():
    state: dict = {}
    store_awareness_brief_surface(
        state,
        {
            "sections": [
                {
                    "key": "weather",
                    "title": "Weather",
                    "items": ["Weather temporarily unavailable."],
                    "status": "unavailable",
                    "source": "weather",
                }
            ]
        },
        set_focus=True,
    )

    answer = answer_grounded_brief_followup("What matters most?", state)
    assert "does not contain enough live information" in answer


def test_awareness_storage_does_not_mutate_cap50_state_or_numeric_story_identity():
    state = _rendered_brief_state()
    original_clusters = list(state["last_brief_clusters"])
    category_items = [
        {"title": "First category story", "source": "NPR", "summary": "First summary"},
        {"title": "Second category story", "source": "BBC News", "summary": "Second summary"},
    ]
    store_active_news_surface(state, "category", category_items, category_key="global")
    original_surface = dict(state["active_news_surface"])

    store_awareness_brief_surface(state, _awareness_payload(), set_focus=True)

    assert state["last_brief_clusters"] == original_clusters
    assert state["active_news_surface"] == original_surface
    answer = answer_grounded_brief_followup("Tell me more about the second story.", state)
    assert "Second category story" in answer


def test_foreground_surface_controls_overview_precedence_and_silent_refresh_does_not_steal_it():
    state = _rendered_brief_state()
    category_items = [
        {"title": "Active news lead", "source": "NPR", "summary": "News summary"},
    ]
    store_active_news_surface(state, "category", category_items, category_key="global")
    store_awareness_brief_surface(state, _awareness_payload(), set_focus=False)

    news_answer = answer_grounded_brief_followup("What matters most?", state)
    assert "Active news lead" in news_answer
    assert "Rain starts after 3 PM." not in news_answer

    store_awareness_brief_surface(state, _awareness_payload(), set_focus=True)
    awareness_answer = answer_grounded_brief_followup("What matters most?", state)
    assert "Rain starts after 3 PM." in awareness_answer
    assert "Active news lead" not in awareness_answer


def test_active_surface_identity_is_stable_for_same_story_collection():
    state: dict = {}
    items = [
        {"title": "Story A", "source": "NPR", "url": "https://example.test/a"},
        {"title": "Story B", "source": "BBC News", "url": "https://example.test/b"},
    ]
    store_active_news_surface(state, "category", items, category_key="global")
    first_surface_id = state["active_news_surface"]["surface_id"]
    store_active_news_surface(state, "category", list(items), category_key="global")

    assert state["active_news_surface"]["surface_id"] == first_surface_id
    assert state["active_news_surface"]["index_to_story"][2] == "url:https://example.test/b"
