from src.trust.trust_contract import normalize_trust_status


def test_normalize_trust_status_bounds_fields():
    normalized = normalize_trust_status(
        {
            "mode": "UnknownMode",
            "last_external_call": "Weather update",
            "data_egress": "Read-only external request",
            "failure_state": "Unexpected",
            "consecutive_failures": "3",
        }
    )
    assert normalized["mode"] == "Local-only"
    assert normalized["failure_state"] == "Temporary issue"
    assert normalized["consecutive_failures"] == 3


def test_normalize_trust_status_defaults():
    normalized = normalize_trust_status({})
    assert normalized["mode"] == "Local-only"
    assert normalized["last_external_call"] == "None"
    assert normalized["data_egress"] == "No external call in this step"
    assert normalized["failure_state"] == "Normal"
    assert normalized["consecutive_failures"] == 0
