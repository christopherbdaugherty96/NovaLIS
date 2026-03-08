from __future__ import annotations

import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


EXPECTED_CAPABILITY_EXECUTOR_MAP: dict[int, str] = {
    16: "web_search_executor",
    17: "webpage_launch_executor",
    18: "tts_executor",
    19: "volume_executor",
    20: "media_executor",
    21: "brightness_executor",
    22: "open_folder_executor",
    31: "response_verification_executor",
    32: "os_diagnostics_executor",
    48: "multi_source_reporting_executor",
    49: "news_intelligence_executor.execute_summary",
    50: "news_intelligence_executor.execute_brief",
    51: "news_intelligence_executor.execute_topic_map",
    52: "story_tracker_executor.execute_update",
    53: "story_tracker_executor.execute_view",
    54: "analysis_document_executor",
}

REFUSAL_HINTS = (
    "can't do that",
    "cannot do that",
    "refusal",
    "refused",
    "not allowed",
    "not permitted",
    "blocked",
)


def current_git_commit(repo_root: str | Path | None = None) -> str:
    root = Path(repo_root) if repo_root else Path(__file__).resolve().parents[3]
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or "unknown"
    except Exception:
        return "unknown"


def build_run_metadata(
    *,
    scenario: str = "",
    profile: str = "simulation",
    passed: bool = True,
    total_turns: int = 0,
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario": scenario,
        "commit": current_git_commit(repo_root=repo_root),
        "profile": profile,
        "total_turns": int(total_turns),
        "pass_fail_summary": "PASS" if passed else "FAIL",
    }


def _percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return round(float(ordered[0]), 3)
    rank = (len(ordered) - 1) * p
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    frac = rank - low
    result = ordered[low] + (ordered[high] - ordered[low]) * frac
    return round(float(result), 3)


def _is_refusal(turn: dict[str, Any]) -> bool:
    if turn.get("errors"):
        return True
    text = str(turn.get("nova_response") or "").lower()
    return any(h in text for h in REFUSAL_HINTS)


def aggregate_simulation_runs(run_records: list[dict[str, Any]]) -> dict[str, Any]:
    capability_latencies: dict[int, list[float]] = defaultdict(list)
    executor_latencies: dict[str, list[float]] = defaultdict(list)
    capability_counts: Counter[int] = Counter()
    executor_counts: Counter[str] = Counter()
    governor_decision_counts: Counter[str] = Counter()
    failing_prompt_counts: Counter[str] = Counter()

    scenario_stats: dict[str, dict[str, float]] = defaultdict(
        lambda: {"transcript_count": 0, "total_turns": 0, "error_turns": 0, "refusal_turns": 0}
    )
    chain_length_distribution: Counter[int] = Counter()
    all_turn_latencies: list[float] = []

    total_turns = 0
    error_turns = 0
    refusal_turns = 0
    mismatch_count = 0
    unknown_capability_count = 0
    run_timestamps: list[str] = []
    run_profiles: Counter[str] = Counter()
    run_scenarios: Counter[str] = Counter()

    for record in run_records:
        metadata = record.get("run_metadata") if isinstance(record.get("run_metadata"), dict) else {}
        scenario_name = str(metadata.get("scenario") or "unspecified")
        if metadata.get("timestamp"):
            run_timestamps.append(str(metadata["timestamp"]))
        if metadata.get("profile"):
            run_profiles[str(metadata["profile"])] += 1
        run_scenarios[scenario_name] += 1
        transcript = record.get("transcript") if isinstance(record.get("transcript"), dict) else {}
        turns = transcript.get("turns") if isinstance(transcript.get("turns"), list) else []
        capped_turns = [t for t in turns if isinstance(t, dict) and t.get("capability_triggered") is not None]
        chain_length_distribution[len(capped_turns)] += 1

        scenario_stats[scenario_name]["transcript_count"] += 1
        scenario_stats[scenario_name]["total_turns"] += len(turns)

        for turn in turns:
            if not isinstance(turn, dict):
                continue
            total_turns += 1
            cap_raw = turn.get("capability_triggered")
            executor = str(turn.get("capability_executor") or "").strip()
            latency = float(turn.get("execution_time_ms") or 0.0)
            all_turn_latencies.append(latency)
            decision = str(turn.get("governor_decision") or "").strip() or "unknown"
            governor_decision_counts[decision] += 1

            had_error = bool(turn.get("errors"))
            is_refusal = _is_refusal(turn)
            if had_error:
                error_turns += 1
                scenario_stats[scenario_name]["error_turns"] += 1
                prompt = str(turn.get("user_message") or "").strip()
                if prompt:
                    failing_prompt_counts[prompt] += 1
            if is_refusal:
                refusal_turns += 1
                scenario_stats[scenario_name]["refusal_turns"] += 1

            if cap_raw is None:
                if executor:
                    mismatch_count += 1
                continue

            try:
                cap_id = int(cap_raw)
            except Exception:
                unknown_capability_count += 1
                continue

            capability_counts[cap_id] += 1
            capability_latencies[cap_id].append(latency)
            if executor:
                executor_counts[executor] += 1
                executor_latencies[executor].append(latency)

            expected_executor = EXPECTED_CAPABILITY_EXECUTOR_MAP.get(cap_id)
            if expected_executor is None:
                unknown_capability_count += 1
            elif executor != expected_executor:
                mismatch_count += 1

    capabilities = {}
    for cap_id in sorted(capability_counts.keys()):
        latencies = capability_latencies.get(cap_id, [])
        capabilities[str(cap_id)] = {
            "count": int(capability_counts[cap_id]),
            "p50_latency_ms": _percentile(latencies, 0.50),
            "p95_latency_ms": _percentile(latencies, 0.95),
        }

    executors = {}
    for executor_name in sorted(executor_counts.keys()):
        latencies = executor_latencies.get(executor_name, [])
        executors[executor_name] = {
            "count": int(executor_counts[executor_name]),
            "mean_latency_ms": round(float(mean(latencies)) if latencies else 0.0, 3),
        }

    scenarios = {}
    for scenario_name in sorted(scenario_stats.keys()):
        stats = scenario_stats[scenario_name]
        turns = int(stats["total_turns"])
        err = int(stats["error_turns"])
        ref = int(stats["refusal_turns"])
        scenarios[scenario_name] = {
            "transcript_count": int(stats["transcript_count"]),
            "total_turns": turns,
            "error_rate": round((err / turns) if turns else 0.0, 4),
            "refusal_rate": round((ref / turns) if turns else 0.0, 4),
        }

    return {
        "run_metadata": {
            "run_count": len(run_records),
            "profiles": dict(sorted(run_profiles.items())),
            "scenarios": dict(sorted(run_scenarios.items())),
            "timestamp_start": min(run_timestamps) if run_timestamps else "",
            "timestamp_end": max(run_timestamps) if run_timestamps else "",
        },
        "summary": {
            "run_count": len(run_records),
            "scenario_transcript_count": sum(v["transcript_count"] for v in scenarios.values()),
            "total_turns": total_turns,
            "error_rate": round((error_turns / total_turns) if total_turns else 0.0, 4),
            "refusal_rate": round((refusal_turns / total_turns) if total_turns else 0.0, 4),
        },
        "turn_latency": {
            "mean_turn_latency_ms": round(float(mean(all_turn_latencies)) if all_turn_latencies else 0.0, 3),
            "p50_turn_latency_ms": _percentile(all_turn_latencies, 0.50),
            "p95_turn_latency_ms": _percentile(all_turn_latencies, 0.95),
        },
        "capability_chain_length": {
            str(length): int(count) for length, count in sorted(chain_length_distribution.items())
        },
        "capabilities": capabilities,
        "executors": executors,
        "governor_decisions": dict(sorted(governor_decision_counts.items())),
        "integrity": {
            "capability_executor_mismatch_count": mismatch_count,
            "unknown_capability_count": unknown_capability_count,
        },
        "top_failing_user_prompts": [
            {"prompt": prompt, "count": int(count)}
            for prompt, count in failing_prompt_counts.most_common(10)
        ],
        "scenarios": scenarios,
    }


def load_run_records(directory: str | Path) -> list[dict[str, Any]]:
    root = Path(directory)
    if not root.exists():
        raise FileNotFoundError(f"Run directory not found: {root}")
    out: list[dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict) and isinstance(payload.get("transcript"), dict):
            out.append(payload)
    return out


def export_analytics_json(analytics: dict[str, Any], path: str | Path) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(analytics, indent=2), encoding="utf-8")
    return out_path


def export_analytics_html(analytics: dict[str, Any], path: str | Path) -> Path:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    summary = analytics.get("summary", {})
    run_metadata = analytics.get("run_metadata", {})
    turn_latency = analytics.get("turn_latency", {})
    chain = analytics.get("capability_chain_length", {})
    caps = analytics.get("capabilities", {})
    executors = analytics.get("executors", {})
    decisions = analytics.get("governor_decisions", {})
    integrity = analytics.get("integrity", {})

    def _rows(items: list[tuple[str, Any]]) -> str:
        return "\n".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in items)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Nova Simulation Analytics</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; background: #0b1020; color: #e8eefc; }}
    h1, h2 {{ margin: 0 0 12px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    .card {{ border: 1px solid #24314f; border-radius: 10px; padding: 12px; background: #111a31; }}
    table {{ width: 100%; border-collapse: collapse; }}
    td {{ border-bottom: 1px solid #24314f; padding: 6px; vertical-align: top; }}
  </style>
</head>
<body>
  <h1>Nova Simulation Analytics</h1>
  <div class="grid">
    <div class="card"><h2>Run Metadata</h2><table>{_rows([(k, run_metadata[k]) for k in sorted(run_metadata.keys())])}</table></div>
    <div class="card"><h2>Summary</h2><table>{_rows([(k, summary[k]) for k in sorted(summary.keys())])}</table></div>
    <div class="card"><h2>Turn Latency</h2><table>{_rows([(k, turn_latency[k]) for k in sorted(turn_latency.keys())])}</table></div>
    <div class="card"><h2>Chain Length</h2><table>{_rows([(k, chain[k]) for k in sorted(chain.keys())])}</table></div>
    <div class="card"><h2>Integrity</h2><table>{_rows([(k, integrity[k]) for k in sorted(integrity.keys())])}</table></div>
    <div class="card"><h2>Capabilities</h2><table>{_rows([(k, caps[k]) for k in sorted(caps.keys())])}</table></div>
    <div class="card"><h2>Executors</h2><table>{_rows([(k, executors[k]) for k in sorted(executors.keys())])}</table></div>
    <div class="card"><h2>Governor Decisions</h2><table>{_rows([(k, decisions[k]) for k in sorted(decisions.keys())])}</table></div>
  </div>
</body>
</html>
"""
    out_path.write_text(html, encoding="utf-8")
    return out_path
