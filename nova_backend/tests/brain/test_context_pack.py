"""Tests for context_pack.py — prove the four Stage 4 invariants.

Invariants under test:
  1. Candidate items are never treated as confirmed (machine-readable flag, render block)
  2. Runtime truth outranks memory (sort order enforced, truncated not dropped)
  3. Budget enforcement (within_budget, items dropped with warnings when exceeded)
  4. Non-authorizing frozen dataclass (execution_performed=False, authorization_granted=False)

Additional coverage:
  - Stale detection (items older than threshold flagged with stale_memory warning)
  - Conflict detection (same title prefix → conflicting_sources warning)
  - Warning cap (max_warnings respected, WARN_TOO_MANY_WARNINGS overflow)
  - to_legacy_format() backwards compatibility
  - render_context_block() output
  - Deleted item filtering
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.brain.context_pack import (
    AUTHORITY_CANDIDATE_MEMORY,
    AUTHORITY_CONFIRMED_PROJECT_MEMORY,
    AUTHORITY_RUNTIME_TRUTH,
    DEFAULT_BUDGET_CHARS,
    DEFAULT_MAX_CANDIDATE,
    DEFAULT_MAX_CONFIRMED,
    SOURCE_CANDIDATE_MEMORY,
    SOURCE_CONFIRMED_MEMORY,
    SOURCE_RUNTIME_TRUTH,
    WARN_BUDGET_EXCEEDED,
    WARN_CONFLICTING_SOURCES,
    WARN_STALE_MEMORY,
    WARN_TOO_MANY_WARNINGS,
    ContextItem,
    ContextPack,
    ContextPackWarning,
    compose_context_pack,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_NOW = datetime.now(timezone.utc)
_FRESH_TS = (_NOW - timedelta(days=5)).isoformat()
_STALE_TS = (_NOW - timedelta(days=60)).isoformat()


def _mem(
    *,
    id: str = "1",
    title: str = "Test item",
    content: str = "some content",
    source: str = "explicit_user_save",
    updated_at: str | None = None,
    deleted: bool = False,
) -> dict:
    item = {
        "id": id,
        "title": title,
        "content": content,
        "source": source,
        "scope": "",
        "thread_name": "",
    }
    if updated_at is not None:
        item["updated_at"] = updated_at
    if deleted:
        item["deleted"] = True
    return item


def _rt(*, id: str = "rt1", title: str = "Runtime fact", content: str = "live data") -> dict:
    return {"id": id, "title": title, "content": content}


# ---------------------------------------------------------------------------
# Invariant 1 — Candidate items are never treated as confirmed
# ---------------------------------------------------------------------------

class TestCandidateItemsNotConfirmed:
    def test_auto_extracted_gets_candidate_authority(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="auto_extracted")],
        )
        assert len(pack.items) == 1
        item = pack.items[0]
        assert item.authority_label == AUTHORITY_CANDIDATE_MEMORY
        assert item.is_candidate is True
        assert item.source_label == SOURCE_CANDIDATE_MEMORY

    def test_explicit_user_save_gets_confirmed_authority(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="explicit_user_save")],
        )
        assert pack.items[0].authority_label == AUTHORITY_CONFIRMED_PROJECT_MEMORY
        assert pack.items[0].is_candidate is False
        assert pack.items[0].source_label == SOURCE_CONFIRMED_MEMORY

    def test_explicit_user_edit_gets_confirmed_authority(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="explicit_user_edit")],
        )
        assert pack.items[0].authority_label == AUTHORITY_CONFIRMED_PROJECT_MEMORY

    def test_unknown_source_gets_candidate_authority(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="")],
        )
        assert pack.items[0].authority_label == AUTHORITY_CANDIDATE_MEMORY

    def test_observed_source_gets_candidate_authority(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="observed")],
        )
        assert pack.items[0].authority_label == AUTHORITY_CANDIDATE_MEMORY

    def test_render_block_marks_candidates_as_unconfirmed(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="auto_extracted", title="Candidate thing")],
        )
        rendered = pack.render_context_block()
        assert "unconfirmed" in rendered

    def test_render_block_does_not_mark_confirmed_as_unconfirmed(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="explicit_user_save", title="Confirmed thing")],
        )
        rendered = pack.render_context_block()
        assert "unconfirmed" not in rendered

    def test_candidate_items_property_returns_only_candidates(self):
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="c1", source="auto_extracted", title="Cand"),
                _mem(id="c2", source="explicit_user_save", title="Conf"),
            ],
        )
        assert len(pack.candidate_items) == 1
        assert pack.candidate_items[0].id == "c1"

    def test_confirmed_items_property_returns_only_confirmed(self):
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="c1", source="auto_extracted", title="Cand"),
                _mem(id="c2", source="explicit_user_save", title="Conf"),
            ],
        )
        assert len(pack.confirmed_items) == 1
        assert pack.confirmed_items[0].id == "c2"

    def test_why_selected_differs_confirmed_vs_candidate(self):
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="c1", source="explicit_user_save", title="Confirmed"),
                _mem(id="c2", source="auto_extracted", title="Candidate"),
            ],
        )
        items_by_id = {i.id: i for i in pack.items}
        assert "confirmed" in items_by_id["c1"].why_selected.lower()
        assert "suggestion" in items_by_id["c2"].why_selected.lower()


# ---------------------------------------------------------------------------
# Invariant 2 — Runtime truth outranks memory (sort order + truncation)
# ---------------------------------------------------------------------------

class TestRuntimeTruthOutranksMemory:
    def test_runtime_truth_is_first_in_items(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="explicit_user_save", title="Memory item")],
            runtime_truth_items=[_rt(title="Live fact")],
        )
        assert pack.items[0].is_runtime_truth is True
        assert pack.items[0].authority_label == AUTHORITY_RUNTIME_TRUTH
        assert pack.items[0].source_label == SOURCE_RUNTIME_TRUTH

    def test_runtime_truth_sort_rank_is_zero(self):
        item = compose_context_pack("q", runtime_truth_items=[_rt()]).items[0]
        assert item.authority_rank == 0

    def test_confirmed_rank_less_than_candidate(self):
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="cand", source="auto_extracted", title="Candidate"),
                _mem(id="conf", source="explicit_user_save", title="Confirmed"),
            ],
        )
        ranks = {i.id: i.authority_rank for i in pack.items}
        assert ranks["conf"] < ranks["cand"]

    def test_runtime_truth_truncated_not_dropped_when_over_budget(self):
        big_content = "x" * 5000
        pack = compose_context_pack(
            "q",
            runtime_truth_items=[{"id": "rt1", "title": "Big fact", "content": big_content}],
            budget_chars=100,
        )
        # Item exists — not dropped
        assert len(pack.runtime_truth_items) == 1
        # Content is truncated to budget
        assert len(pack.runtime_truth_items[0].content) <= 100

    def test_runtime_truth_gets_minimal_excerpt_when_budget_zero(self):
        big_content = "z" * 5000
        pack = compose_context_pack(
            "q",
            runtime_truth_items=[
                {"id": "rt1", "title": "First RT", "content": "a" * 3000},
                {"id": "rt2", "title": "Second RT", "content": big_content},
            ],
            budget_chars=100,
        )
        # Both items present — second gets minimal 200-char excerpt
        ids = [i.id for i in pack.items]
        assert "rt2" in ids
        rt2 = next(i for i in pack.items if i.id == "rt2")
        assert len(rt2.content) <= 200

    def test_runtime_truth_items_property(self):
        pack = compose_context_pack(
            "q",
            runtime_truth_items=[_rt(id="rt1"), _rt(id="rt2")],
            memory_items=[_mem(id="m1", source="explicit_user_save")],
        )
        assert pack.runtime_truth_count == 2
        assert all(i.is_runtime_truth for i in pack.runtime_truth_items)

    def test_sort_order_rt_then_confirmed_then_candidate(self):
        pack = compose_context_pack(
            "q",
            runtime_truth_items=[_rt(id="rt1", title="RT")],
            memory_items=[
                _mem(id="cand1", source="auto_extracted", title="Cand"),
                _mem(id="conf1", source="explicit_user_save", title="Conf"),
            ],
        )
        assert pack.items[0].id == "rt1"
        assert pack.items[1].id == "conf1"
        assert pack.items[2].id == "cand1"


# ---------------------------------------------------------------------------
# Invariant 3 — Budget enforcement
# ---------------------------------------------------------------------------

class TestBudgetEnforcement:
    def test_within_budget_true_when_content_fits(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(content="short")],
            budget_chars=1000,
        )
        assert pack.within_budget is True

    def test_budget_used_tracks_actual_content(self):
        content = "hello world"
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(content=content, source="explicit_user_save")],
        )
        assert pack.budget_used == len(content)

    def test_confirmed_item_dropped_when_budget_exhausted(self):
        big_rt = "x" * 4000
        pack = compose_context_pack(
            "q",
            runtime_truth_items=[{"id": "rt1", "title": "RT", "content": big_rt}],
            memory_items=[_mem(id="m1", source="explicit_user_save", content="spillover")],
            budget_chars=4000,
        )
        # RT item consumed all budget; confirmed item should be dropped
        mem_ids = [i.id for i in pack.items if not i.is_runtime_truth]
        assert "m1" not in mem_ids
        # Warning issued
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_BUDGET_EXCEEDED in warn_types

    def test_candidate_item_dropped_when_budget_exhausted(self):
        # confirmed item uses 3999 of 4000 budget; candidate needs 20 chars — no room
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="c1", source="explicit_user_save", content="x" * 3999, title="Big confirmed"),
                _mem(id="c2", source="auto_extracted", content="a" * 20),
            ],
            budget_chars=4000,
        )
        ids = [i.id for i in pack.items]
        assert "c2" not in ids
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_BUDGET_EXCEEDED in warn_types

    def test_max_confirmed_limit_emits_warning(self):
        items = [
            _mem(id=str(i), source="explicit_user_save", title=f"Item {i}", content=f"content {i}")
            for i in range(DEFAULT_MAX_CONFIRMED + 2)
        ]
        pack = compose_context_pack("q", memory_items=items)
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_BUDGET_EXCEEDED in warn_types
        assert len([i for i in pack.items if not i.is_runtime_truth]) <= DEFAULT_MAX_CONFIRMED

    def test_max_candidate_limit_emits_warning(self):
        items = [
            _mem(id=str(i), source="auto_extracted", title=f"Cand {i}", content=f"content {i}")
            for i in range(DEFAULT_MAX_CANDIDATE + 2)
        ]
        pack = compose_context_pack("q", memory_items=items)
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_BUDGET_EXCEEDED in warn_types
        assert len(pack.candidate_items) <= DEFAULT_MAX_CANDIDATE

    def test_budget_remaining_decrements(self):
        content = "abcde"  # 5 chars
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(content=content, source="explicit_user_save")],
            budget_chars=100,
        )
        assert pack.budget_remaining == 95

    def test_budget_limit_stored(self):
        pack = compose_context_pack("q", budget_chars=2000)
        assert pack.budget_limit == 2000

    def test_budget_used_and_within_budget_accurate_at_zero_budget(self):
        # budget_chars=0: runtime truth still gets a minimal 200-char excerpt.
        # budget_used must reflect actual chars injected; within_budget must be False.
        pack = compose_context_pack(
            "q",
            runtime_truth_items=[{"id": "rt1", "title": "RT", "content": "x" * 5000}],
            budget_chars=0,
        )
        assert len(pack.runtime_truth_items) == 1
        assert pack.runtime_truth_items[0].char_count <= 200
        assert pack.budget_used > 0
        assert pack.within_budget is False


# ---------------------------------------------------------------------------
# Invariant 4 — Non-authorizing frozen dataclass
# ---------------------------------------------------------------------------

class TestNonAuthorizingInvariants:
    def test_execution_performed_is_false(self):
        pack = compose_context_pack("q")
        assert pack.execution_performed is False

    def test_authorization_granted_is_false(self):
        pack = compose_context_pack("q")
        assert pack.authorization_granted is False

    def test_cannot_set_execution_performed_via_constructor(self):
        pack = ContextPack(
            items=(),
            warnings=(),
            budget_used=0,
            budget_limit=100,
            composed_at="2026-01-01T00:00:00+00:00",
            execution_performed=True,  # attempt to set True
            authorization_granted=False,
        )
        assert pack.execution_performed is False

    def test_cannot_set_authorization_granted_via_constructor(self):
        pack = ContextPack(
            items=(),
            warnings=(),
            budget_used=0,
            budget_limit=100,
            composed_at="2026-01-01T00:00:00+00:00",
            execution_performed=False,
            authorization_granted=True,  # attempt to set True
        )
        assert pack.authorization_granted is False

    def test_pack_is_frozen(self):
        pack = compose_context_pack("q")
        with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
            pack.execution_performed = True  # type: ignore[misc]

    def test_to_dict_flags_are_false(self):
        d = compose_context_pack("q").to_dict()
        assert d["execution_performed"] is False
        assert d["authorization_granted"] is False

    def test_context_item_is_frozen(self):
        item = ContextItem(
            id="1",
            title="T",
            content="C",
            source_label=SOURCE_RUNTIME_TRUTH,
            authority_label=AUTHORITY_RUNTIME_TRUTH,
            why_selected="test",
        )
        with pytest.raises(Exception):
            item.content = "modified"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Stale detection
# ---------------------------------------------------------------------------

class TestStaleDetection:
    def test_item_older_than_threshold_flagged(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(updated_at=_STALE_TS)],
            stale_threshold_days=30,
        )
        assert pack.items[0].is_stale is True
        assert pack.items[0].stale_reason != ""

    def test_fresh_item_not_flagged(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(updated_at=_FRESH_TS)],
            stale_threshold_days=30,
        )
        assert pack.items[0].is_stale is False

    def test_stale_item_emits_stale_memory_warning(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(updated_at=_STALE_TS)],
            stale_threshold_days=30,
        )
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_STALE_MEMORY in warn_types

    def test_stale_items_property(self):
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="s1", updated_at=_STALE_TS, title="Stale"),
                _mem(id="f1", updated_at=_FRESH_TS, title="Fresh"),
            ],
        )
        assert len(pack.stale_items) == 1
        assert pack.stale_items[0].id == "s1"

    def test_no_timestamp_does_not_trigger_stale(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem()],  # no updated_at
        )
        assert pack.items[0].is_stale is False

    def test_render_block_notes_stale_items(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(updated_at=_STALE_TS, title="Old data")],
            stale_threshold_days=30,
            max_warnings=10,
        )
        rendered = pack.render_context_block()
        assert "stale" in rendered.lower()

    def test_unparseable_timestamp_emits_stale_warning(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(updated_at="not-a-date", title="Bad ts item")],
            max_warnings=5,
        )
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_STALE_MEMORY in warn_types

    def test_unparseable_timestamp_item_is_not_flagged_stale(self):
        # Item itself is not marked is_stale — we can't know its age
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(updated_at="not-a-date")],
            max_warnings=5,
        )
        assert pack.items[0].is_stale is False


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

class TestConflictDetection:
    def test_same_title_prefix_emits_conflicting_sources_warning(self):
        # Both titles share the same first 40 chars:
        # "User dietary preferences and restriction" (40 chars)
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="a", source="explicit_user_save", title="User dietary preferences and restrictions (v1)"),
                _mem(id="b", source="explicit_user_save", title="User dietary preferences and restrictions (v2)"),
            ],
            max_warnings=10,
        )
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_CONFLICTING_SOURCES in warn_types

    def test_different_title_no_conflict_warning(self):
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="a", source="explicit_user_save", title="Item Alpha"),
                _mem(id="b", source="explicit_user_save", title="Item Beta"),
            ],
        )
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_CONFLICTING_SOURCES not in warn_types

    def test_conflict_only_within_selected_items(self):
        # Titles share the same first 40 chars:
        # "Conflicting memory fact about the projec" (40 chars)
        # Item b is over budget and gets dropped; conflict detection must not fire
        # because only item a is selected.
        shared_prefix = "Conflicting memory fact about the projec"  # exactly 40 chars
        assert len(shared_prefix) == 40
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="a", source="explicit_user_save", title=shared_prefix + "t v1", content="x" * 3990),
                _mem(id="b", source="explicit_user_save", title=shared_prefix + "t v2", content="y" * 20),
            ],
            budget_chars=4000,
        )
        # b dropped due to budget — no conflict warning (only a was selected)
        ids_selected = [i.id for i in pack.items]
        assert "a" in ids_selected
        assert "b" not in ids_selected
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_CONFLICTING_SOURCES not in warn_types


# ---------------------------------------------------------------------------
# Warning cap
# ---------------------------------------------------------------------------

class TestWarningCap:
    def test_warnings_capped_at_max_warnings(self):
        # Generate many stale items to overflow warning count
        items = [
            _mem(id=str(i), source="explicit_user_save", title=f"Item {i}", updated_at=_STALE_TS)
            for i in range(10)
        ]
        pack = compose_context_pack("q", memory_items=items, max_warnings=2)
        assert len(pack.warnings) == 3  # 2 kept + 1 WARN_TOO_MANY_WARNINGS

    def test_too_many_warnings_type_added(self):
        items = [
            _mem(id=str(i), source="explicit_user_save", title=f"Item {i}", updated_at=_STALE_TS)
            for i in range(10)
        ]
        pack = compose_context_pack("q", memory_items=items, max_warnings=2)
        assert pack.warnings[-1].warning_type == WARN_TOO_MANY_WARNINGS

    def test_no_too_many_warnings_when_under_cap(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(updated_at=_STALE_TS)],
            max_warnings=5,
        )
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_TOO_MANY_WARNINGS not in warn_types

    def test_exact_max_warnings_no_overflow(self):
        items = [
            _mem(id=str(i), source="explicit_user_save", title=f"Dup title", updated_at=_STALE_TS)
            for i in range(2)
        ]
        pack = compose_context_pack("q", memory_items=items, max_warnings=10)
        # stale warning per item + possible conflict = at most 3 warnings, all under cap
        assert WARN_TOO_MANY_WARNINGS not in [w.warning_type for w in pack.warnings]


# ---------------------------------------------------------------------------
# Deleted item filtering
# ---------------------------------------------------------------------------

class TestDeletedItemFiltering:
    def test_deleted_items_excluded(self):
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="alive", deleted=False, title="Live item"),
                _mem(id="gone", deleted=True, title="Deleted item"),
            ],
        )
        ids = [i.id for i in pack.items]
        assert "alive" in ids
        assert "gone" not in ids

    def test_empty_content_items_excluded(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(content="")],
        )
        assert len(pack.items) == 0

    def test_empty_runtime_truth_content_excluded(self):
        pack = compose_context_pack(
            "q",
            runtime_truth_items=[{"id": "rt1", "title": "Empty RT", "content": ""}],
        )
        assert len(pack.items) == 0


# ---------------------------------------------------------------------------
# to_legacy_format()
# ---------------------------------------------------------------------------

class TestLegacyFormat:
    def test_returns_list_of_dicts(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="explicit_user_save")],
        )
        legacy = pack.to_legacy_format()
        assert isinstance(legacy, list)
        assert isinstance(legacy[0], dict)

    def test_legacy_format_has_required_keys(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(id="m1", title="T", content="C", source="explicit_user_save")],
        )
        item = pack.to_legacy_format()[0]
        for key in ("id", "title", "content", "scope", "thread_name", "source", "authority_label", "why_selected"):
            assert key in item, f"Missing key: {key}"

    def test_legacy_source_maps_to_source_label(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="explicit_user_save")],
        )
        item = pack.to_legacy_format()[0]
        assert item["source"] == SOURCE_CONFIRMED_MEMORY

    def test_empty_pack_returns_empty_list(self):
        pack = compose_context_pack("q")
        assert pack.to_legacy_format() == []


# ---------------------------------------------------------------------------
# render_context_block()
# ---------------------------------------------------------------------------

class TestRenderContextBlock:
    def test_empty_pack_returns_empty_string(self):
        pack = compose_context_pack("q")
        assert pack.render_context_block() == ""

    def test_authority_label_in_output(self):
        pack = compose_context_pack("q", runtime_truth_items=[_rt(title="Live", content="data")])
        rendered = pack.render_context_block()
        assert "runtime_truth" in rendered

    def test_warnings_appended_at_end(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(updated_at=_STALE_TS)],
            max_warnings=5,
        )
        rendered = pack.render_context_block()
        assert "[context warnings]" in rendered

    def test_mark_candidates_false_omits_unconfirmed_flag(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="auto_extracted")],
        )
        rendered = pack.render_context_block(mark_candidates=False)
        assert "unconfirmed" not in rendered

    def test_stale_flag_shown_in_render(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(updated_at=_STALE_TS)],
            max_warnings=10,
        )
        rendered = pack.render_context_block()
        assert "stale" in rendered.lower()


# ---------------------------------------------------------------------------
# to_dict() serialization
# ---------------------------------------------------------------------------

class TestToDictSerialization:
    def test_to_dict_has_expected_keys(self):
        pack = compose_context_pack("q", memory_items=[_mem(source="explicit_user_save")])
        d = pack.to_dict()
        for key in (
            "items", "warnings", "budget_used", "budget_limit", "budget_remaining",
            "within_budget", "candidate_count", "runtime_truth_count",
            "composed_at", "execution_performed", "authorization_granted",
        ):
            assert key in d, f"Missing key: {key}"

    def test_context_item_to_dict(self):
        item = ContextItem(
            id="x",
            title="T",
            content="C",
            source_label=SOURCE_CONFIRMED_MEMORY,
            authority_label=AUTHORITY_CONFIRMED_PROJECT_MEMORY,
            why_selected="test",
            is_stale=True,
            stale_reason="old",
        )
        d = item.to_dict()
        assert d["id"] == "x"
        assert d["is_stale"] is True
        assert d["char_count"] == 1

    def test_warning_to_dict(self):
        w = ContextPackWarning(
            warning_type=WARN_STALE_MEMORY,
            item_id="x",
            reason="old",
        )
        d = w.to_dict()
        assert d == {"warning_type": WARN_STALE_MEMORY, "item_id": "x", "reason": "old"}


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_query_no_items(self):
        pack = compose_context_pack("", memory_items=[], runtime_truth_items=[])
        assert len(pack.items) == 0

    def test_none_memory_items_no_error(self):
        pack = compose_context_pack("q", memory_items=None, runtime_truth_items=None)
        assert len(pack.items) == 0

    def test_composed_at_is_iso_string(self):
        pack = compose_context_pack("q")
        # Should parse without error
        datetime.fromisoformat(pack.composed_at)

    def test_candidate_count_property(self):
        pack = compose_context_pack(
            "q",
            memory_items=[
                _mem(id="a", source="auto_extracted", title="Cand A"),
                _mem(id="b", source="auto_extracted", title="Cand B"),
            ],
        )
        assert pack.candidate_count == DEFAULT_MAX_CANDIDATE

    def test_items_are_tuple_not_list(self):
        pack = compose_context_pack("q", memory_items=[_mem()])
        assert isinstance(pack.items, tuple)
        assert isinstance(pack.warnings, tuple)

    def test_body_field_used_as_content_fallback(self):
        pack = compose_context_pack(
            "q",
            memory_items=[{"id": "1", "title": "T", "body": "body content", "source": "explicit_user_save"}],
        )
        assert pack.items[0].content == "body content"

    def test_runtime_truth_body_field_fallback(self):
        pack = compose_context_pack(
            "q",
            runtime_truth_items=[{"id": "rt1", "title": "RT", "body": "rt body"}],
        )
        assert pack.items[0].content == "rt body"

    def test_max_confirmed_zero_drops_all_confirmed(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="explicit_user_save", title="Confirmed item")],
            max_confirmed=0,
        )
        assert len(pack.confirmed_items) == 0
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_BUDGET_EXCEEDED in warn_types

    def test_max_candidate_zero_drops_all_candidates(self):
        pack = compose_context_pack(
            "q",
            memory_items=[_mem(source="auto_extracted", title="Candidate item")],
            max_candidate=0,
        )
        assert pack.candidate_count == 0
        warn_types = [w.warning_type for w in pack.warnings]
        assert WARN_BUDGET_EXCEEDED in warn_types
