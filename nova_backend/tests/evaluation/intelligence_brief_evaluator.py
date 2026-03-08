from __future__ import annotations

from dataclasses import dataclass

from .cognitive_evaluator import CognitiveEvaluationResult, CognitiveEvaluator


@dataclass(frozen=True)
class IntelligenceBriefGrade:
    result: CognitiveEvaluationResult
    structure_pass: bool
    source_coverage_pass: bool
    confidence_present: bool


class IntelligenceBriefEvaluator:
    @staticmethod
    def evaluate(text: str) -> IntelligenceBriefGrade:
        result = CognitiveEvaluator.evaluate_intelligence_brief(text)
        structure_pass = result.has_summary and result.has_key_findings and result.has_sources
        source_coverage_pass = result.source_count >= 2
        confidence_present = result.has_confidence
        return IntelligenceBriefGrade(
            result=result,
            structure_pass=structure_pass,
            source_coverage_pass=source_coverage_pass,
            confidence_present=confidence_present,
        )

