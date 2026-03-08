from __future__ import annotations

from src.cognition.cognitive_layer_contract import (
    CognitiveModule,
    CognitiveRequest,
    CognitiveResult,
    validate_cognitive_result,
)


class VerificationModule(CognitiveModule):
    """Template analysis-only verification module for Phase 4.2 cognition surfaces."""

    name = "verification_module"
    version = "0.1.0"

    def analyze(self, request: CognitiveRequest) -> CognitiveResult:
        query = request.user_query.strip() or "General Topic"
        findings = request.source_data.get("findings", [])
        sources = request.source_data.get("sources", [])

        normalized_findings = [str(item).strip() for item in findings if str(item).strip()]
        normalized_sources = [str(item).strip() for item in sources if str(item).strip()]

        contradiction_markers = (
            ("increase", "decrease"),
            ("rise", "fall"),
            ("supports", "opposes"),
            ("strict", "voluntary"),
            ("accelerating", "slowing"),
        )
        corpus = " ".join(normalized_findings).lower()
        contradictions: list[str] = []
        for left, right in contradiction_markers:
            if left in corpus and right in corpus:
                contradictions.append(f"Conflicting signal detected: '{left}' vs '{right}'.")

        base = 0.55
        source_bonus = min(len(normalized_sources), 4) * 0.08
        contradiction_penalty = min(len(contradictions), 3) * 0.10
        confidence = max(0.3, min(0.95, base + source_bonus - contradiction_penalty))

        if not contradictions:
            contradictions = ["No major contradiction markers detected in the collected findings."]

        key_points = (
            "Verification run completed under analysis-only constraints.",
            f"Sources reviewed: {len(normalized_sources)}",
            f"Contradiction markers: {len(contradictions)}",
        )
        result = CognitiveResult(
            summary=(
                f"Verification pass for '{query}' reviewed source agreement and contradiction markers."
            ),
            key_points=key_points,
            supporting_sources=tuple(normalized_sources[:5]) or ("unattributed-source",),
            confidence=confidence,
            module_name=self.name,
            diagnostics={
                "template": True,
                "topic": query,
                "contradictions": contradictions[:4],
                "source_count": len(normalized_sources),
                "request_id": request.request_id,
            },
        )
        validate_cognitive_result(result)
        return result
