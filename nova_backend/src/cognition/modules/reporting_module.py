from __future__ import annotations

from src.cognition.cognitive_layer_contract import (
    CognitiveModule,
    CognitiveRequest,
    CognitiveResult,
    validate_cognitive_result,
)


class ReportingModule(CognitiveModule):
    """Template analysis-only reporting module for Phase 4.2 cognition surfaces."""

    name = "reporting_module"
    version = "0.1.0"

    def analyze(self, request: CognitiveRequest) -> CognitiveResult:
        topic = request.user_query.strip() or "General Topic"
        summary = str(request.source_data.get("summary") or "").strip()
        findings = request.source_data.get("findings", [])
        sources = request.source_data.get("sources", [])
        contradictions = request.source_data.get("contradictions", [])
        confidence = float(request.source_data.get("confidence", 0.5))

        normalized_findings = tuple(str(item).strip() for item in findings if str(item).strip())[:5]
        normalized_sources = tuple(str(item).strip() for item in sources if str(item).strip())[:5]
        normalized_contradictions = tuple(str(item).strip() for item in contradictions if str(item).strip())[:4]

        if not summary:
            summary = f"Structured intelligence brief generated for '{topic}'."
        if not normalized_findings:
            normalized_findings = ("No high-confidence finding available from current inputs.",)
        if not normalized_sources:
            normalized_sources = ("unattributed-source",)
        if not normalized_contradictions:
            normalized_contradictions = ("No major contradiction markers were detected.",)

        result = CognitiveResult(
            summary=summary,
            key_points=normalized_findings,
            supporting_sources=normalized_sources,
            confidence=max(0.0, min(1.0, confidence)),
            module_name=self.name,
            diagnostics={
                "template": True,
                "topic": topic,
                "contradictions": normalized_contradictions,
                "request_id": request.request_id,
            },
        )
        validate_cognitive_result(result)
        return result
