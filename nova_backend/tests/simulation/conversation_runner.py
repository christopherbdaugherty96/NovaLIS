from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .conversation_simulator import ConversationTranscript, run_simulation
from .analytics import build_run_metadata


def load_script(path: str | Path) -> list[str]:
    script_path = Path(path)
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    if script_path.suffix.lower() == ".json":
        payload: Any = json.loads(script_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("script"), list):
            return [str(item) for item in payload["script"]]
        if isinstance(payload, list):
            return [str(item) for item in payload]
        raise ValueError("JSON script must be a list[str] or an object with a 'script' list.")

    lines = [line.strip() for line in script_path.read_text(encoding="utf-8").splitlines()]
    return [line for line in lines if line and not line.startswith("#")]


def run_script(script: list[str], *, include_trace: bool = False) -> ConversationTranscript:
    return run_simulation(script, include_trace=include_trace)


def load_scenario_library(directory: str | Path) -> list[dict[str, Any]]:
    root = Path(directory)
    if not root.exists():
        raise FileNotFoundError(f"Scenario directory not found: {root}")

    scenarios: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            continue
        script = payload.get("script")
        if not isinstance(script, list):
            continue
        scenarios.append(
            {
                "name": str(payload.get("name") or path.stem),
                "script": [str(item) for item in script],
                "expect": payload.get("expect") if isinstance(payload.get("expect"), dict) else {},
                "path": str(path),
            }
        )
    return scenarios


def run_scenario_library(directory: str | Path) -> list[tuple[dict[str, Any], ConversationTranscript]]:
    scenarios = load_scenario_library(directory)
    out: list[tuple[dict[str, Any], ConversationTranscript]] = []
    for scenario in scenarios:
        transcript = run_script(scenario["script"])
        out.append((scenario, transcript))
    return out


def transcript_to_dict(transcript: ConversationTranscript) -> dict[str, Any]:
    return {
        "turns": [
            {
                "user_message": turn.user_message,
                "nova_response": turn.nova_response,
                "decision_mode": turn.decision_mode,
                "intent_family": turn.intent_family,
                "continuation_detected": turn.continuation_detected,
                "should_escalate": turn.should_escalate,
                "policy_blocked": turn.policy_blocked,
                "clarification_triggered": turn.clarification_triggered,
                "capability_triggered": turn.capability_triggered,
                "capability_executor": turn.capability_executor,
                "governor_decision": turn.governor_decision,
                "execution_time_ms": turn.execution_time_ms,
                "errors": list(turn.errors),
                "trace_id": turn.trace_id,
                "trace_steps": list(turn.trace_steps),
            }
            for turn in transcript.turns
        ]
    }


def build_run_record(
    transcript: ConversationTranscript,
    *,
    scenario: str = "",
    profile: str = "simulation",
    passed: bool = True,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    transcript_payload = transcript_to_dict(transcript)
    turns = transcript_payload.get("turns", [])
    return {
        "run_metadata": build_run_metadata(
            scenario=scenario,
            profile=profile,
            passed=passed,
            total_turns=len(turns),
            repo_root=repo_root,
        ),
        "transcript": transcript_payload,
    }


def export_transcript_json(
    transcript: ConversationTranscript,
    path: str | Path,
    *,
    scenario: str = "",
    profile: str = "simulation",
    passed: bool = True,
    repo_root: str | Path | None = None,
) -> Path:
    out_path = Path(path)
    run_record = build_run_record(
        transcript,
        scenario=scenario,
        profile=profile,
        passed=passed,
        repo_root=repo_root,
    )
    out_path.write_text(json.dumps(run_record, indent=2), encoding="utf-8")
    return out_path


def print_transcript(transcript: ConversationTranscript) -> None:
    for idx, turn in enumerate(transcript.turns, start=1):
        cap = f"capability={turn.capability_triggered}" if turn.capability_triggered is not None else "capability=None"
        print(f"[{idx}] USER: {turn.user_message}")
        print(f"    NOVA: {turn.nova_response}")
        print(
            f"    META: mode={turn.decision_mode or 'n/a'} intent={turn.intent_family or 'n/a'} "
            f"continuation={turn.continuation_detected} escalate={turn.should_escalate} "
            f"policy_blocked={turn.policy_blocked} clarification={turn.clarification_triggered} "
            f"{cap} executor={turn.capability_executor or 'n/a'} decision={turn.governor_decision} "
            f"latency_ms={turn.execution_time_ms:.3f} errors={turn.errors}"
        )
