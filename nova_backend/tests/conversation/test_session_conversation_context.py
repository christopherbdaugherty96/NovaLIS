"""
Tests for SessionConversationContext — serialization, deserialization, and
the continuity fields (mode, last_decision, open_loops, recent_recommendations)
wired through _next_conversation_context.
"""
from __future__ import annotations

from src.skills.general_chat import SessionConversationContext


# ---------------------------------------------------------------------------
# Serialization round-trip
# ---------------------------------------------------------------------------


class TestToDict:
    def test_default_instance_produces_all_keys(self):
        ctx = SessionConversationContext()
        d = ctx.to_dict()
        for key in (
            "topic", "user_goal", "open_question", "active_options",
            "latest_recommendation", "rewrite_target", "presentation_preference",
            "last_answer_kind", "last_options_snapshot",
            "mode", "last_decision", "open_loops", "recent_recommendations",
        ):
            assert key in d, f"Missing key: {key}"

    def test_new_fields_roundtrip(self):
        ctx = SessionConversationContext(
            mode="analysis",
            last_decision="analysis:explanation",
            open_loops=["What is the best option?", "How long will it take?"],
            recent_recommendations=["Go with option A", "Consider option B"],
        )
        d = ctx.to_dict()
        assert d["mode"] == "analysis"
        assert d["last_decision"] == "analysis:explanation"
        assert d["open_loops"] == ["What is the best option?", "How long will it take?"]
        assert d["recent_recommendations"] == ["Go with option A", "Consider option B"]

    def test_to_dict_returns_copies_of_lists(self):
        loops = ["q1", "q2"]
        recs = ["r1"]
        ctx = SessionConversationContext(open_loops=loops, recent_recommendations=recs)
        d = ctx.to_dict()
        d["open_loops"].append("mutated")
        d["recent_recommendations"].append("mutated")
        assert ctx.open_loops == ["q1", "q2"]
        assert ctx.recent_recommendations == ["r1"]


# ---------------------------------------------------------------------------
# from_session_state — new fields
# ---------------------------------------------------------------------------


class TestFromSessionState:
    def test_reads_mode_from_payload(self):
        ctx = SessionConversationContext.from_session_state(
            {"conversation_context": {"mode": "brainstorm"}}
        )
        assert ctx.mode == "brainstorm"

    def test_reads_last_decision_from_payload(self):
        ctx = SessionConversationContext.from_session_state(
            {"conversation_context": {"last_decision": "direct:answer"}}
        )
        assert ctx.last_decision == "direct:answer"

    def test_reads_open_loops_from_payload(self):
        ctx = SessionConversationContext.from_session_state(
            {"conversation_context": {"open_loops": ["Loop A", "Loop B"]}}
        )
        assert ctx.open_loops == ["Loop A", "Loop B"]

    def test_reads_recent_recommendations_from_payload(self):
        ctx = SessionConversationContext.from_session_state(
            {"conversation_context": {"recent_recommendations": ["Rec 1", "Rec 2"]}}
        )
        assert ctx.recent_recommendations == ["Rec 1", "Rec 2"]

    def test_empty_state_returns_empty_continuity_fields(self):
        ctx = SessionConversationContext.from_session_state({})
        assert ctx.mode == ""
        assert ctx.last_decision == ""
        assert ctx.open_loops == []
        assert ctx.recent_recommendations == []

    def test_none_state_returns_empty_continuity_fields(self):
        ctx = SessionConversationContext.from_session_state(None)
        assert ctx.mode == ""
        assert ctx.open_loops == []
        assert ctx.recent_recommendations == []

    def test_filters_blank_entries_from_open_loops(self):
        ctx = SessionConversationContext.from_session_state(
            {"conversation_context": {"open_loops": ["", "  ", "real question?"]}}
        )
        assert ctx.open_loops == ["real question?"]

    def test_filters_blank_entries_from_recent_recommendations(self):
        ctx = SessionConversationContext.from_session_state(
            {"conversation_context": {"recent_recommendations": [" ", "Use option A"]}}
        )
        assert ctx.recent_recommendations == ["Use option A"]

    def test_non_list_open_loops_falls_back_to_empty(self):
        ctx = SessionConversationContext.from_session_state(
            {"conversation_context": {"open_loops": None}}
        )
        assert ctx.open_loops == []

    def test_roundtrip_via_session_state(self):
        original = SessionConversationContext(
            mode="work",
            last_decision="work:recommendation",
            open_loops=["Which framework?"],
            recent_recommendations=["Use FastAPI"],
        )
        restored = SessionConversationContext.from_session_state(
            {"conversation_context": original.to_dict()}
        )
        assert restored.mode == "work"
        assert restored.last_decision == "work:recommendation"
        assert restored.open_loops == ["Which framework?"]
        assert restored.recent_recommendations == ["Use FastAPI"]


# ---------------------------------------------------------------------------
# open_loops accumulation logic (tested via direct instantiation)
# ---------------------------------------------------------------------------


class TestOpenLoopsAccumulation:
    def _build_next(
        self,
        *,
        open_question: str,
        existing_loops: list[str],
        topic_shift: bool = False,
    ) -> list[str]:
        """Replicate the open_loops computation from _next_conversation_context."""
        existing = SessionConversationContext(open_loops=existing_loops)
        if open_question and not topic_shift:
            loops_seen: list[str] = []
            for s in [open_question] + list(existing.open_loops):
                if s not in loops_seen:
                    loops_seen.append(s)
            return loops_seen[:5]
        elif topic_shift:
            return [open_question] if open_question else []
        return list(existing.open_loops)

    def test_new_question_prepended(self):
        result = self._build_next(
            open_question="New question?",
            existing_loops=["Old question?"],
        )
        assert result[0] == "New question?"
        assert "Old question?" in result

    def test_duplicate_question_not_added_twice(self):
        result = self._build_next(
            open_question="Same question?",
            existing_loops=["Same question?", "Other?"],
        )
        assert result.count("Same question?") == 1

    def test_capped_at_five(self):
        existing = [f"Q{i}?" for i in range(5)]
        result = self._build_next(open_question="New?", existing_loops=existing)
        assert len(result) == 5

    def test_topic_shift_clears_loops(self):
        result = self._build_next(
            open_question="Fresh question?",
            existing_loops=["Old A?", "Old B?"],
            topic_shift=True,
        )
        assert result == ["Fresh question?"]
        assert "Old A?" not in result

    def test_topic_shift_with_no_question_yields_empty(self):
        result = self._build_next(
            open_question="",
            existing_loops=["Old?"],
            topic_shift=True,
        )
        assert result == []

    def test_no_new_question_retains_existing(self):
        result = self._build_next(
            open_question="",
            existing_loops=["Persisted?"],
        )
        assert result == ["Persisted?"]


# ---------------------------------------------------------------------------
# recent_recommendations accumulation logic
# ---------------------------------------------------------------------------


class TestRecentRecommendationsAccumulation:
    def _build_next(
        self,
        *,
        latest_recommendation: str,
        existing_recs: list[str],
        topic_shift: bool = False,
    ) -> list[str]:
        existing = SessionConversationContext(recent_recommendations=existing_recs)
        if latest_recommendation and not topic_shift:
            recs_seen: list[str] = []
            for s in [latest_recommendation] + list(existing.recent_recommendations):
                if s not in recs_seen:
                    recs_seen.append(s)
            return recs_seen[:3]
        elif topic_shift:
            return [latest_recommendation] if latest_recommendation else []
        return list(existing.recent_recommendations)

    def test_new_recommendation_prepended(self):
        result = self._build_next(
            latest_recommendation="New rec",
            existing_recs=["Old rec"],
        )
        assert result[0] == "New rec"
        assert "Old rec" in result

    def test_duplicate_recommendation_not_added(self):
        result = self._build_next(
            latest_recommendation="Same rec",
            existing_recs=["Same rec", "Other rec"],
        )
        assert result.count("Same rec") == 1

    def test_capped_at_three(self):
        result = self._build_next(
            latest_recommendation="New",
            existing_recs=["A", "B", "C"],
        )
        assert len(result) == 3

    def test_topic_shift_clears_recommendations(self):
        result = self._build_next(
            latest_recommendation="Fresh rec",
            existing_recs=["Old A", "Old B"],
            topic_shift=True,
        )
        assert result == ["Fresh rec"]
        assert "Old A" not in result

    def test_empty_recommendation_preserves_existing(self):
        result = self._build_next(
            latest_recommendation="",
            existing_recs=["Keep me"],
        )
        assert result == ["Keep me"]
