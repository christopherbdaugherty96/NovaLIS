from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

from tests.simulation.analytics import (
    aggregate_simulation_runs,
    export_analytics_html,
    export_analytics_json,
)
from tests.simulation.conversation_runner import build_run_record
from tests.simulation.conversation_simulator import run_simulation

from .stress_generator import generate_stress_scripts
from .stress_profiles import PROFILES, StressProfile


def run_profile(profile: StressProfile, *, seed: int = 42) -> dict[str, Any]:
    scripts = generate_stress_scripts(profile, seed=seed)
    run_records = []
    for idx, script in enumerate(scripts, start=1):
        transcript = run_simulation(script)
        run_records.append(
            build_run_record(
                transcript,
                scenario=f"stress:{profile.name}:{idx}",
                profile=f"stress-{profile.name}",
                passed=True,
            )
        )
    analytics = aggregate_simulation_runs(run_records)
    return {"profile": profile.name, "seed": seed, "run_records": run_records, "analytics": analytics}


def export_profile_reports(result: dict[str, Any], report_dir: str | Path) -> dict[str, Path]:
    root = Path(report_dir)
    root.mkdir(parents=True, exist_ok=True)

    profile = str(result.get("profile") or "unknown")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    json_path = root / f"stress_run_{profile}_{timestamp}.json"
    html_path = root / f"stress_run_{profile}_{timestamp}.html"

    export_analytics_json(result["analytics"], json_path)
    export_analytics_html(result["analytics"], html_path)
    return {"json": json_path, "html": html_path}


def _build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Nova cognitive stress simulations.")
    parser.add_argument("--profile", choices=sorted(PROFILES.keys()), default="light")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--report-dir",
        default=str(Path(__file__).resolve().parents[4] / "docs" / "testing" / "reports"),
    )
    parser.add_argument("--export", action="store_true")
    return parser


def main() -> int:
    args = _build_cli().parse_args()
    profile = PROFILES[args.profile]
    result = run_profile(profile, seed=args.seed)
    analytics = result["analytics"]
    summary = analytics.get("summary", {})
    print(f"Profile: {profile.name}")
    print(f"Conversations: {profile.conversation_count}")
    print(f"Turns: {summary.get('total_turns', 0)}")
    print(f"Refusal rate: {summary.get('refusal_rate', 0.0)}")
    print(f"Error rate: {summary.get('error_rate', 0.0)}")
    if args.export:
        outputs = export_profile_reports(result, args.report_dir)
        print(f"JSON: {outputs['json']}")
        print(f"HTML: {outputs['html']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

