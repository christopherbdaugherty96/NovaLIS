import pytest

from src.openclaw.read_only_workflow_proof import (
    ProjectForemanBriefInput,
    ProjectForemanBriefProof,
    ReadOnlyOpenClawWorkflowReceipt,
    build_project_foreman_brief_proof,
)


def _sample_input(**overrides):
    payload = {
        "project_name": "NovaLIS Sample Project",
        "allowed_input_scope": ("sample_project_notes", "sample_repo_map"),
        "project_summary": "A local sample workspace used to prove a read-only OpenClaw mediator path.",
        "current_focus": ("Keep the workflow proof read-only.", "Preserve mediator boundaries."),
        "known_blockers": ("Browser/computer-use remains blocked.",),
        "recent_decisions": ("Use caller-provided sample input only.",),
        "next_safe_steps": ("Review proof payload.", "Do not start broad automation."),
    }
    payload.update(overrides)
    return ProjectForemanBriefInput(**payload)


def test_read_only_project_foreman_brief_with_sample_input_succeeds_as_proof_artifact():
    proof = build_project_foreman_brief_proof(_sample_input())

    assert proof.workflow_name == "Project Foreman Brief"
    assert proof.mediator_decision.decision == "preview_allowed"
    assert proof.mediator_decision.preview_allowed is True
    assert proof.proof_output_rendered is True
    assert "Project Foreman Brief: NovaLIS Sample Project" in proof.brief
    assert "caller-provided sample input only" in proof.brief
    assert proof.execution_performed is False
    assert proof.authorization_granted is False


def test_missing_allowed_input_scope_is_blocked():
    proof = build_project_foreman_brief_proof(_sample_input(allowed_input_scope=()))

    assert proof.mediator_decision.decision == "blocked"
    assert proof.proof_output_rendered is False
    assert proof.brief == ""
    assert "missing_allowed_input_scope" in proof.mediator_decision.blocked_reasons


def test_browser_request_is_blocked():
    proof = build_project_foreman_brief_proof(_sample_input(), browser_use=True)

    assert proof.mediator_decision.decision == "blocked"
    assert "browser_use_blocked" in proof.mediator_decision.blocked_reasons


def test_filesystem_write_request_is_blocked():
    proof = build_project_foreman_brief_proof(_sample_input(), filesystem_write=True)

    assert proof.mediator_decision.decision == "blocked"
    assert "filesystem_write_blocked" in proof.mediator_decision.blocked_reasons


@pytest.mark.parametrize(
    ("flag", "reason"),
    [
        ("external_write", "external_write_blocked"),
        ("email_action", "email_action_blocked"),
        ("calendar_action", "calendar_action_blocked"),
        ("shopify_action", "shopify_action_blocked"),
        ("account_action", "account_action_blocked"),
    ],
)
def test_external_and_account_requests_are_blocked(flag, reason):
    proof = build_project_foreman_brief_proof(_sample_input(), **{flag: True})

    assert proof.mediator_decision.decision == "blocked"
    assert reason in proof.mediator_decision.blocked_reasons


def test_direct_cap63_shortcut_is_blocked():
    proof = build_project_foreman_brief_proof(_sample_input(), direct_cap63_shortcut=True)

    assert proof.mediator_decision.decision == "blocked"
    assert "direct_cap63_shortcut_blocked" in proof.mediator_decision.blocked_reasons


def test_receipt_includes_did_happen_and_did_not_happen():
    proof = build_project_foreman_brief_proof(_sample_input())

    assert "OpenClawMediator evaluated the Project Foreman Brief envelope." in proof.receipt.did_happen
    assert "A deterministic read-only proof output was rendered from caller-provided sample input." in proof.receipt.did_happen
    assert "OpenClaw was not executed." in proof.receipt.did_not_happen
    assert "No Governor call was made." in proof.receipt.did_not_happen
    assert "No capability was called." in proof.receipt.did_not_happen
    assert "No Cap 63 shortcut was used." in proof.receipt.did_not_happen
    assert "No network request was made." in proof.receipt.did_not_happen


def test_no_openclaw_governor_capability_or_side_effect_flags():
    proof = build_project_foreman_brief_proof(_sample_input())

    assert proof.mediator_decision.openclaw_called is False
    assert proof.mediator_decision.governor_called is False
    assert proof.mediator_decision.capabilities_called is False
    assert proof.mediator_decision.filesystem_touched is False
    assert proof.mediator_decision.browser_opened is False
    assert proof.mediator_decision.network_called is False
    assert proof.receipt.openclaw_called is False
    assert proof.receipt.governor_called is False
    assert proof.receipt.capabilities_called is False
    assert proof.receipt.filesystem_write_performed is False
    assert proof.receipt.browser_opened is False
    assert proof.receipt.network_called is False


def test_proof_and_receipt_enforce_no_execution_or_authorization():
    sample = _sample_input()
    proof = build_project_foreman_brief_proof(sample)

    with pytest.raises(ValueError, match="must not record OpenClaw execution"):
        ProjectForemanBriefProof(
            workflow_name=proof.workflow_name,
            input=sample,
            mediator_envelope=proof.mediator_envelope,
            mediator_decision=proof.mediator_decision,
            mediator_receipt=proof.mediator_receipt,
            brief=proof.brief,
            receipt=proof.receipt,
            proof_output_rendered=True,
            execution_performed=True,
        )
    with pytest.raises(ValueError, match="must not grant authorization"):
        ReadOnlyOpenClawWorkflowReceipt(
            receipt_type="first_read_only_openclaw_workflow_proof",
            workflow_name="Project Foreman Brief",
            mediator_decision="preview_allowed",
            did_happen=("A receipt was constructed.",),
            did_not_happen=("OpenClaw was not executed.",),
            non_action_statement="proof only",
            authorization_granted=True,
        )


def test_payload_contains_no_execution_handles():
    proof = build_project_foreman_brief_proof(_sample_input())
    payload = proof.to_dict()
    serialized = str(payload).lower()

    assert "run_template" not in serialized
    assert "run_goal" not in serialized
    assert "openclaw_execute" not in serialized
    assert payload["mediator_decision"]["openclaw_called"] is False
    assert payload["mediator_decision"]["governor_called"] is False
    assert payload["mediator_decision"]["capabilities_called"] is False
