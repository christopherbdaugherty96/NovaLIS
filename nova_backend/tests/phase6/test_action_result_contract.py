from src.actions.action_result import ActionResult


def test_action_result_ok_normalizes_legacy_payload_into_contract_fields():
    result = ActionResult.ok(
        "Search complete.",
        data={"query": "ai regulation", "result_count": 3},
        request_id="req-search-1",
    )

    assert result.success is True
    assert result.status == "completed"
    assert result.user_message == "Search complete."
    assert result.speakable_text == "Search complete."
    assert result.structured_data == {"query": "ai regulation", "result_count": 3}


def test_action_result_failure_normalizes_reason_and_preserves_structured_payload():
    result = ActionResult.failure(
        "I couldn't build the report right now.",
        data={
            "structured_data": {"query": "ai regulation"},
            "retryable": True,
        },
        request_id="req-report-1",
    ).normalize(capability_id=48, authority_class="read_only_network")

    contract = result.to_contract_dict()

    assert result.success is False
    assert result.status == "failed"
    assert result.outcome_reason == "I couldn't build the report right now."
    assert result.capability_id == 48
    assert result.authority_class == "read_only_network"
    assert result.structured_data == {"query": "ai regulation"}
    assert contract["request_id"] == "req-report-1"
    assert contract["speakable_text"] == "I couldn't build the report right now."
