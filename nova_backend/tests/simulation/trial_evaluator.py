from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .conversation_simulator import ConversationTranscript, TranscriptTurn


@dataclass(frozen=True)
class TrialGap:
    severity: str
    category: str
    message: str
    turn_index: int | None = None
    expected: Any = None
    actual: Any = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "turn_index": self.turn_index,
            "expected": self.expected,
            "actual": self.actual,
        }
        return {key: value for key, value in payload.items() if value is not None}


def _expectation(scenario: dict[str, Any], key: str, default: Any = None) -> Any:
    expect = scenario.get("expect") if isinstance(scenario.get("expect"), dict) else {}
    return expect.get(key, default)


def _list_expectation(scenario: dict[str, Any], key: str) -> list[Any]:
    value = _expectation(scenario, key, [])
    return list(value) if isinstance(value, (list, tuple)) else []


def _turn_text(turn: TranscriptTurn) -> str:
    return str(turn.nova_response or "")


def _safe_nonnegative_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except Exception:
        return 0


def evaluate_trial(
    scenario: dict[str, Any],
    transcript: ConversationTranscript,
) -> dict[str, Any]:
    """Evaluate one simulated scenario against structured expectations."""

    gaps: list[TrialGap] = []
    turns = list(transcript.turns)
    scenario_name = str(scenario.get("name") or "unnamed_scenario")
    raw_script = scenario.get("script")
    expected_script = list(raw_script) if isinstance(raw_script, list) else []

    if len(turns) != len(expected_script):
        gaps.append(
            TrialGap(
                severity="high",
                category="transcript",
                message=f"{scenario_name} produced an unexpected turn count.",
                expected=len(expected_script),
                actual=len(turns),
            )
        )

    expected_caps = _list_expectation(scenario, "capability_sequence")
    if expected_caps:
        actual_caps = transcript.capability_sequence()
        if actual_caps != expected_caps:
            gaps.append(
                TrialGap(
                    severity="high",
                    category="routing",
                    message="Capability sequence did not match the scenario expectation.",
                    expected=expected_caps,
                    actual=actual_caps,
                )
            )

    expected_decisions = _list_expectation(scenario, "governor_decisions")
    if expected_decisions:
        actual_decisions = [turn.governor_decision for turn in turns]
        if actual_decisions != expected_decisions:
            gaps.append(
                TrialGap(
                    severity="medium",
                    category="governor",
                    message="Governor decision sequence did not match.",
                    expected=expected_decisions,
                    actual=actual_decisions,
                )
            )

    if bool(_expectation(scenario, "no_policy_blocks", True)):
        blocked_turns = [idx for idx, turn in enumerate(turns, start=1) if turn.policy_blocked]
        if blocked_turns:
            gaps.append(
                TrialGap(
                    severity="high",
                    category="safety",
                    message="Scenario hit policy blocks where none were expected.",
                    expected=[],
                    actual=blocked_turns,
                )
            )

    expected_policy_blocks = _list_expectation(scenario, "policy_block_turns")
    if expected_policy_blocks:
        blocked_turns = [idx for idx, turn in enumerate(turns, start=1) if turn.policy_blocked]
        if blocked_turns != expected_policy_blocks:
            gaps.append(
                TrialGap(
                    severity="high",
                    category="safety",
                    message="Policy block turns did not match the scenario expectation.",
                    expected=expected_policy_blocks,
                    actual=blocked_turns,
                )
            )

    expected_clarifications = _list_expectation(scenario, "clarification_turns")
    if expected_clarifications:
        clarification_turns = [
            idx for idx, turn in enumerate(turns, start=1) if turn.clarification_triggered
        ]
        if clarification_turns != expected_clarifications:
            gaps.append(
                TrialGap(
                    severity="medium",
                    category="clarification",
                    message="Clarification turns did not match the scenario expectation.",
                    expected=expected_clarifications,
                    actual=clarification_turns,
                )
            )

    allowed_error_turns = _safe_nonnegative_int(_expectation(scenario, "max_error_turns", 0))
    error_turns = [idx for idx, turn in enumerate(turns, start=1) if turn.errors]
    if len(error_turns) > allowed_error_turns:
        error_details = [
            {
                "turn": idx,
                "prompt": turns[idx - 1].user_message,
                "errors": list(turns[idx - 1].errors),
            }
            for idx in error_turns
        ]
        gaps.append(
            TrialGap(
                severity="high",
                category="execution",
                message="Scenario produced more error turns than allowed.",
                expected=allowed_error_turns,
                actual=error_details,
            )
        )

    required_fragments = _list_expectation(scenario, "required_response_fragments")
    for rule in required_fragments:
        if not isinstance(rule, dict):
            continue
        turn_index = _safe_nonnegative_int(rule.get("turn"))
        fragment = str(rule.get("contains") or "").strip()
        if not turn_index or not fragment:
            continue
        actual_text = _turn_text(turns[turn_index - 1]) if 0 < turn_index <= len(turns) else ""
        if fragment.lower() not in actual_text.lower():
            gaps.append(
                TrialGap(
                    severity=str(rule.get("severity") or "medium"),
                    category="response_quality",
                    message="Required response fragment was missing.",
                    turn_index=turn_index,
                    expected=fragment,
                    actual=actual_text[:240],
                )
            )

    forbidden_fragments = _list_expectation(scenario, "forbidden_response_fragments")
    for rule in forbidden_fragments:
        if not isinstance(rule, dict):
            continue
        turn_index = _safe_nonnegative_int(rule.get("turn"))
        fragment = str(rule.get("contains") or "").strip()
        if not turn_index or not fragment:
            continue
        actual_text = _turn_text(turns[turn_index - 1]) if 0 < turn_index <= len(turns) else ""
        if fragment.lower() in actual_text.lower():
            gaps.append(
                TrialGap(
                    severity=str(rule.get("severity") or "medium"),
                    category="response_quality",
                    message="Forbidden response fragment appeared.",
                    turn_index=turn_index,
                    expected=f"avoid: {fragment}",
                    actual=actual_text[:240],
                )
            )

    severity_weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    penalty = sum(severity_weights.get(gap.severity.lower(), 1) for gap in gaps)
    score = max(0.0, round(1.0 - (penalty / 10.0), 3))

    return {
        "scenario": scenario_name,
        "passed": not gaps,
        "score": score,
        "gap_count": len(gaps),
        "gaps": [gap.to_dict() for gap in gaps],
        "capability_sequence": transcript.capability_sequence(),
        "turn_count": len(turns),
    }


def prioritize_gaps(evaluations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    gaps: list[dict[str, Any]] = []
    for evaluation in evaluations:
        scenario_name = str(evaluation.get("scenario") or "unnamed_scenario")
        for gap in list(evaluation.get("gaps") or []):
            if not isinstance(gap, dict):
                continue
            row = dict(gap)
            row["scenario"] = scenario_name
            gaps.append(row)
    return sorted(
        gaps,
        key=lambda gap: (
            severity_rank.get(str(gap.get("severity") or "low").lower(), 4),
            str(gap.get("category") or ""),
            str(gap.get("scenario") or ""),
        ),
    )
