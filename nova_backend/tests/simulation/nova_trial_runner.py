from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    _repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(_repo_root))
    sys.path.insert(0, str(_repo_root / "nova_backend"))

try:
    from .analytics import aggregate_simulation_runs, export_analytics_json
    from .conversation_runner import (
        build_run_record,
        load_scenario_library,
        run_script,
        transcript_to_dict,
    )
    from .trial_evaluator import evaluate_trial, prioritize_gaps
except ImportError:
    from nova_backend.tests.simulation.analytics import aggregate_simulation_runs, export_analytics_json
    from nova_backend.tests.simulation.conversation_runner import (
        build_run_record,
        load_scenario_library,
        run_script,
        transcript_to_dict,
    )
    from nova_backend.tests.simulation.trial_evaluator import evaluate_trial, prioritize_gaps


REPORT_TEXT_REPLACEMENTS = {
    "\u2192": "->",
    "\u2014": "-",
    "\u2013": "-",
    "\u00b0F": "F",
    "\u00c3\u00a2\u00e2\u20ac\u00a0\u00e2\u20ac\u2122": "->",
    "\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u009d": "-",
    "\u00c3\u00a2\u00e2\u201a\u00ac\u00e2\u20ac\u0153": "-",
    "\u00c3\u201a\u00c2\u00b0F": "F",
    "\u00e2\u2020\u2019": "->",
    "\u00e2\u20ac\u201d": "-",
    "\u00e2\u20ac\u201c": "-",
    "\u00c2\u00b0F": "F",
}


def _slug(value: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "_" for ch in str(value or "").strip())
    return "_".join(part for part in safe.split("_") if part) or "scenario"


def _sanitize_report_value(value: Any) -> Any:
    if isinstance(value, str):
        cleaned = value
        for source, replacement in REPORT_TEXT_REPLACEMENTS.items():
            cleaned = cleaned.replace(source, replacement)
        return cleaned
    if isinstance(value, list):
        return [_sanitize_report_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _sanitize_report_value(item) for key, item in value.items()}
    return value


def _format_report_value(value: Any) -> str:
    value = _sanitize_report_value(value)
    if isinstance(value, (dict, list)):
        return "\n```json\n" + json.dumps(value, indent=2, ensure_ascii=False) + "\n```"
    return f"`{value}`"


def _count_by_key(rows: list[dict[str, Any]], key: str) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    for row in rows:
        label = str(row.get(key) or "unknown").strip() or "unknown"
        counts[label] = counts.get(label, 0) + 1
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))


def render_trial_report(summary: dict[str, Any]) -> str:
    evaluations = list(summary.get("evaluations") or [])
    prioritized = list(summary.get("prioritized_gaps") or [])
    analytics = dict(summary.get("analytics") or {})
    analytics_summary = dict(analytics.get("summary") or {})
    environment = dict(summary.get("environment") or {})
    lines = [
        "# Nova Trial Report",
        "",
        f"- Generated: {summary.get('generated_at', '')}",
        f"- Scenario count: {summary.get('scenario_count', 0)}",
        f"- Passed: {summary.get('passed_count', 0)}",
        f"- Failed: {summary.get('failed_count', 0)}",
        f"- Total gaps: {len(prioritized)}",
        f"- Total turns: {analytics_summary.get('total_turns', 0)}",
        f"- Error rate: {analytics_summary.get('error_rate', 0.0)}",
        f"- Environment: budget={environment.get('usage_budget_state', 'unknown')}, "
        f"local_model={environment.get('local_model_state', 'unknown')}",
        "",
        "## Scenario Results",
        "",
    ]
    for evaluation in evaluations:
        status = "PASS" if evaluation.get("passed") else "FAIL"
        lines.append(
            f"- {status} `{evaluation.get('scenario')}` "
            f"score={evaluation.get('score')} gaps={evaluation.get('gap_count')} "
            f"capabilities={evaluation.get('capability_sequence')}"
        )

    lines.extend(["", "## Gap Summary", ""])
    if not prioritized:
        lines.append("- No gaps found.")
    else:
        severity_summary = ", ".join(f"{name}={count}" for name, count in _count_by_key(prioritized, "severity"))
        category_summary = ", ".join(f"{name}={count}" for name, count in _count_by_key(prioritized, "category"))
        top_scenarios = ", ".join(
            f"{name}={count}" for name, count in _count_by_key(prioritized, "scenario")[:8]
        )
        lines.append(f"- By severity: {severity_summary}")
        lines.append(f"- By category: {category_summary}")
        lines.append(f"- Top scenarios: {top_scenarios}")

    lines.extend(["", "## Prioritized Gaps", ""])
    if not prioritized:
        lines.append("- No gaps found.")
    else:
        for gap in prioritized:
            turn = f" turn={gap.get('turn_index')}" if gap.get("turn_index") else ""
            lines.append(
                f"- [{str(gap.get('severity') or 'low').upper()}] "
                f"{gap.get('scenario')} / {gap.get('category')}{turn}: {gap.get('message')}"
            )
            if gap.get("expected") is not None:
                lines.append(f"  Expected: {_format_report_value(gap.get('expected'))}")
            if gap.get("actual") is not None:
                lines.append(f"  Actual: {_format_report_value(gap.get('actual'))}")

    lines.extend(
        [
            "",
            "## Artifacts",
            "",
            f"- Run log directory: `{summary.get('run_log_dir', '')}`",
            f"- Analytics: `{summary.get('analytics_path', '')}`",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def run_trial_scenarios(
    scenario_dir: str | Path,
    output_dir: str | Path,
    *,
    include_trace: bool = False,
    profile: str = "trial",
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Run scenario library, log each transcript, evaluate gaps, and write a report."""

    scenarios = load_scenario_library(scenario_dir)
    out_root = Path(output_dir)
    logs_dir = out_root / "logs"
    reports_dir = out_root
    logs_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    run_records: list[dict[str, Any]] = []
    evaluations: list[dict[str, Any]] = []
    log_slug_counts: dict[str, int] = {}

    for scenario in scenarios:
        raw_script = scenario.get("script")
        script = list(raw_script) if isinstance(raw_script, list) else []
        scenario_expect = scenario.get("expect") if isinstance(scenario.get("expect"), dict) else {}
        transcript = run_script(script, include_trace=include_trace)
        evaluation = evaluate_trial(scenario, transcript)
        evaluations.append(evaluation)
        run_record = build_run_record(
            transcript,
            scenario=str(scenario.get("name") or ""),
            profile=profile,
            passed=bool(evaluation.get("passed")),
            repo_root=repo_root,
        )
        run_record["scenario"] = {
            "name": str(scenario.get("name") or ""),
            "path": str(scenario.get("path") or ""),
            "expect": dict(scenario_expect),
        }
        run_record["evaluation"] = evaluation
        run_record["transcript"] = transcript_to_dict(transcript)
        log_slug = _slug(str(scenario.get("name") or "scenario"))
        log_slug_counts[log_slug] = log_slug_counts.get(log_slug, 0) + 1
        log_name = log_slug if log_slug_counts[log_slug] == 1 else f"{log_slug}_{log_slug_counts[log_slug]}"
        log_path = logs_dir / f"{log_name}.json"
        log_path.write_text(json.dumps(run_record, indent=2), encoding="utf-8")
        run_records.append(run_record)

    analytics = aggregate_simulation_runs(run_records)
    analytics_path = export_analytics_json(analytics, out_root / "analytics.json")
    prioritized = prioritize_gaps(evaluations)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenario_count": len(scenarios),
        "passed_count": sum(1 for item in evaluations if item.get("passed")),
        "failed_count": sum(1 for item in evaluations if not item.get("passed")),
        "environment": _trial_environment_snapshot(),
        "evaluations": evaluations,
        "prioritized_gaps": prioritized,
        "analytics": analytics,
        "run_log_dir": str(logs_dir),
        "analytics_path": str(analytics_path),
    }
    report_path = reports_dir / "latest_trial_report.md"
    report_path.write_text(render_trial_report(summary), encoding="utf-8")
    summary["report_path"] = str(report_path)
    return summary


def _trial_environment_snapshot() -> dict[str, Any]:
    usage_state = "unknown"
    local_model_state = "unknown"
    try:
        from src.usage.provider_usage_store import provider_usage_store

        snapshot = provider_usage_store.snapshot()
        usage_state = str(snapshot.get("budget_state") or snapshot.get("budget_state_label") or "unknown")
    except Exception:
        pass
    try:
        from src.llm.llm_gateway import is_model_update_pending

        local_model_state = "update_pending" if is_model_update_pending() else "available_or_fallback"
    except Exception:
        pass
    return {
        "usage_budget_state": usage_state,
        "local_model_state": local_model_state,
        "brave_api_configured": bool(str(os.getenv("BRAVE_API_KEY") or "").strip()),
        "weather_api_configured": bool(str(os.getenv("WEATHER_API_KEY") or "").strip()),
    }


def default_scenario_dir() -> Path:
    return Path(__file__).resolve().parent / "scenarios"


def default_output_dir() -> Path:
    return Path(__file__).resolve().parent / "reports"


if __name__ == "__main__":
    result = run_trial_scenarios(default_scenario_dir(), default_output_dir(), include_trace=True)
    print(result["report_path"])
