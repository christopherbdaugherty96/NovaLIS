from __future__ import annotations

from src.conversation.brief_followup_grounding import (
    active_news_surface_clusters,
    answer_grounded_brief_followup,
    build_grounded_brief_context,
    is_discussion_shaped_brief_followup,
    is_fetch_shaped_brief_request,
    is_schedule_commitment_question,
    schedule_commitment_guard,
    store_active_news_surface,
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
