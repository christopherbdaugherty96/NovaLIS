from __future__ import annotations

from dataclasses import dataclass

from src.validation.authority import AuthorityLanguageDetector
from src.validation.emotional import EmotionalBoundaryEnforcer
from src.validation.formatting import FormattingValidator
from src.validation.transformation import TransformationValidator


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    stage: str = ""
    reason: str = ""


class ValidationPipeline:
    """Fixed-order Phase 4.2 validation pipeline."""

    def __init__(self) -> None:
        self._transformation = TransformationValidator()
        self._authority = AuthorityLanguageDetector()
        self._emotional = EmotionalBoundaryEnforcer()
        self._formatting = FormattingValidator()

    def validate(self, raw_text: str, presented_text: str) -> ValidationResult:
        step1 = self._transformation.validate(raw_text, presented_text)
        if not step1.ok:
            return ValidationResult(False, "TransformationValidator", step1.reason)

        step2 = self._authority.validate(presented_text)
        if not step2.ok:
            return ValidationResult(False, "AuthorityLanguageDetector", step2.reason)

        step3 = self._emotional.validate(presented_text)
        if not step3.ok:
            return ValidationResult(False, "EmotionalBoundaryEnforcer", step3.reason)

        step4 = self._formatting.validate(presented_text)
        if not step4.ok:
            return ValidationResult(False, "FormattingValidator", step4.reason)

        return ValidationResult(True)
