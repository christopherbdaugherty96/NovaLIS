from __future__ import annotations

from typing import Any


REQUIRED_STRUCTURED_FIELDS = (
    "topic",
    "summary",
    "key_findings",
    "supporting_sources",
    "contradictions",
    "confidence",
)

REQUIRED_RENDER_SECTIONS = (
    "INTELLIGENCE BRIEF",
    "Summary",
    "Key Findings",
    "Supporting Sources",
    "Contradictions",
    "Confidence",
)


def validate_structured_report_payload(payload: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED_STRUCTURED_FIELDS if key not in payload]
    if missing:
        raise ValueError(f"Structured intelligence payload missing required fields: {missing}")

    if not str(payload.get("topic", "")).strip():
        raise ValueError("Structured intelligence payload requires non-empty topic.")
    if not str(payload.get("summary", "")).strip():
        raise ValueError("Structured intelligence payload requires non-empty summary.")

    findings = payload.get("key_findings")
    sources = payload.get("supporting_sources")
    contradictions = payload.get("contradictions")
    if not isinstance(findings, list) or not findings:
        raise ValueError("Structured intelligence payload requires non-empty key_findings list.")
    if not isinstance(sources, list) or not sources:
        raise ValueError("Structured intelligence payload requires non-empty supporting_sources list.")
    if not isinstance(contradictions, list) or not contradictions:
        raise ValueError("Structured intelligence payload requires non-empty contradictions list.")

    confidence = payload.get("confidence")
    try:
        bounded = float(confidence)
    except (TypeError, ValueError):
        raise ValueError("Structured intelligence payload requires numeric confidence.") from None
    if not 0.0 <= bounded <= 1.0:
        raise ValueError("Structured intelligence payload confidence must be in [0.0, 1.0].")


def validate_rendered_report_text(text: str) -> None:
    content = str(text or "")
    missing_sections = [section for section in REQUIRED_RENDER_SECTIONS if section not in content]
    if missing_sections:
        raise ValueError(f"Rendered intelligence report missing required sections: {missing_sections}")
