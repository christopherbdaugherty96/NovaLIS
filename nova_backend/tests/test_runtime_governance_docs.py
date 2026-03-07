from pathlib import Path

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


def test_current_runtime_state_includes_required_sections():
    report = ra.run_runtime_truth_audit()
    registry = ra._load_registry()
    md = ra.render_current_runtime_state_markdown(report, registry)

    assert "## Execution Authority Model" in md
    assert "## Active Capabilities" in md
    assert "## Network Authority" in md
    assert "## Runtime Safety Guarantees" in md
    assert "## Runtime Fingerprint" in md
    assert "## Change Control" in md

    # Required checks
    assert "Capabilities using NetworkMediator: [16" in md
    assert "deepseek_uses_ollama_chat_directly=False" in md


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
    assert rows[0]["execution_surface"] in {"Governor â†’ Executor", "Governor â†’ Speech", "Governor â†’ NetworkMediator"}

