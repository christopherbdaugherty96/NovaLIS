from __future__ import annotations

import ast
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from src.actions.action_result import ActionResult
from src.brain.search_synthesis import EvidenceConfidence
from src.brain.second_brain.schemas import Confidence as SecondBrainConfidence
from src.semantic import (
    Confidence,
    DeltaKind,
    EvidenceEnvelope,
    Freshness,
    FreshnessStatus,
    IntendedState,
    ObservedState,
    OutcomeSemantics,
    OutcomeState,
    SourceIdentity,
    StateDelta,
)

OBSERVED_AT = datetime(2026, 8, 9, 14, 0, tzinfo=timezone.utc)
AS_OF = datetime(2026, 8, 9, 15, 0, tzinfo=timezone.utc)


def _evidence(claim: str = "Task remains open") -> EvidenceEnvelope:
    return EvidenceEnvelope(
        source=SourceIdentity(provider="local", service="nova"),
        freshness=Freshness(observed_at=OBSERVED_AT),
        confidence=Confidence.HIGH,
        claim=claim,
        reference="receipt:SCH-TEST",
    )


def test_source_identity_supports_local_and_external_references_without_credentials():
    local = SourceIdentity(provider="LOCAL", service="Nova")
    external = SourceIdentity(
        provider="google",
        service="tasks",
        account_id="acct-123",
        resource_id="task-456",
    )

    assert local.canonical == "local:nova"
    assert external.canonical == "google:tasks"
    assert external.account_id == "acct-123"
    assert external.resource_id == "task-456"
    assert not hasattr(external, "credential")
    assert not hasattr(external, "token")
    assert not hasattr(external, "secret")


def test_freshness_supports_age_evaluation_and_unknown_observation_time():
    freshness = Freshness(observed_at=OBSERVED_AT)
    unknown = Freshness()

    assert freshness.age_at(AS_OF) == timedelta(hours=1)
    assert freshness.evaluate(as_of=AS_OF, max_age=timedelta(hours=2)) is FreshnessStatus.FRESH
    assert freshness.evaluate(as_of=AS_OF, max_age=timedelta(minutes=30)) is FreshnessStatus.STALE
    assert unknown.age_at(AS_OF) is None
    assert unknown.evaluate(as_of=AS_OF, max_age=timedelta(days=1)) is FreshnessStatus.UNKNOWN


def test_freshness_rejects_naive_timestamps_and_domain_thresholds_are_caller_supplied():
    with pytest.raises(ValueError, match="timezone-aware"):
        Freshness(observed_at=datetime(2026, 8, 9, 14, 0))

    with pytest.raises(ValueError, match="max_age"):
        Freshness(observed_at=OBSERVED_AT).evaluate(
            as_of=AS_OF,
            max_age=timedelta(seconds=-1),
        )


def test_evidence_retains_source_timestamp_reference_and_confidence():
    evidence = _evidence()

    assert evidence.source.canonical == "local:nova"
    assert evidence.observed_at == OBSERVED_AT
    assert evidence.claim == "Task remains open"
    assert evidence.reference == "receipt:SCH-TEST"
    assert evidence.confidence is Confidence.HIGH
    assert not hasattr(evidence, "content")
    assert not hasattr(evidence, "raw_payload")

    with pytest.raises(ValueError, match="claim or opaque reference"):
        EvidenceEnvelope(
            source=SourceIdentity(provider="local", service="nova"),
            freshness=Freshness(observed_at=OBSERVED_AT),
        )


def test_shared_confidence_consolidates_existing_vocabulary_without_authority_semantics():
    assert EvidenceConfidence is Confidence
    assert SecondBrainConfidence is Confidence
    assert Confidence.UNKNOWN.value == "unknown"
    assert not hasattr(Confidence.HIGH, "verified")
    assert not hasattr(Confidence.HIGH, "authorized")


def test_observed_state_requires_evidence_when_known_and_supports_explicit_unknown():
    known = ObservedState.known_state("open", evidence=[_evidence()])
    unknown = ObservedState.unknown_state(reason="Source has not been observed.")

    assert known.known is True
    assert known.value == "open"
    assert known.evidence == (_evidence(),)
    assert unknown.known is False
    assert unknown.value is None
    assert unknown.reason == "Source has not been observed."

    with pytest.raises(ValueError, match="supporting evidence"):
        ObservedState(known=True, value="open")


def test_intended_state_is_independent_from_observation_and_grants_no_authority():
    intended = IntendedState(
        target="complete",
        reference="goal:owner-onboarding",
        target_at=AS_OF,
        condition="Owner explicitly selected this target.",
    )

    assert intended.target == "complete"
    assert intended.reference == "goal:owner-onboarding"
    assert not hasattr(intended, "authority")
    assert not hasattr(intended, "approved")
    assert not hasattr(intended, "execute")


@pytest.mark.parametrize("kind", [DeltaKind.MATCH, DeltaKind.MISMATCH])
def test_state_delta_represents_known_match_or_mismatch_without_deciding_action(kind):
    observed = ObservedState.known_state("open", evidence=[_evidence()])
    intended = IntendedState(target="complete")
    delta = StateDelta(kind=kind, observed=observed, intended=intended)

    assert delta.kind is kind
    assert not hasattr(delta, "priority")
    assert not hasattr(delta, "recommendation")
    assert not hasattr(delta, "execute")


def test_state_delta_represents_insufficient_evidence():
    observed = ObservedState.unknown_state(reason="No current observation.")
    intended = IntendedState(target="complete")
    delta = StateDelta(
        kind=DeltaKind.INSUFFICIENT_EVIDENCE,
        observed=observed,
        intended=intended,
    )

    assert delta.kind is DeltaKind.INSUFFICIENT_EVIDENCE


def test_state_delta_does_not_allow_known_difference_claims_from_unknown_state():
    with pytest.raises(ValueError, match="known observed state"):
        StateDelta(
            kind=DeltaKind.MISMATCH,
            observed=ObservedState.unknown_state(),
            intended=IntendedState(target="complete"),
        )


@pytest.mark.parametrize(
    ("metadata", "expected_state", "request_accepted", "effect_verified"),
    [
        (
            {
                "status": "completed",
                "outcome_state": "accepted_unverified",
                "launch_request_accepted": True,
                "visible_effect_verified": False,
            },
            OutcomeState.ACCEPTED_UNVERIFIED,
            True,
            False,
        ),
        (
            {
                "status": "completed",
                "outcome_state": "visible_verified",
                "launch_request_accepted": True,
                "visible_effect_verified": True,
            },
            OutcomeState.EFFECT_VERIFIED,
            True,
            True,
        ),
        (
            {"status": "failed", "outcome_state": "unknown_unverified"},
            OutcomeState.UNKNOWN_UNVERIFIED,
            None,
            False,
        ),
        (
            {
                "status": "failed",
                "outcome_state": "rejected",
                "launch_request_accepted": False,
            },
            OutcomeState.REJECTED,
            False,
            False,
        ),
        (
            {"status": "failed", "outcome_state": "failed"},
            OutcomeState.FAILED,
            None,
            False,
        ),
    ],
)
def test_outcome_adapter_preserves_pr331_distinctions(
    metadata,
    expected_state,
    request_accepted,
    effect_verified,
):
    outcome = OutcomeSemantics.from_action_metadata(metadata)

    assert outcome.state is expected_state
    assert outcome.request_accepted is request_accepted
    assert outcome.effect_verified is effect_verified


@pytest.mark.parametrize(
    ("metadata", "expected_state", "request_accepted"),
    [
        (
            {
                "status": "completed",
                "outcome_state": "visible_verified",
                "launch_request_accepted": True,
                "visible_effect_verified": False,
            },
            OutcomeState.ACCEPTED_UNVERIFIED,
            True,
        ),
        (
            {
                "status": "completed",
                "outcome_state": "visible_verified",
                "launch_request_accepted": True,
            },
            OutcomeState.ACCEPTED_UNVERIFIED,
            True,
        ),
        (
            {
                "status": "failed",
                "outcome_state": "visible_verified",
                "launch_request_accepted": True,
                "visible_effect_verified": True,
            },
            OutcomeState.FAILED,
            True,
        ),
        (
            {
                "status": "rejected",
                "outcome_state": "visible_verified",
                "launch_request_accepted": False,
                "visible_effect_verified": True,
            },
            OutcomeState.REJECTED,
            False,
        ),
    ],
)
def test_outcome_adapter_never_upgrades_missing_or_contradictory_verification(
    metadata,
    expected_state,
    request_accepted,
):
    outcome = OutcomeSemantics.from_action_metadata(metadata)

    assert outcome.state is expected_state
    assert outcome.request_accepted is request_accepted
    assert outcome.effect_verified is False


@pytest.mark.parametrize(
    "metadata",
    [
        {
            "status": "completed",
            "success": False,
            "outcome_state": "visible_verified",
            "launch_request_accepted": True,
        },
        {
            "status": "completed",
            "success": False,
            "outcome_state": "visible_verified",
            "launch_request_accepted": True,
            "visible_effect_verified": True,
        },
        {
            "status": "failed",
            "success": True,
            "outcome_state": "visible_verified",
            "launch_request_accepted": True,
            "visible_effect_verified": True,
        },
    ],
)
def test_explicit_failure_prevents_verified_effect(metadata):
    outcome = OutcomeSemantics.from_action_metadata(metadata)

    assert outcome.state is OutcomeState.FAILED
    assert outcome.effect_verified is False


@pytest.mark.parametrize(
    ("metadata", "expected_state", "request_accepted"),
    [
        (
            {
                "status": "completed",
                "outcome_state": "accepted_unverified",
                "launch_request_accepted": False,
            },
            OutcomeState.REJECTED,
            False,
        ),
        (
            {
                "status": "failed",
                "outcome_state": "accepted_unverified",
            },
            OutcomeState.FAILED,
            None,
        ),
        (
            {
                "status": "completed",
                "success": False,
                "outcome_state": "accepted_unverified",
            },
            OutcomeState.FAILED,
            None,
        ),
        (
            {
                "status": "rejected",
                "outcome_state": "accepted_unverified",
            },
            OutcomeState.REJECTED,
            False,
        ),
        (
            {
                "status": "completed",
                "outcome_state": "accepted_unverified",
            },
            OutcomeState.UNKNOWN_UNVERIFIED,
            None,
        ),
        (
            {
                "status": "completed",
                "outcome_state": "accepted_unverified",
                "launch_request_accepted": True,
            },
            OutcomeState.ACCEPTED_UNVERIFIED,
            True,
        ),
    ],
)
def test_accepted_label_never_upgrades_missing_or_contradictory_acceptance(
    metadata,
    expected_state,
    request_accepted,
):
    outcome = OutcomeSemantics.from_action_metadata(metadata)

    assert outcome.state is expected_state
    assert outcome.request_accepted is request_accepted
    assert outcome.effect_verified is False


def test_explicit_acceptance_is_preserved_when_execution_later_fails():
    outcome = OutcomeSemantics.from_action_metadata(
        {
            "status": "failed",
            "success": False,
            "outcome_state": "accepted_unverified",
            "launch_request_accepted": True,
        }
    )

    assert outcome.state is OutcomeState.FAILED
    assert outcome.request_accepted is True
    assert outcome.effect_verified is False


@pytest.mark.parametrize("positive_label", [False, True])
def test_action_result_refusal_preserves_rejection_with_or_without_positive_label(
    positive_label,
):
    metadata = ActionResult.refusal("Action is not authorized.").to_contract_dict()
    if positive_label:
        metadata.update(
            {
                "outcome_state": "accepted_unverified",
                "launch_request_accepted": True,
            }
        )

    outcome = OutcomeSemantics.from_action_metadata(metadata)

    assert outcome.state is OutcomeState.REJECTED
    assert outcome.request_accepted is False
    assert outcome.effect_verified is False


def test_timed_out_refusal_preserves_unknown_outcome():
    metadata = ActionResult.refusal(
        "The final outcome could not be verified.",
        outcome_reason="timed_out_outcome_unknown",
    ).to_contract_dict()

    outcome = OutcomeSemantics.from_action_metadata(metadata)

    assert outcome.state is OutcomeState.UNKNOWN_UNVERIFIED
    assert outcome.request_accepted is None
    assert outcome.effect_verified is False
    assert outcome.reason == "timed_out_outcome_unknown"


@pytest.mark.parametrize(
    "metadata",
    [
        ActionResult.failure("Action failed.").to_contract_dict(),
        {"status": "completed", "success": False},
    ],
)
def test_unlabeled_explicit_failure_maps_to_failed(metadata):
    outcome = OutcomeSemantics.from_action_metadata(metadata)

    assert outcome.state is OutcomeState.FAILED
    assert outcome.effect_verified is False


@pytest.mark.parametrize(
    "metadata",
    [
        {"status": "failed", "success": False, "outcome_state": "cancelled"},
        {"status": "failed", "success": True, "outcome_state": "future_state"},
        {"status": "completed", "success": False, "outcome_state": "future_state"},
    ],
)
def test_unrecognized_outcome_label_cannot_suppress_explicit_failure(metadata):
    outcome = OutcomeSemantics.from_action_metadata(metadata)

    assert outcome.state is OutcomeState.FAILED
    assert outcome.effect_verified is False


def test_unrecognized_positive_outcome_remains_conservatively_unknown():
    outcome = OutcomeSemantics.from_action_metadata(
        {
            "status": "completed",
            "success": True,
            "outcome_state": "future_state",
        }
    )

    assert outcome.state is OutcomeState.UNKNOWN_UNVERIFIED
    assert outcome.effect_verified is False


@pytest.mark.parametrize("authority_class", ["read_only_local", "read_only_network"])
def test_successful_completed_read_has_its_own_non_effect_outcome(authority_class):
    outcome = OutcomeSemantics.from_action_metadata(
        {
            "status": "completed",
            "success": True,
            "authority_class": authority_class,
            "external_effect": False,
        }
    )

    assert outcome.state is OutcomeState.READ_SUCCEEDED
    assert outcome.lifecycle_completed is True
    assert outcome.request_accepted is True
    assert outcome.effect_verified is False


def test_successful_completed_write_without_effect_proof_remains_unknown():
    outcome = OutcomeSemantics.from_action_metadata(
        {
            "status": "completed",
            "success": True,
            "authority_class": "persistent_change",
        }
    )

    assert outcome.state is OutcomeState.UNKNOWN_UNVERIFIED
    assert outcome.effect_verified is False


def test_explicit_unknown_read_outcome_is_not_upgraded_to_success():
    outcome = OutcomeSemantics.from_action_metadata(
        {
            "status": "completed",
            "success": True,
            "authority_class": "read_only_local",
            "outcome_state": "unknown_unverified",
        }
    )

    assert outcome.state is OutcomeState.UNKNOWN_UNVERIFIED
    assert outcome.effect_verified is False


@pytest.mark.parametrize(
    ("raw_state", "expected_state"),
    [
        ("failed", OutcomeState.FAILED),
        ("unknown_unverified", OutcomeState.UNKNOWN_UNVERIFIED),
        ("", OutcomeState.UNKNOWN_UNVERIFIED),
    ],
)
def test_non_verified_states_clear_contradictory_verification_evidence(
    raw_state,
    expected_state,
):
    outcome = OutcomeSemantics.from_action_metadata(
        {
            "status": "completed",
            "outcome_state": raw_state,
            "visible_effect_verified": True,
        }
    )

    assert outcome.state is expected_state
    assert outcome.effect_verified is False


@pytest.mark.parametrize(
    ("structured_data", "expected_state", "effect_verified"),
    [
        (
            {
                "outcome_state": "accepted_unverified",
                "launch_request_accepted": True,
                "visible_effect_verified": False,
            },
            OutcomeState.ACCEPTED_UNVERIFIED,
            False,
        ),
        (
            {
                "outcome_state": "visible_verified",
                "launch_request_accepted": True,
                "visible_effect_verified": True,
            },
            OutcomeState.EFFECT_VERIFIED,
            True,
        ),
    ],
)
def test_action_result_structured_outcome_metadata_is_adapted(
    structured_data,
    expected_state,
    effect_verified,
):
    metadata = ActionResult.ok(
        "Action result.",
        data=structured_data,
    ).to_contract_dict()

    outcome = OutcomeSemantics.from_action_metadata(metadata)

    assert outcome.state is expected_state
    assert outcome.request_accepted is True
    assert outcome.effect_verified is effect_verified


def test_top_level_receipt_metadata_takes_precedence_over_structured_action_data():
    metadata = ActionResult.ok(
        "Action result.",
        data={
            "outcome_state": "visible_verified",
            "launch_request_accepted": True,
            "visible_effect_verified": True,
        },
    ).to_contract_dict()
    metadata.update(
        {
            "outcome_state": "accepted_unverified",
            "launch_request_accepted": True,
            "visible_effect_verified": False,
        }
    )

    outcome = OutcomeSemantics.from_action_metadata(metadata)

    assert outcome.state is OutcomeState.ACCEPTED_UNVERIFIED
    assert outcome.request_accepted is True
    assert outcome.effect_verified is False


def test_outcome_states_and_lifecycle_completion_remain_independent():
    accepted = OutcomeSemantics.from_action_metadata(
        {
            "status": "completed",
            "outcome_state": "accepted_unverified",
            "launch_request_accepted": True,
        }
    )
    unknown = OutcomeSemantics.from_action_metadata(
        {"status": "failed", "outcome_state": "unknown_unverified"}
    )
    rejected = OutcomeSemantics.from_action_metadata(
        {"status": "failed", "outcome_state": "rejected"}
    )
    failed = OutcomeSemantics.from_action_metadata(
        {"status": "failed", "outcome_state": "failed"}
    )

    assert accepted.state is not OutcomeState.EFFECT_VERIFIED
    assert accepted.lifecycle_completed is True
    assert accepted.effect_verified is False
    assert unknown.state is not rejected.state
    assert failed.state is not rejected.state


def test_partial_failure_is_available_without_changing_runtime_lifecycle():
    outcome = OutcomeSemantics.from_action_metadata(
        {
            "status": "completed",
            "outcome_state": "partial_failure",
            "partial_failure": True,
        }
    )

    assert outcome.state is OutcomeState.PARTIAL_FAILURE
    assert outcome.partial_failure is True
    assert outcome.lifecycle_completed is True


def test_semantic_contract_module_has_stdlib_only_dependencies_and_no_effect_methods():
    import src.semantic.contracts as contracts

    source = Path(contracts.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    imported_roots.update(
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )

    assert imported_roots <= {
        "__future__",
        "collections",
        "dataclasses",
        "datetime",
        "enum",
        "re",
        "typing",
    }
    method_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    assert not method_names.intersection(
        {
            "authorize",
            "execute",
            "invoke_capability",
            "persist",
            "save",
            "schedule",
            "send",
        }
    )
