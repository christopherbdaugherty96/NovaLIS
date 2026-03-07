from pathlib import Path

from src.audit import runtime_auditor


def test_runtime_doc_path_points_to_current_runtime_state_md():
    expected = (Path(__file__).resolve().parents[3] / "docs" / "current_runtime" / "CURRENT_RUNTIME_STATE.md").resolve()
    assert runtime_auditor.RUNTIME_DOC_PATH.resolve() == expected


def test_render_current_runtime_state_markdown_contains_core_sections():
    report = {
        "generated_at_utc": "2026-01-01T00:00:00+00:00",
        "status": "pass",
        "summary": {
            "execution_gate_enabled": True,
            "mediator_mapped_capability_ids": [16, 32],
        },
        "discrepancies": [],
    }
    registry = {
        "capabilities": [
            {"id": 16, "name": "governed_web_search", "enabled": True, "status": "active", "risk_level": "low", "data_exfiltration": True},
            {"id": 32, "name": "governed_file_ops", "enabled": True, "status": "active", "risk_level": "confirm", "data_exfiltration": False},
            {"id": 22, "name": "open_file_folder", "enabled": False, "status": "active", "risk_level": "confirm", "data_exfiltration": False},
        ]
    }

    markdown = runtime_auditor.render_current_runtime_state_markdown(report, registry)

    assert "# NOVA - CURRENT RUNTIME STATE" in markdown
    assert "## Active Capabilities" in markdown
    assert "| 16 | governed_web_search | Governed runtime capability |" in markdown
    assert "## Runtime Fingerprint" in markdown
    assert "- Capabilities enabled: [16, 32]" in markdown
    assert "- Capabilities disabled: [22]" in markdown


def test_write_current_runtime_state_snapshot_writes_current_runtime_state_and_creates_dir(monkeypatch, tmp_path: Path):
    output_path = tmp_path / "docs" / "current_runtime" / "CURRENT_RUNTIME_STATE.md"

    monkeypatch.setattr(
        runtime_auditor,
        "run_runtime_truth_audit",
        lambda: {
            "generated_at_utc": "2026-01-01T00:00:00+00:00",
            "status": "warn",
            "summary": {"execution_gate_enabled": True, "mediator_mapped_capability_ids": [16, 32]},
            "discrepancies": [{"severity": "warning", "code": "TEST", "message": "test message"}],
        },
    )
    monkeypatch.setattr(
        runtime_auditor,
        "_load_registry",
        lambda: {
            "capabilities": [
                {
                    "id": 16,
                    "name": "governed_web_search",
                    "enabled": True,
                    "status": "active",
                    "risk_level": "low",
                    "data_exfiltration": True,
                },
                {
                    "id": 32,
                    "name": "governed_file_ops",
                    "enabled": True,
                    "status": "active",
                    "risk_level": "confirm",
                    "data_exfiltration": False,
                },
            ]
        },
    )

    returned_path = runtime_auditor.write_current_runtime_state_snapshot(path=output_path)

    assert returned_path == output_path.resolve()
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "# NOVA - CURRENT RUNTIME STATE" in content
    assert "- Capabilities enabled: [16, 32]" in content
    assert "TEST" in content
