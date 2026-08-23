from __future__ import annotations

import importlib.util
import sys
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
            "scanner_scope": "requests-library usage over the existing runtime-auditor allowlist",
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
    match = [
        item for item in discrepancies if item.code == "KNOWN_DIRECT_NETWORK_EXCEPTION"
    ]

    assert len(match) == 1
    assert match[0].severity == "warning"
    assert match[0].details["exceptions"][0]["path"].endswith(
        "connections_api.py"
    )
    assert "requests-library" in match[0].details["scanner_scope"]
    assert "requests-based" in match[0].message


def test_unclassified_direct_network_path_is_hard_fail(monkeypatch):
    monkeypatch.setattr(
        ra,
        "_classify_direct_network_paths",
        lambda paths=None: {
            "scanner_scope": "requests-library usage over the existing runtime-auditor allowlist",
            "detected_paths": ["nova_backend/src/example.py"],
            "known_exceptions": [],
            "unclassified_paths": ["nova_backend/src/example.py"],
        },
    )

    discrepancies = ra._build_discrepancies(**_base_discrepancy_kwargs())
    match = [
        item for item in discrepancies if item.code == "UNCLASSIFIED_DIRECT_NETWORK_PATH"
    ]

    assert len(match) == 1
    assert match[0].severity == "hard_fail"
    assert "requests-based" in match[0].message


def test_phase9_status_uses_live_symbol_evidence_not_placeholder_paths(monkeypatch):
    monkeypatch.setattr(
        ra,
        "_phase_9_live_evidence",
        lambda: {"checks": [], "all_required_symbols_live": True},
    )
    registry = {
        "capabilities": [
            {
                "id": 63,
                "name": "openclaw_execute",
                "enabled": True,
                "status": "active",
            }
        ]
    }

    assert ra._phase_9_status(registry) == "ACTIVE"


def test_phase9_live_evidence_targets_active_modules_not_retired_placeholders():
    evidence = ra._phase_9_live_evidence()
    modules = {item["module"] for item in evidence["checks"]}

    assert "src.openclaw.thinking_loop" in modules
    assert "src.openclaw.tool_registry" in modules
    assert "src.openclaw.execution_memory" in modules
    assert "src.openclaw.agent_personality_bridge" in modules
    assert "src.identity.nova_self_awareness" in modules
    assert "src.openclaw.agent_thinking_loop" not in modules
    assert "src.openclaw.agent_tool_registry_bootstrap" not in modules
    assert "src.openclaw.agent_execution_memory" not in modules


def test_runtime_fingerprint_declares_expanded_scope_without_broadening_scanner():
    fp = ra._runtime_fingerprint([])
    fingerprint_paths = ra._fingerprinted_runtime_surface_paths()

    assert fp["scope_version"] == "behaviorally_active_v2"
    assert fp["runtime_surface_file_count"] > 0
    assert fp["runtime_surface_file_count"] == len(fingerprint_paths)
    assert all(path.exists() for path in fingerprint_paths)

    missing_allowed_paths = {
        path.resolve() for path in ra.ALLOWED_READ_PATHS if not path.resolve().exists()
    }
    assert fingerprint_paths.isdisjoint(missing_allowed_paths)

    runtime_doc_root = Path(ra.RUNTIME_DOC_DIR).resolve()
    assert all(
        not path.resolve().is_relative_to(runtime_doc_root)
        for path in fingerprint_paths
    )

    required_families = {"brain", "connections", "identity", "memory", "usage"}
    assert required_families.issubset(set(fp["source_families"]))

    fingerprint_relpaths = {
        path.resolve().relative_to(ra.PROJECT_ROOT).as_posix()
        for path in fingerprint_paths
        if path.resolve().is_relative_to(ra.PROJECT_ROOT)
    }
    for family in required_families:
        assert any(
            path.startswith(f"nova_backend/src/{family}/")
            for path in fingerprint_relpaths
        )

    scanner_paths = {
        path.resolve().relative_to(ra.PROJECT_ROOT).as_posix()
        for path in ra.ALLOWED_READ_PATHS
        if path.resolve().is_relative_to(ra.PROJECT_ROOT)
    }
    assert not any(path.startswith("nova_backend/src/usage/") for path in scanner_paths)
    assert ra._find_requests_usage_outside_network_mediator.__module__ == (
        "src.audit.runtime_auditor"
    )

    rendered = ra.render_runtime_fingerprint_markdown([])
    assert "scope_version: behaviorally_active_v2" in rendered
    assert "runtime_surface_file_count:" in rendered
    assert "source_families:" in rendered
    for family in required_families:
        assert family in rendered


def test_current_runtime_state_qualifies_network_and_execution_invariants():
    rendered = ra.render_current_runtime_state_markdown(
        {"discrepancies": []},
        {"capabilities": []},
    )

    assert "All outbound HTTP must pass NetworkMediator" not in rendered
    assert "All actions must pass GovernorMediator" not in rendered
    assert "All execution logged to ledger" not in rendered
    assert "requests-based direct paths detectable by the existing scanner" in rendered
    assert "## Generated Evidence Scope" in rendered
    assert "requests scanner" in rendered
    assert "Runtime Surface Families:" in rendered


def test_bypass_report_classifies_known_network_exception():
    rendered = ra.render_bypass_surfaces_markdown()

    assert "## requests-based direct-network classification" in rendered
    assert "existing requests-library scanner" in rendered
    assert "does not prove the absence of every possible network mechanism" in rendered
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


def _load_runtime_generator():
    repo_root = Path(__file__).resolve().parents[2]
    scripts_dir = repo_root / "scripts"
    script = scripts_dir / "generate_runtime_docs.py"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    spec = importlib.util.spec_from_file_location("b1_runtime_docs_generator", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generator_entrypoint_writes_instrumented_runtime_truth(tmp_path, monkeypatch):
    generator = _load_runtime_generator()

    assert getattr(ra, "_B1_RUNTIME_TRUTH_INSTRUMENTATION_INSTALLED", False) is True
    assert generator.write_current_runtime_state_snapshot is ra.write_current_runtime_state_snapshot

    actual_writer = generator.write_current_runtime_state_snapshot
    output = tmp_path / "CURRENT_RUNTIME_STATE.md"

    def write_to_temp():
        return actual_writer(output)

    monkeypatch.setattr(generator, "write_current_runtime_state_snapshot", write_to_temp)
    monkeypatch.setattr(generator, "refresh_obsidian_overlay", lambda: None)

    generator.main()

    current = output.read_text(encoding="utf-8")
    bypass = (tmp_path / "BYPASS_SURFACES.md").read_text(encoding="utf-8")
    fingerprint = (tmp_path / "RUNTIME_FINGERPRINT.md").read_text(encoding="utf-8")

    discrepancy_section = current.split("## Runtime Truth Discrepancies", 1)[1].split(
        "## Design Runtime Divergences", 1
    )[0]
    assert "KNOWN_DIRECT_NETWORK_EXCEPTION" in discrepancy_section
    assert "- None" not in discrepancy_section

    assert "src.openclaw.thinking_loop.ThinkingLoop" in current
    assert "src.openclaw.tool_registry.ToolRegistry" in current
    assert "src.openclaw.execution_memory.ExecutionMemory" in current
    assert (
        "src.openclaw.agent_personality_bridge.OpenClawAgentPersonalityBridge"
        in current
    )
    assert "src.identity.nova_self_awareness.build_self_awareness_block" in current
    assert "requests-based direct paths detectable by the existing scanner" in current

    assert "nova_backend/src/api/connections_api.py" in bypass
    assert "local_administrative_health_probe" in bypass
    assert "existing requests-library scanner" in bypass

    assert "scope_version: behaviorally_active_v2" in fingerprint
    for family in ("brain", "connections", "identity", "memory", "usage"):
        assert family in fingerprint


def _write_surface(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _minimal_operational_fixture(
    root: Path,
    *,
    daily_lane: str = "B1",
    roadmap_lane: str = "B1",
    canonical_index_lane: str = "B1",
) -> None:
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
    _write_surface(
        root,
        "docs/todo/ACTIVE_TODO.md",
        "### Wave B1 — runtime truth instrumentation\n",
    )
    _write_surface(
        root,
        "docs/CANONICAL/00_INDEX.md",
        "**Implementation:** code\n**Automated/recorded evidence:** tests\n"
        "current HEAD != immutable validated baseline\n"
        f"Current active stabilization lane: {canonical_index_lane}\n",
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
        f"Current active stabilization lane: {roadmap_lane}\n"
        "B1 runtime-truth instrumentation\n#335 OPEN / DRAFT / UNMERGED\n",
    )


def test_operational_truth_checker_accepts_consistent_lane(tmp_path):
    checker = _load_operational_checker()
    _minimal_operational_fixture(tmp_path)

    assert checker.check_operational_truth(tmp_path) == []
    assert "AGENTS.md" in checker.CHECKED_SURFACES
    assert "docs/CANONICAL/00_INDEX.md" in checker.CHECKED_SURFACES
    assert "docs/CANONICAL/07_ROADMAP_TRUTH.md" in checker.CHECKED_SURFACES
    assert "generated runtime truth/runtime behavior" in checker.NON_GOALS


def test_operational_truth_checker_detects_lane_mismatch(tmp_path):
    checker = _load_operational_checker()
    _minimal_operational_fixture(tmp_path, daily_lane="B2")

    errors = checker.check_operational_truth(tmp_path)
    assert any("active stabilization lane mismatch" in error for error in errors)


def test_operational_truth_checker_detects_roadmap_lane_drift(tmp_path):
    checker = _load_operational_checker()
    _minimal_operational_fixture(tmp_path, roadmap_lane="B2")

    errors = checker.check_operational_truth(tmp_path)
    assert any("active stabilization lane mismatch" in error for error in errors)


def test_operational_truth_checker_detects_canonical_index_lane_drift(tmp_path):
    checker = _load_operational_checker()
    _minimal_operational_fixture(tmp_path, canonical_index_lane="A1")

    errors = checker.check_operational_truth(tmp_path)
    assert any("active stabilization lane mismatch" in error for error in errors)
    assert any("canonical_index=A1" in error for error in errors)


def test_operational_truth_checker_requires_agents_surface(tmp_path):
    checker = _load_operational_checker()
    _minimal_operational_fixture(tmp_path)
    (tmp_path / "AGENTS.md").unlink()

    errors = checker.check_operational_truth(tmp_path)
    assert any("AGENTS.md" in error and "missing" in error for error in errors)
