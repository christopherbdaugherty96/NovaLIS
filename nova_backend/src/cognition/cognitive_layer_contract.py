from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol


class CognitiveMode(str, Enum):
    ANALYSIS = "analysis"
    VERIFICATION = "verification"
    SUMMARIZATION = "summarization"
    REPORTING = "reporting"


@dataclass(frozen=True)
class CognitiveRequest:
    user_query: str
    conversation_context: tuple[str, ...] = ()
    source_data: Mapping[str, Any] = field(default_factory=dict)
    mode: CognitiveMode = CognitiveMode.ANALYSIS
    request_id: str = ""


@dataclass(frozen=True)
class CognitiveResult:
    summary: str
    key_points: tuple[str, ...] = ()
    supporting_sources: tuple[str, ...] = ()
    confidence: float = 0.5
    module_name: str = ""
    diagnostics: Mapping[str, Any] = field(default_factory=dict)


class CognitiveModule(Protocol):
    name: str
    version: str

    def analyze(self, request: CognitiveRequest) -> CognitiveResult:
        """Perform analysis only. Execution authority is forbidden."""


def validate_cognitive_result(result: CognitiveResult) -> None:
    if not result.summary.strip():
        raise ValueError("Cognitive result summary must not be empty.")
    if not 0.0 <= float(result.confidence) <= 1.0:
        raise ValueError("Cognitive result confidence must be within [0.0, 1.0].")
    if any(not str(point).strip() for point in result.key_points):
        raise ValueError("Cognitive result key points must not contain blank entries.")
    if any(not str(source).strip() for source in result.supporting_sources):
        raise ValueError("Cognitive result sources must not contain blank entries.")
