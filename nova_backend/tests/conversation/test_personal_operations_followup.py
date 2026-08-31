from src.brief.daily_loop import DailyLoopItem, DailyLoopProjection, DailyLoopSource
from src.conversation.personal_operations_followup import (
    answer_personal_operations_followup,
    build_personal_operations_surface,
    is_personal_operations_followup,
    take_personal_operations_surface,
)
from src.conversation.personal_operations_intent import PersonalOperationsIntent


def _projection() -> DailyLoopProjection:
    return DailyLoopProjection(
        next=(
            DailyLoopItem("Review the launch checklist", "governed_memory"),
            DailyLoopItem("Call Sam at 2 PM", "calendar"),
        ),
        changed=(),
        waiting_on=(),
        open_loops=(),
        completed_today=(),
        unresolved_outcomes=(),
        recommended_next=DailyLoopItem(
            "Review the launch checklist",
            "recommendation_from:governed_memory",
        ),
        context_today=(),
        sources=(DailyLoopSource("google_tasks", "not_connected", "Google Tasks is not connected."),),
    )


def test_why_explains_immediately_prior_recommendation_with_provenance():
    surface = build_personal_operations_surface(
        PersonalOperationsIntent.RECOMMENDED_NEXT,
        _projection(),
        "What you should do next",
    )
    answer = answer_personal_operations_followup("Why?", surface)
    assert "supported DailyLoop evidence" in answer
    assert "Review the launch checklist" in answer
    assert "recommendation_from:governed_memory" in answer
    assert "No action was executed" in answer


def test_tell_me_more_preserves_items_and_missing_source_truth():
    surface = build_personal_operations_surface(
        PersonalOperationsIntent.NEXT,
        _projection(),
        "What you have next",
    )
    answer = answer_personal_operations_followup("tell me more", surface)
    assert "Review the launch checklist" in answer
    assert "Call Sam at 2 PM" in answer
    assert "Google Tasks is not connected" in answer


def test_why_uses_truthful_neutral_rationale_for_waiting_fallback():
    projection = DailyLoopProjection(
        next=(),
        changed=(),
        waiting_on=(DailyLoopItem("Vendor reply", "governed_memory"),),
        open_loops=(),
        completed_today=(),
        unresolved_outcomes=(),
        recommended_next=DailyLoopItem(
            "Review waiting item: Vendor reply",
            "recommendation_from:governed_memory",
        ),
        context_today=(),
        sources=(),
    )
    surface = build_personal_operations_surface(
        PersonalOperationsIntent.RECOMMENDED_NEXT,
        projection,
        "What you should do next",
    )
    answer = answer_personal_operations_followup("Why?", surface)
    assert "supported DailyLoop evidence" in answer
    assert "Review waiting item: Vendor reply" in answer
    assert "first supported next item" not in answer


def test_why_uses_truthful_neutral_rationale_for_open_loop_fallback():
    projection = DailyLoopProjection(
        next=(),
        changed=(),
        waiting_on=(),
        open_loops=(DailyLoopItem("Finish the beta notes", "governed_memory"),),
        completed_today=(),
        unresolved_outcomes=(),
        recommended_next=DailyLoopItem(
            "Continue open loop: Finish the beta notes",
            "recommendation_from:governed_memory",
        ),
        context_today=(),
        sources=(),
    )
    surface = build_personal_operations_surface(
        PersonalOperationsIntent.RECOMMENDED_NEXT,
        projection,
        "What you should do next",
    )
    answer = answer_personal_operations_followup("Why?", surface)
    assert "supported DailyLoop evidence" in answer
    assert "Continue open loop: Finish the beta notes" in answer
    assert "first supported next item" not in answer


def test_second_one_binds_only_to_second_prior_item():
    surface = build_personal_operations_surface(
        PersonalOperationsIntent.NEXT,
        _projection(),
        "What you have next",
    )
    answer = answer_personal_operations_followup("the second one", surface)
    assert "Call Sam at 2 PM" in answer
    assert "source: calendar" in answer
    assert "Review the launch checklist" not in answer


def test_waiting_surface_does_not_expose_unrendered_unresolved_outcome_as_second_item():
    projection = DailyLoopProjection(
        next=(),
        changed=(),
        waiting_on=(DailyLoopItem("Vendor reply", "governed_memory"),),
        open_loops=(),
        completed_today=(),
        unresolved_outcomes=(DailyLoopItem("Outcome unknown: calendar", "receipts"),),
        recommended_next=None,
        context_today=(),
        sources=(),
    )
    surface = build_personal_operations_surface(
        PersonalOperationsIntent.WAITING_ON,
        projection,
        "What you're waiting on:\n- Vendor reply\n- Unresolved action outcomes: 1",
    )
    answer = answer_personal_operations_followup("the second one", surface)
    assert answer == "I don't have a reliable second item in the immediately prior answer."
    assert "calendar" not in answer


def test_followup_without_reliable_surface_fails_closed():
    assert is_personal_operations_followup("Why?") is True
    answer = answer_personal_operations_followup("Why?", None)
    assert "don't have a reliable immediately prior" in answer
    assert "Ask the full question again" in answer


def test_unrelated_question_is_not_captured():
    assert is_personal_operations_followup("Why is the sky blue?") is False
    assert is_personal_operations_followup("tell me more about Python") is False


def test_silent_widget_refresh_does_not_consume_active_user_answer():
    surface = {"surface_type": "personal_operations"}
    state = {"active_personal_operations_surface": surface}
    assert take_personal_operations_surface(state, silent_widget_refresh=True) is None
    assert state["active_personal_operations_surface"] is surface
    assert take_personal_operations_surface(state, silent_widget_refresh=False) is surface
    assert "active_personal_operations_surface" not in state
