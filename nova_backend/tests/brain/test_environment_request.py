import json

from src.brain.environment_request import (
    AllowedStatus,
    AuthorityTier,
    BrainDryRun,
    BrainTraceEvent,
    CapabilityContract,
    ClarificationQuestion,
    EnvironmentOption,
    EnvironmentRequest,
    EnvironmentType,
    PlanStep,
)


def test_environment_request_serializes_enum_values():
    request = EnvironmentRequest(
        task_id="task_search_1",
        task="What are the latest model releases?",
        task_type="current_search",
        requested_environment=EnvironmentType.WEB_SEARCH,
        reason="Current facts require web evidence.",
        authority_required=AuthorityTier.NETWORK_READ,
        capability_needed="cap16_governed_web_search",
        proof_required=["source_urls", "search_receipt"],
        confidence=0.91,
        risk_level="network_read",
        allowed_status=AllowedStatus.ALLOWED,
        next_safe_step="Run governed web search through Cap 16.",
    )

    payload = json.loads(json.dumps(request, default=lambda value: value.value if hasattr(value, "value") else value.__dict__))

    assert payload["requested_environment"] == "web_search"
    assert payload["authority_required"] == "network_read"
    assert payload["allowed_status"] == "allowed"


def test_brain_dry_run_to_dict_is_json_safe():
    dry_run = BrainDryRun(
        task="Find contractors and draft an email.",
        clarification=ClarificationQuestion(
            question="What city or service area should I search in?",
            missing_fields=["city_or_service_area"],
            assumptions_to_avoid=["Do not guess the user's location."],
            safe_partial_path="Explain the plan without searching or drafting yet.",
        ),
        environment_options=[
            EnvironmentOption(
                environment=EnvironmentType.WEB_SEARCH,
                confidence=0.86,
                risk_level="network_read",
                authority_tier=AuthorityTier.NETWORK_READ,
                capability_needed="cap16_governed_web_search",
                reason="Contractor discovery requires current public web results.",
            ),
            EnvironmentOption(
                environment=EnvironmentType.EMAIL_DRAFT,
                confidence=0.78,
                risk_level="external_effect_draft",
                authority_tier=AuthorityTier.EXTERNAL_EFFECT_DRAFT,
                capability_needed="cap64_send_email_draft",
                requires_confirmation=True,
                reason="Drafting email is local draft only and requires confirmation.",
            ),
        ],
        selected_environment=None,
        plan_steps=[
            PlanStep(
                step_id="clarify_city",
                description="Ask for city or service area before searching.",
                environment=EnvironmentType.LOCAL_CONVERSATION,
                authority_required=AuthorityTier.NONE,
            )
        ],
        capability_contracts=[
            CapabilityContract(
                capability_id=64,
                name="send_email_draft",
                environment=EnvironmentType.EMAIL_DRAFT,
                authority_tier=AuthorityTier.EXTERNAL_EFFECT_DRAFT,
                can=["open a local mailto draft after confirmation"],
                cannot=["send email", "use SMTP", "read inbox"],
                confirmation_required=True,
                expected_receipts=["EMAIL_DRAFT_CREATED"],
            )
        ],
        confirmation_points=["before_opening_email_draft"],
        proof_expected=["source_urls", "EMAIL_DRAFT_CREATED if opened"],
        fallback_ladder=["ask clarification", "show manual plan"],
        will_not_do=["send email", "search before city is known"],
    )

    payload = dry_run.to_dict()
    json.dumps(payload)

    assert payload["clarification"]["missing_fields"] == ["city_or_service_area"]
    assert payload["environment_options"][0]["environment"] == "web_search"
    assert payload["capability_contracts"][0]["cannot"] == ["send email", "use SMTP", "read inbox"]


def test_brain_trace_event_create_sets_utc_timestamp():
    event = BrainTraceEvent.create(
        event_type="dry_run_created",
        task_id="task_1",
        route="brain_dry_run",
        environment=EnvironmentType.WEB_SEARCH,
        capability="cap16_governed_web_search",
        authority_tier=AuthorityTier.NETWORK_READ,
        status=AllowedStatus.DRY_RUN_ONLY,
        note="No execution performed.",
    )

    payload = event.to_dict()

    assert payload["timestamp"].endswith("+00:00")
    assert payload["environment"] == "web_search"
    assert payload["status"] == "dry_run_only"
