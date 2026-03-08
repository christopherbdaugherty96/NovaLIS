from __future__ import annotations

from src.validation.pipeline import ValidationPipeline, ValidationResult


class PersonalityValidator:
    def __init__(self) -> None:
        self._pipeline = ValidationPipeline()

    def validate(self, raw_text: str, presented_text: str) -> ValidationResult:
        return self._pipeline.validate(raw_text, presented_text)
