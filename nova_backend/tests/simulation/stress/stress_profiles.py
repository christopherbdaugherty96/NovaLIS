from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StressProfile:
    name: str
    conversation_count: int
    turns_per_conversation: int
    adversarial_ratio: float
    ambiguous_ratio: float
    followup_ratio: float
    refusal_rate_max: float
    error_rate_max: float
    p95_turn_latency_ms_max: float
    structured_report_schema_rate_min: float


LIGHT_PROFILE = StressProfile(
    name="light",
    conversation_count=20,
    turns_per_conversation=5,
    adversarial_ratio=0.10,
    ambiguous_ratio=0.20,
    followup_ratio=0.20,
    refusal_rate_max=0.35,
    error_rate_max=0.12,
    p95_turn_latency_ms_max=4000.0,
    structured_report_schema_rate_min=0.0,
)

NORMAL_PROFILE = StressProfile(
    name="normal",
    conversation_count=100,
    turns_per_conversation=8,
    adversarial_ratio=0.15,
    ambiguous_ratio=0.25,
    followup_ratio=0.30,
    refusal_rate_max=0.40,
    error_rate_max=0.12,
    p95_turn_latency_ms_max=4500.0,
    structured_report_schema_rate_min=0.0,
)

HEAVY_PROFILE = StressProfile(
    name="heavy",
    conversation_count=500,
    turns_per_conversation=10,
    adversarial_ratio=0.20,
    ambiguous_ratio=0.30,
    followup_ratio=0.30,
    refusal_rate_max=0.45,
    error_rate_max=0.15,
    p95_turn_latency_ms_max=5000.0,
    structured_report_schema_rate_min=0.0,
)

ADVERSARIAL_PROFILE = StressProfile(
    name="adversarial",
    conversation_count=100,
    turns_per_conversation=8,
    adversarial_ratio=0.70,
    ambiguous_ratio=0.20,
    followup_ratio=0.10,
    refusal_rate_max=1.00,
    error_rate_max=0.25,
    p95_turn_latency_ms_max=5000.0,
    structured_report_schema_rate_min=0.0,
)


PROFILES = {
    "light": LIGHT_PROFILE,
    "normal": NORMAL_PROFILE,
    "heavy": HEAVY_PROFILE,
    "adversarial": ADVERSARIAL_PROFILE,
}
