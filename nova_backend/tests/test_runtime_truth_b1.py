from __future__ import annotations

import importlib.util
from pathlib import Path

from src.audit import runtime_auditor as ra


def _base_discrepancy_kwargs() -> dict:
    return {
        "runtime_doc_enabled_ids": [16],
        "registry_enabled_ids": [16],
        "mediator_mapped_ids": [16],
        "model_path_signals": {
            "deepseek_uses_ollama_chat_directly": False,
            "general_chat_uses_ollama_chat_directly": False,
        },
        "execution_gate_enabled": True,
    }


def test_known_direct_network_exception_is_visible_warning(monkeypatch):
    monkeypatch.setattr(
        ra,
        "_classify_direct_network_paths",
        lambda paths=None: {
            "detected_paths": ["nova_backend/src/api/connections_api.py"],
            "known_exceptions": [
                {
                    "path": "nova_backend/src/api/connections_api.py",
                    "classification": "local_administrative_health_probe",
                    "disposition": "pending_explicit_runtime_governance_disposition",
                    "reason": "test",
                }
            ],
            "unclassified_paths": [],
        },
    )

    discrepancies = ra._build_discrepancies(**_base_discrepancy_kwargs())
    match = [item for item in discrepancies if item.code == "KNOWN_DIRECT_NETWORK_EXCEPTION"]

    assert len(match) == 1
    assert match[0].severity == "warning"
    assert match[0].details["exceptions"][0]["path"].endswith("connections_api.py")


def test_unclassified_direct_network_path_is_hard_fail(monkeypatch):
    monkeypatch.setattr(
        ra,
        "_classify_direct_network_paths",
        lambda paths=None: {
            "detected_paths": ["nova_backend/src/example.py"],
            "known_exceptions": [],
            "unclassified_paths": ["nova_backend/src/example.py"],
        },
    )

    discrepancies = ra._build_discrepancies(**_base_discrepancy_kwargs())
    match = [item for item in discrepancies if item.code == "UNCLASSIFIED_DIRECT_NETWORK_PATH"]

    assert len(match) == 1
    assert match[0].severity == "hard_fail"


def test_phase9_status_uses_live_symbol_evidence_not_placeholder_paths(monkeypatch):
    monkeypatch.setattr(
        ra,
        "_phase_9_live_evidence",
        lambda: {"checks": [], "all_required_symbols_live": True},
    )
    registry = {
        "capabilities": [
            {"id": 63, "name": "openclaw_execute", "enabled": True, "status": "active"}
        ]
    }

    assert ra._phase_9_status(registry) == "ACTIVE"


def test_phase9_live_evidence_targets_active_modules_not_retired_placeholders():
    evidence = ra._phase_9_live_evidence()
    modules = {item["module"] for item in evidence["checks"]}

    assert "src.openclaw.thinking_loop" in modules
    assert "src.openclaw.tool_registry" in modules
    assert "src.openclaw.execution_memory" in modules
    assert "src.openclaw.agent_thinking_loop" not in modules
    assert "src.openclaw.agent_tool_registry_bootstrap" not in modules
    assert "src.openclaw.agent_execution_memory" not in modules


def test_runtime_fingerprint_declares_expanded_scope():
    fp = ra._runtime_fingerprint([])

    assert fp["scope_version"] == "behaviorally_active_v2"
    assert fp["runtime_surface_file_count"] > 0

    rendered = ra.render_runtime_fingerprint_markdown([])
    assert "scope_version: behaviorally_active_v2" in rendered
    assert "runtime_surface_file_count:" in rendered


def test_current_runtime_state_qualifies_network_and_execution_invariants():
    rendered = ra.render_current_runtime_state_markdown(
        {"discrepancies": []},
        {"capabilities": []},
    )

    assert "All outbound HTTP must pass NetworkMediator" not in rendered
    assert "All actions must pass GovernorMediator" not in rendered
    assert "All execution logged to ledger" not in rendered
    assert "detected direct-network exceptions are reported separately" in rendered
    assert "## Generated Evidence Scope" in rendered


def test_bypass_report_classifies_known_network_exception():
    rendered = ra.render_bypass_surfaces_markdown()

    assert "## Direct-network classification" in rendered
    assert "nova_backend/src/api/connections_api.py" in rendered
    assert "local_administrative_health_probe" in rendered


def _load_operational_checker():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "check_operational_truth_consistency.py"
    spec = importlib.util.spec_from_file_location("operational_truth_checker", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_surface(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _minimal_operational_fixture(root: Path, *, daily_lane: str = "B1") -> None:
    _write_surface(root, "AGENTS.md", "## Wave B1 Current Development State\n")
    _write_surface(
        root,
        ".agent_context/current_priority.md",
        "## Wave B1 — Runtime Truth Instrumentation\n#335 OPEN / DRAFT / UNMERGED\n",
    )
    _write_surface(
        root,
        "docs/status/CURRENT_WORK_STATUS.md",
        "WAVE B1 — runtime truth instrumentation\n",
    )
    _write_surface(
        root,
        "docs/status/DAILY_COMMAND_CENTER.md",
        f"ACTIVE LANE:\n  Wave {daily_lane} — runtime truth instrumentation\n",
    )
    _write_surface(root, "docs/todo/ACTIVE_TODO.md", "### Wave B1 — runtime truth instrumentation\n")
    _write_surface(
        root,
        "docs/CANONICAL/00_INDEX.md",
        "**Implementation:** code\n**Automated/recorded evidence:** tests\n"
        "current HEAD != immutable validated baseline\n",
    )
    _write_surface(
        root,
        "docs/CANONICAL/03_GOVERNANCE_TRUTH.md",
        "Governed capability plane\nLocal operator / administrative plane\n"
        "Bounded agent / routine plane\nnova_backend/src/api/connections_api.py\n",
    )
    _write_surface(
        root,
        "docs/CANONICAL/07_ROADMAP_TRUTH.md",
        "B1 runtime-truth instrumentation\n#335 OPEN / DRAFT / UNMERGED\n",
    )


def test_operational_truth_checker_accepts_consistent_lane(tmp_path):
    checker = _load_operational_checker()
    _minimal_operational_fixture(tmp_path)

    assert checker.check_operational_truth(tmp_path) == []


def test_operational_truth_checker_detects_lane_mismatch(tmp_path):
    checker = _load_operational_checker()
    _minimal_operational_fixture(tmp_path, daily_lane="B2")

    errors = checker.check_operational_truth(tmp_path)
    assert any("active stabilization lane mismatch" in error for error in errors)
