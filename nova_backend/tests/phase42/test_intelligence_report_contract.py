from src.cognition.intelligence_report_contract import (
    validate_rendered_report_text,
    validate_structured_report_payload,
)


def test_structured_report_contract_accepts_valid_payload():
    payload = {
        "topic": "AI Regulation",
        "summary": "Policy momentum is increasing.",
        "key_findings": ["EU and US policy updates remain active."],
        "supporting_sources": ["reuters.com", "bbc.com"],
        "contradictions": ["No major contradiction markers detected."],
        "confidence": 0.82,
    }
    validate_structured_report_payload(payload)


def test_structured_report_contract_rejects_missing_fields():
    payload = {
        "topic": "AI Regulation",
        "summary": "Policy momentum is increasing.",
        "key_findings": ["EU and US policy updates remain active."],
        "confidence": 0.82,
    }
    try:
        validate_structured_report_payload(payload)
        assert False, "Expected ValueError for missing required fields."
    except ValueError:
        assert True


def test_rendered_report_contract_sections_required():
    valid_text = (
        "INTELLIGENCE BRIEF\n"
        "Summary\n"
        "Key Findings\n"
        "Supporting Sources\n"
        "Contradictions\n"
        "Confidence\n"
    )
    validate_rendered_report_text(valid_text)
