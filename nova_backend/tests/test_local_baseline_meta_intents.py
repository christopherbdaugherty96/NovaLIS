from src.conversation.meta_intent_handler import MetaIntentHandler


def test_core_status_prompt_uses_local_meta_fallback():
    response = MetaIntentHandler().handle("What works today?", session_state={"turn_count": 1})
    assert response is not None
    lowered = response.lower()
    assert "local fallback" in lowered
    assert "memory" in lowered
    assert "receipts" in lowered
    assert "email" in lowered


def test_memory_authority_prompt_uses_local_meta_fallback():
    response = MetaIntentHandler().handle(
        "Can memory authorize actions?",
        session_state={"turn_count": 1},
    )
    assert response is not None
    lowered = response.lower()
    assert "cannot authorize actions" in lowered
    assert "intelligence is not authority" in lowered


def test_memory_receipts_difference_uses_local_meta_fallback():
    response = MetaIntentHandler().handle(
        "What is the difference between memory and receipts?",
        session_state={"turn_count": 1},
    )
    assert response is not None
    lowered = response.lower()
    assert "memory helps nova understand" in lowered
    assert "receipts help you audit" in lowered
