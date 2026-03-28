from pathlib import Path
import re

from src.audit import runtime_auditor as ra


def test_current_runtime_state_path_is_docs_current_runtime():
    assert ra.RUNTIME_DOC_PATH.as_posix().endswith("docs/current_runtime/CURRENT_RUNTIME_STATE.md")


def test_governance_docs_generation(tmp_path, monkeypatch):
    runtime_dir = tmp_path / "docs" / "current_runtime"
    monkeypatch.setattr(ra, "RUNTIME_DOC_DIR", runtime_dir)
    monkeypatch.setattr(ra, "RUNTIME_DOC_PATH", runtime_dir / "CURRENT_RUNTIME_STATE.md")
    monkeypatch.setattr(ra, "GOVERNANCE_MATRIX_PATH", runtime_dir / "GOVERNANCE_MATRIX.md")
    monkeypatch.setattr(ra, "SKILL_SURFACE_MAP_PATH", runtime_dir / "SKILL_SURFACE_MAP.md")
    monkeypatch.setattr(ra, "BYPASS_SURFACES_PATH", runtime_dir / "BYPASS_SURFACES.md")
    monkeypatch.setattr(ra, "RUNTIME_FINGERPRINT_PATH", runtime_dir / "RUNTIME_FINGERPRINT.md")
    monkeypatch.setattr(ra, "GOVERNANCE_MATRIX_TREE_PATH", runtime_dir / "GOVERNANCE_MATRIX_TREE.md")
    monkeypatch.setattr(ra, "ALLOWED_READ_PATHS", set(ra.ALLOWED_READ_PATHS) | {ra.RUNTIME_DOC_PATH})

    out = ra.write_current_runtime_state_snapshot(path=ra.RUNTIME_DOC_PATH)

    assert out == ra.RUNTIME_DOC_PATH.resolve()
    assert runtime_dir.exists()

    files = {
        "CURRENT_RUNTIME_STATE.md": "# NOVA - CURRENT RUNTIME STATE",
        "GOVERNANCE_MATRIX.md": "# GOVERNANCE_MATRIX",
        "SKILL_SURFACE_MAP.md": "# SKILL_SURFACE_MAP",
        "BYPASS_SURFACES.md": "# BYPASS_SURFACES",
        "RUNTIME_FINGERPRINT.md": "# RUNTIME_FINGERPRINT",
        "GOVERNANCE_MATRIX_TREE.md": "# GOVERNANCE_MATRIX_TREE",
    }

    for name, anchor in files.items():
        content = (runtime_dir / name).read_text(encoding="utf-8")
        assert anchor in content

    skill_map = (runtime_dir / "SKILL_SURFACE_MAP.md").read_text(encoding="utf-8")
    assert "src/skills/web_search.py" not in skill_map
    assert "src/skills/web_search_skill.py" not in skill_map
    assert "intentionally omitted from this live runtime map" in skill_map
    for module in (
        "src/skills/system.py",
        "src/skills/calendar.py",
        "src/skills/weather.py",
        "src/skills/news.py",
        "src/skills/general_chat.py",
    ):
        assert module in skill_map


def test_current_runtime_state_includes_required_sections():
    report = ra.run_runtime_truth_audit()
    registry = ra._load_registry()
    md = ra.render_current_runtime_state_markdown(report, registry)

    assert "## Phase Activation Matrix" in md
    assert "## Runtime Governance Spine" in md
    assert "## Active Capabilities" in md
    assert "## Runtime Systems" in md
    assert "## Known Runtime Gaps" in md
    assert "## Runtime Invariants" in md
    assert "## Runtime Fingerprint" in md

    assert "Manual edits: NOT PERMITTED" in md
    assert "| 49 | headline_summary |" in md


def test_runtime_fingerprint_markdown_omits_volatile_fields():
    md = ra.render_runtime_fingerprint_markdown([16, 48, 54])
    assert "runtime_surface_hash" in md
    assert "runtime_fingerprint_hash" in md
    assert "git_commit_hash" not in md
    assert "git_dirty" not in md
    assert "generated_at_utc" not in md
    assert "python_version" not in md
    assert "platform" not in md


def test_runtime_surface_hash_consistent_between_runtime_docs():
    report = ra.run_runtime_truth_audit()
    registry = ra._load_registry()
    state_md = ra.render_current_runtime_state_markdown(report, registry)
    fp_md = ra.render_runtime_fingerprint_markdown(ra._enabled_registry_ids(registry))

    state_match = re.search(r"^- Runtime Surface Hash: ([a-f0-9]{64})$", state_md, flags=re.MULTILINE)
    fp_match = re.search(r"^- runtime_surface_hash: ([a-f0-9]{64})$", fp_md, flags=re.MULTILINE)

    assert state_match is not None
    assert fp_match is not None
    assert state_match.group(1) == fp_match.group(1)


def test_governance_matrix_tree_up_to_date_with_renderer():
    registry = ra._load_registry()
    expected = ra.render_governance_matrix_tree_markdown(registry)
    current = ra.GOVERNANCE_MATRIX_TREE_PATH.read_text(encoding="utf-8")
    assert current == expected


def test_derived_fields_do_not_crash_with_missing_optional_reads(monkeypatch):
    registry = {"capabilities": [{"id": 999, "name": "x", "enabled": True, "status": "active", "phase_introduced": "4", "risk_level": "low", "data_exfiltration": False}]}

    real_safe_read = ra._safe_read

    def fake_safe_read(path: Path) -> str:
        if path in {ra.GOVERNOR_PATH, ra.NETWORK_MEDIATOR_PATH, ra.LEDGER_WRITER_PATH}:
            return ""
        return real_safe_read(path)

    monkeypatch.setattr(ra, "_safe_read", fake_safe_read)
    rows = ra._derive_capability_governance_rows(registry)

    assert len(rows) == 1
    assert "authority_class" in rows[0]
    assert rows[0]["execution_surface"] in {"Governor -> Executor", "Governor -> Speech", "Governor -> NetworkMediator"}

