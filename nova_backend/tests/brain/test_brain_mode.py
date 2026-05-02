"""Tests for brain_mode.py — prove the four Stage 5 invariants.

Invariants under test:
  1. Brainstorm mode never mutates repo (may_mutate_repo=False, cannot list)
  2. Repo-review mode requires context before recommending
  3. Implementation mode stays focused (explicit scope boundary in cannot list)
  4. BrainTrace never exposes private reasoning or authorizes action

Additional coverage:
  - All seven modes have registered contracts
  - classify_mode() returns expected mode for representative queries
  - ModeContract.to_dict() and BrainTrace.to_dict() serialization
  - get_contract() fallback behavior
  - compose_brain_trace() produces valid trace with correct fields
  - Non-authorizing frozen dataclasses (execution_performed, authorization_granted)
"""

from __future__ import annotations

import pytest

from src.brain.brain_mode import (
    BrainMode,
    BrainTrace,
    CONTRACTS,
    ModeClassification,
    ModeContract,
    classify_mode,
    compose_brain_trace,
    get_contract,
)


# ---------------------------------------------------------------------------
# Invariant 1 — Brainstorm mode never mutates repo
# ---------------------------------------------------------------------------

class TestBrainstormNeverMutatesRepo:
    def test_brainstorm_contract_may_mutate_repo_false(self):
        contract = get_contract(BrainMode.BRAINSTORM)
        assert contract.may_mutate_repo is False

    def test_brainstorm_cannot_includes_write_or_modify_files(self):
        contract = get_contract(BrainMode.BRAINSTORM)
        cannot_text = " ".join(contract.cannot).lower()
        assert "write" in cannot_text or "modify" in cannot_text

    def test_brainstorm_cannot_includes_commit_or_push(self):
        contract = get_contract(BrainMode.BRAINSTORM)
        cannot_text = " ".join(contract.cannot).lower()
        assert "commit" in cannot_text or "push" in cannot_text

    def test_brainstorm_cannot_produce_code(self):
        contract = get_contract(BrainMode.BRAINSTORM)
        assert contract.may_produce_code is False

    def test_brainstorm_can_produce_plan(self):
        contract = get_contract(BrainMode.BRAINSTORM)
        assert contract.may_produce_plan is True

    def test_brainstorm_cannot_authorize_capabilities(self):
        contract = get_contract(BrainMode.BRAINSTORM)
        cannot_text = " ".join(contract.cannot).lower()
        assert "authorize" in cannot_text

    def test_brainstorm_output_not_treated_as_confirmed_plan(self):
        contract = get_contract(BrainMode.BRAINSTORM)
        cannot_text = " ".join(contract.cannot).lower()
        assert "confirmed plan" in cannot_text

    def test_casual_mode_also_cannot_mutate_repo(self):
        assert get_contract(BrainMode.CASUAL).may_mutate_repo is False

    def test_planning_mode_cannot_mutate_repo(self):
        assert get_contract(BrainMode.PLANNING).may_mutate_repo is False

    def test_action_review_mode_cannot_mutate_repo(self):
        assert get_contract(BrainMode.ACTION_REVIEW).may_mutate_repo is False

    def test_unknown_mode_cannot_mutate_repo(self):
        assert get_contract(BrainMode.UNKNOWN).may_mutate_repo is False

    def test_only_implementation_and_merge_may_mutate_repo(self):
        mutating = [m for m, c in CONTRACTS.items() if c.may_mutate_repo]
        assert set(mutating) == {BrainMode.IMPLEMENTATION, BrainMode.MERGE}


# ---------------------------------------------------------------------------
# Invariant 2 — Repo-review mode requires context before recommending
# ---------------------------------------------------------------------------

class TestRepoReviewRequiresContext:
    def test_repo_review_requires_context_before_recommending(self):
        contract = get_contract(BrainMode.REPO_REVIEW)
        assert contract.requires_context_before_recommending is True

    def test_repo_review_cannot_recommend_without_reading_state(self):
        contract = get_contract(BrainMode.REPO_REVIEW)
        cannot_text = " ".join(contract.cannot).lower()
        assert "without" in cannot_text

    def test_repo_review_cannot_mutate_repo(self):
        assert get_contract(BrainMode.REPO_REVIEW).may_mutate_repo is False

    def test_repo_review_may_produce_review(self):
        assert get_contract(BrainMode.REPO_REVIEW).may_produce_review is True

    def test_repo_review_cannot_produce_code(self):
        assert get_contract(BrainMode.REPO_REVIEW).may_produce_code is False

    def test_action_review_also_requires_context(self):
        assert get_contract(BrainMode.ACTION_REVIEW).requires_context_before_recommending is True

    def test_implementation_also_requires_context(self):
        assert get_contract(BrainMode.IMPLEMENTATION).requires_context_before_recommending is True

    def test_merge_also_requires_context(self):
        assert get_contract(BrainMode.MERGE).requires_context_before_recommending is True

    def test_brainstorm_does_not_require_context(self):
        assert get_contract(BrainMode.BRAINSTORM).requires_context_before_recommending is False

    def test_planning_does_not_require_context(self):
        assert get_contract(BrainMode.PLANNING).requires_context_before_recommending is False


# ---------------------------------------------------------------------------
# Invariant 3 — Implementation mode stays focused (no scope creep)
# ---------------------------------------------------------------------------

class TestImplementationStaysFocused:
    def test_implementation_cannot_expand_scope_unilaterally(self):
        contract = get_contract(BrainMode.IMPLEMENTATION)
        cannot_text = " ".join(contract.cannot).lower()
        assert "scope" in cannot_text

    def test_implementation_cannot_merge_unilaterally(self):
        contract = get_contract(BrainMode.IMPLEMENTATION)
        cannot_text = " ".join(contract.cannot).lower()
        assert "merge" in cannot_text or "main" in cannot_text

    def test_implementation_cannot_add_features_beyond_task(self):
        contract = get_contract(BrainMode.IMPLEMENTATION)
        cannot_text = " ".join(contract.cannot).lower()
        assert "beyond" in cannot_text

    def test_implementation_may_produce_code(self):
        assert get_contract(BrainMode.IMPLEMENTATION).may_produce_code is True

    def test_implementation_may_mutate_repo(self):
        assert get_contract(BrainMode.IMPLEMENTATION).may_mutate_repo is True

    def test_implementation_cannot_authorize_capabilities_outside_task(self):
        contract = get_contract(BrainMode.IMPLEMENTATION)
        cannot_text = " ".join(contract.cannot).lower()
        assert "authorize" in cannot_text

    def test_merge_cannot_force_push_main(self):
        contract = get_contract(BrainMode.MERGE)
        cannot_text = " ".join(contract.cannot).lower()
        assert "force" in cannot_text

    def test_merge_cannot_bypass_review_hooks(self):
        contract = get_contract(BrainMode.MERGE)
        cannot_text = " ".join(contract.cannot).lower()
        assert "hook" in cannot_text or "bypass" in cannot_text


# ---------------------------------------------------------------------------
# Invariant 4 — BrainTrace never exposes private reasoning or authorizes
# ---------------------------------------------------------------------------

class TestBrainTraceNonAuthorizing:
    def test_trace_execution_performed_is_false(self):
        trace = compose_brain_trace(mode=BrainMode.BRAINSTORM)
        assert trace.execution_performed is False

    def test_trace_authorization_granted_is_false(self):
        trace = compose_brain_trace(mode=BrainMode.BRAINSTORM)
        assert trace.authorization_granted is False

    def test_trace_private_reasoning_exposed_is_false(self):
        trace = compose_brain_trace(mode=BrainMode.BRAINSTORM)
        assert trace.private_reasoning_exposed is False

    def test_cannot_set_execution_performed_true_via_constructor(self):
        trace = BrainTrace(
            trace_id="BT-TEST",
            mode=BrainMode.REPO_REVIEW,
            composed_at="2026-01-01T00:00:00+00:00",
            context_sources=(),
            decision_notes=(),
            warnings=(),
            execution_performed=True,
        )
        assert trace.execution_performed is False

    def test_cannot_set_authorization_granted_true_via_constructor(self):
        trace = BrainTrace(
            trace_id="BT-TEST",
            mode=BrainMode.REPO_REVIEW,
            composed_at="2026-01-01T00:00:00+00:00",
            context_sources=(),
            decision_notes=(),
            warnings=(),
            authorization_granted=True,
        )
        assert trace.authorization_granted is False

    def test_cannot_set_private_reasoning_exposed_true(self):
        trace = BrainTrace(
            trace_id="BT-TEST",
            mode=BrainMode.IMPLEMENTATION,
            composed_at="2026-01-01T00:00:00+00:00",
            context_sources=(),
            decision_notes=(),
            warnings=(),
            private_reasoning_exposed=True,
        )
        assert trace.private_reasoning_exposed is False

    def test_trace_is_frozen(self):
        trace = compose_brain_trace(mode=BrainMode.PLANNING)
        with pytest.raises(Exception):
            trace.execution_performed = True  # type: ignore[misc]

    def test_trace_to_dict_flags_are_false(self):
        d = compose_brain_trace(mode=BrainMode.PLANNING).to_dict()
        assert d["execution_performed"] is False
        assert d["authorization_granted"] is False
        assert d["private_reasoning_exposed"] is False

    def test_action_review_cannot_execute_reviewed_action(self):
        contract = get_contract(BrainMode.ACTION_REVIEW)
        cannot_text = " ".join(contract.cannot).lower()
        assert "execute" in cannot_text

    def test_action_review_cannot_approve_on_behalf_of_user(self):
        contract = get_contract(BrainMode.ACTION_REVIEW)
        cannot_text = " ".join(contract.cannot).lower()
        assert "approve" in cannot_text or "on behalf" in cannot_text

    def test_action_review_output_not_authorization(self):
        contract = get_contract(BrainMode.ACTION_REVIEW)
        cannot_text = " ".join(contract.cannot).lower()
        assert "authorization" in cannot_text


# ---------------------------------------------------------------------------
# Contract registry completeness
# ---------------------------------------------------------------------------

class TestContractRegistry:
    def test_all_modes_have_contracts(self):
        for mode in BrainMode:
            assert mode in CONTRACTS, f"No contract registered for BrainMode.{mode}"

    def test_get_contract_returns_correct_mode(self):
        for mode in BrainMode:
            assert get_contract(mode).mode == mode

    def test_all_contracts_have_non_empty_can(self):
        for mode, contract in CONTRACTS.items():
            assert len(contract.can) > 0, f"{mode} has empty can list"

    def test_all_contracts_have_non_empty_cannot(self):
        for mode, contract in CONTRACTS.items():
            assert len(contract.cannot) > 0, f"{mode} has empty cannot list"

    def test_all_contracts_have_description(self):
        for mode, contract in CONTRACTS.items():
            assert contract.description.strip(), f"{mode} has empty description"

    def test_contract_to_dict_has_required_keys(self):
        d = get_contract(BrainMode.BRAINSTORM).to_dict()
        for key in (
            "mode", "description", "can", "cannot",
            "requires_context_before_recommending",
            "may_produce_code", "may_produce_plan",
            "may_produce_review", "may_mutate_repo",
        ):
            assert key in d, f"Missing key: {key}"

    def test_contract_can_and_cannot_are_lists_in_dict(self):
        d = get_contract(BrainMode.IMPLEMENTATION).to_dict()
        assert isinstance(d["can"], list)
        assert isinstance(d["cannot"], list)


# ---------------------------------------------------------------------------
# classify_mode()
# ---------------------------------------------------------------------------

class TestClassifyMode:
    def test_brainstorm_query_classified(self):
        result = classify_mode("brainstorm ideas for the new feature")
        assert result.mode == BrainMode.BRAINSTORM

    def test_what_if_classified_as_brainstorm(self):
        result = classify_mode("what if we used a different approach here")
        assert result.mode == BrainMode.BRAINSTORM

    def test_review_query_classified(self):
        result = classify_mode("review the current implementation of context_pack")
        assert result.mode == BrainMode.REPO_REVIEW

    def test_audit_classified_as_repo_review(self):
        result = classify_mode("audit the governance test suite")
        assert result.mode == BrainMode.REPO_REVIEW

    def test_implement_query_classified(self):
        result = classify_mode("implement the stale detection feature")
        assert result.mode == BrainMode.IMPLEMENTATION

    def test_fix_query_classified_as_implementation(self):
        result = classify_mode("fix the budget_remaining off-by-one bug")
        assert result.mode == BrainMode.IMPLEMENTATION

    def test_merge_query_classified(self):
        result = classify_mode("merge the PR")
        assert result.mode == BrainMode.MERGE

    def test_pr_number_classified_as_merge(self):
        result = classify_mode("is PR #83 ready to merge?")
        assert result.mode == BrainMode.MERGE

    def test_plan_query_classified(self):
        result = classify_mode("plan the next phase of the project")
        assert result.mode == BrainMode.PLANNING

    def test_how_should_we_classified_as_planning(self):
        result = classify_mode("how should we approach the brain discipline stage")
        assert result.mode == BrainMode.PLANNING

    def test_should_i_run_classified_as_action_review(self):
        result = classify_mode("should I run this migration now")
        assert result.mode == BrainMode.ACTION_REVIEW

    def test_is_it_safe_classified_as_action_review(self):
        result = classify_mode("is it safe to force push main here")
        assert result.mode == BrainMode.ACTION_REVIEW

    def test_greeting_classified_as_casual(self):
        result = classify_mode("hi")
        assert result.mode == BrainMode.CASUAL

    def test_thanks_classified_as_casual(self):
        result = classify_mode("thanks")
        assert result.mode == BrainMode.CASUAL

    def test_empty_query_classified_as_unknown(self):
        result = classify_mode("")
        assert result.mode == BrainMode.UNKNOWN

    def test_unrecognized_query_classified_as_unknown(self):
        result = classify_mode("xyzzy wibble frobnicate")
        assert result.mode == BrainMode.UNKNOWN

    def test_classification_returns_contract(self):
        result = classify_mode("brainstorm some options")
        assert isinstance(result.contract, ModeContract)
        assert result.contract.mode == result.mode

    def test_classification_confidence_is_0_to_1(self):
        for query in [
            "brainstorm", "review the code", "implement this", "merge PR",
            "plan the roadmap", "should I delete this", "hi", "xyzzy"
        ]:
            result = classify_mode(query)
            assert 0.0 <= result.confidence <= 1.0, f"Bad confidence for: {query!r}"

    def test_unknown_confidence_is_zero(self):
        result = classify_mode("xyzzy wibble frobnicate")
        assert result.confidence == 0.0

    def test_classification_to_dict(self):
        d = classify_mode("review the auth module").to_dict()
        for key in ("mode", "confidence", "signal", "contract"):
            assert key in d


# ---------------------------------------------------------------------------
# compose_brain_trace()
# ---------------------------------------------------------------------------

class TestComposeBrainTrace:
    def test_trace_has_trace_id(self):
        trace = compose_brain_trace(mode=BrainMode.REPO_REVIEW)
        assert trace.trace_id.startswith("BT-")
        assert len(trace.trace_id) > 3

    def test_trace_id_is_unique(self):
        ids = {compose_brain_trace(mode=BrainMode.CASUAL).trace_id for _ in range(10)}
        assert len(ids) == 10

    def test_trace_mode_matches(self):
        trace = compose_brain_trace(mode=BrainMode.IMPLEMENTATION)
        assert trace.mode == BrainMode.IMPLEMENTATION

    def test_trace_composed_at_is_iso_string(self):
        from datetime import datetime
        trace = compose_brain_trace(mode=BrainMode.PLANNING)
        datetime.fromisoformat(trace.composed_at)

    def test_trace_context_sources_stored(self):
        trace = compose_brain_trace(
            mode=BrainMode.REPO_REVIEW,
            context_sources=["runtime_truth", "confirmed_project_memory"],
        )
        assert "runtime_truth" in trace.context_sources
        assert "confirmed_project_memory" in trace.context_sources

    def test_trace_decision_notes_stored(self):
        trace = compose_brain_trace(
            mode=BrainMode.IMPLEMENTATION,
            decision_notes=["scope limited to context_pack.py", "no new capabilities required"],
        )
        assert len(trace.decision_notes) == 2

    def test_trace_warnings_stored(self):
        trace = compose_brain_trace(
            mode=BrainMode.MERGE,
            warnings=["CI not yet confirmed"],
        )
        assert "CI not yet confirmed" in trace.warnings

    def test_trace_sources_are_tuples(self):
        trace = compose_brain_trace(mode=BrainMode.BRAINSTORM)
        assert isinstance(trace.context_sources, tuple)
        assert isinstance(trace.decision_notes, tuple)
        assert isinstance(trace.warnings, tuple)

    def test_trace_none_inputs_produce_empty_tuples(self):
        trace = compose_brain_trace(
            mode=BrainMode.BRAINSTORM,
            context_sources=None,
            decision_notes=None,
            warnings=None,
        )
        assert trace.context_sources == ()
        assert trace.decision_notes == ()
        assert trace.warnings == ()

    def test_trace_to_dict_has_required_keys(self):
        d = compose_brain_trace(mode=BrainMode.CASUAL).to_dict()
        for key in (
            "trace_id", "mode", "composed_at",
            "context_sources", "decision_notes", "warnings",
            "execution_performed", "authorization_granted", "private_reasoning_exposed",
        ):
            assert key in d, f"Missing key: {key}"

    def test_trace_to_dict_sources_are_lists(self):
        d = compose_brain_trace(
            mode=BrainMode.REPO_REVIEW,
            context_sources=["runtime_truth"],
        ).to_dict()
        assert isinstance(d["context_sources"], list)
        assert isinstance(d["decision_notes"], list)
        assert isinstance(d["warnings"], list)
