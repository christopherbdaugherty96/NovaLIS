import pytest

from src.openclaw.openclaw_mediator import (
    OpenClawDelegationEnvelope,
    OpenClawMediator,
    OpenClawMediatorDecision,
    OpenClawMediatorReceipt,
)


def _mediator() -> OpenClawMediator:
    return OpenClawMediator()


def _read_only_envelope(**overrides):
    payload = {
        "request_text": "Prepare a read-only project snapshot preview from sample docs.",
        "requested_actions": ("summarize provided project notes",),
        "allowed_input_scope": ("sample_project_notes", "repo_map_excerpt"),
        "read_only": True,
    }
    payload.update(overrides)
    return OpenClawDelegationEnvelope(**payload)


def test_read_only_local_sample_request_receives_preview_decision_only():
    decision, receipt = _mediator().evaluate_with_receipt(_read_only_envelope())

    assert decision.decision == "preview_allowed"
    assert decision.preview_allowed is True
    assert decision.execution_performed is False
    assert decision.authorization_granted is False
    assert decision.openclaw_called is False
    assert decision.governor_called is False
    assert decision.capabilities_called is False
    assert decision.filesystem_touched is False
    assert decision.browser_opened is False
    assert decision.network_called is False
    assert "prepare a read-only delegation preview" in decision.allowed_preview_actions
    assert "direct_cap63_shortcut" in decision.blocked_actions
    assert receipt.execution_performed is False
    assert receipt.authorization_granted is False


@pytest.mark.parametrize(
    ("flag", "reason"),
    [
        ("browser_use", "browser_use_blocked"),
        ("computer_use", "computer_use_blocked"),
    ],
)
def test_browser_and_computer_use_requests_are_blocked(flag, reason):
    decision = _mediator().evaluate(_read_only_envelope(**{flag: True}))

    assert decision.decision == "blocked"
    assert decision.preview_allowed is False
    assert reason in decision.blocked_reasons


def test_filesystem_write_request_is_blocked():
    decision = _mediator().evaluate(
        _read_only_envelope(read_only=False, filesystem_write=True, requested_actions=("edit file",))
    )

    assert decision.decision == "blocked"
    assert "read_only_required" in decision.blocked_reasons
    assert "filesystem_write_blocked" in decision.blocked_reasons
    assert "filesystem_write" in decision.blocked_actions


@pytest.mark.parametrize(
    ("flag", "reason"),
    [
        ("email_action", "email_action_blocked"),
        ("calendar_action", "calendar_action_blocked"),
        ("shopify_action", "shopify_action_blocked"),
        ("account_action", "account_action_blocked"),
        ("external_write", "external_write_blocked"),
    ],
)
def test_external_action_requests_are_blocked(flag, reason):
    decision = _mediator().evaluate(_read_only_envelope(**{flag: True}))

    assert decision.decision == "blocked"
    assert reason in decision.blocked_reasons


def test_missing_scope_is_blocked():
    decision = _mediator().evaluate(_read_only_envelope(allowed_input_scope=()))

    assert decision.decision == "blocked"
    assert "missing_allowed_input_scope" in decision.blocked_reasons


def test_direct_cap63_shortcut_is_blocked():
    decision = _mediator().evaluate(_read_only_envelope(direct_cap63_shortcut=True))

    assert decision.decision == "blocked"
    assert "direct_cap63_shortcut_blocked" in decision.blocked_reasons
    assert "direct_cap63_shortcut" in decision.blocked_actions


def test_blocked_terms_in_request_text_are_classified_without_execution():
    decision = _mediator().evaluate(
        _read_only_envelope(
            request_text="Use openclaw_execute / Cap 63 to open a browser and click through my account."
        )
    )

    assert decision.decision == "blocked"
    assert "direct_cap63_shortcut_blocked" in decision.blocked_reasons
    assert "browser_use_blocked" in decision.blocked_reasons
    assert "account_action_blocked" in decision.blocked_reasons


def test_blocked_term_matching_uses_word_boundaries():
    decision = _mediator().evaluate(
        _read_only_envelope(
            request_text="Prepare a stable table of contents from sample notes."
        )
    )

    assert decision.decision == "preview_allowed"
    assert "browser_use_blocked" not in decision.blocked_reasons


def test_blocked_phrase_matching_still_blocks_direct_cap63_and_browser():
    decision = _mediator().evaluate(
        _read_only_envelope(
            request_text="Use openclaw_execute / Cap 63 to open a browser."
        )
    )

    assert decision.decision == "blocked"
    assert "direct_cap63_shortcut_blocked" in decision.blocked_reasons
    assert "browser_use_blocked" in decision.blocked_reasons


def test_receipt_says_what_did_and_did_not_happen():
    decision, receipt = _mediator().evaluate_with_receipt(
        _read_only_envelope(browser_use=True)
    )

    assert decision.decision == "blocked"
    assert "OpenClawMediator evaluated the delegation envelope." in receipt.did_happen
    assert "OpenClaw was not executed." in receipt.did_not_happen
    assert "No capability was called." in receipt.did_not_happen
    assert "The Governor was not called." in receipt.did_not_happen
    assert "No browser or computer-use action was performed." in receipt.did_not_happen
    assert "No network request was made." in receipt.did_not_happen
    assert "Cap 63 was not used as a shortcut." in receipt.did_not_happen


def test_decision_enforces_no_execution_and_no_authorization():
    with pytest.raises(ValueError, match="must not record execution"):
        OpenClawMediatorDecision(
            decision="blocked",
            preview_allowed=False,
            reason="blocked",
            execution_performed=True,
        )
    with pytest.raises(ValueError, match="must not grant authorization"):
        OpenClawMediatorDecision(
            decision="blocked",
            preview_allowed=False,
            reason="blocked",
            authorization_granted=True,
        )
    with pytest.raises(ValueError, match="must not call OpenClaw"):
        OpenClawMediatorDecision(
            decision="blocked",
            preview_allowed=False,
            reason="blocked",
            openclaw_called=True,
        )


def test_receipt_enforces_no_execution_and_no_authorization():
    kwargs = {
        "receipt_type": "openclaw_mediator_preview",
        "request_text": "preview",
        "decision": "blocked",
        "summary": "blocked",
        "non_action_statement": "decision only",
        "did_happen": ("OpenClawMediator returned a policy decision.",),
        "did_not_happen": ("OpenClaw was not executed.",),
    }

    with pytest.raises(ValueError, match="must not record execution"):
        OpenClawMediatorReceipt(**kwargs, execution_performed=True)
    with pytest.raises(ValueError, match="must not grant authorization"):
        OpenClawMediatorReceipt(**kwargs, authorization_granted=True)


def test_payload_contains_no_execution_handles():
    decision, receipt = _mediator().evaluate_with_receipt(_read_only_envelope())
    payload = {
        "envelope": _read_only_envelope().to_dict(),
        "decision": decision.to_dict(),
        "receipt": receipt.to_dict(),
    }

    serialized = str(payload).lower()
    assert "run_template" not in serialized
    assert "run_goal" not in serialized
    assert "governor" in serialized  # only in non-action statement / boolean field names
    assert payload["decision"]["governor_called"] is False
    assert payload["decision"]["capabilities_called"] is False
    assert payload["decision"]["browser_opened"] is False
    assert payload["decision"]["network_called"] is False
