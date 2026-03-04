from pathlib import Path

from src.audit import runtime_auditor


def test_render_current_runtime_state_markdown_contains_core_sections():
    report = {
        "generated_at_utc": "2026-01-01T00:00:00+00:00",
        "status": "pass",
        "summary": {
            "execution_gate_enabled": True,
            "mediator_mapped_capability_ids": [16, 17],
        },
        "discrepancies": [],
    }
    registry = {
        "capabilities": [
            {"id": 16, "name": "governed_web_search", "enabled": True, "status": "active", "risk_level": "low", "data_exfiltration": True},
            {"id": 22, "name": "open_file_folder", "enabled": False, "status": "active", "risk_level": "confirm", "data_exfiltration": False},
        ]
    }

    markdown = runtime_auditor.render_current_runtime_state_markdown(report, registry)

    assert "# runtime.md" in markdown
    assert "## Enabled capability IDs" in markdown
    assert "- [16]" in markdown
    assert "## Disabled capability IDs" in markdown
    assert "- [22]" in markdown
    assert "| 16 | governed_web_search | True |" in markdown


def test_write_current_runtime_state_snapshot_writes_runtime_md(monkeypatch, tmp_path: Path):
    output_path = tmp_path / "runtime.md"

    monkeypatch.setattr(runtime_auditor, "RUNTIME_SNAPSHOT_PATH", output_path)
    monkeypatch.setattr(
        runtime_auditor,
        "run_runtime_truth_audit",
        lambda: {
            "generated_at_utc": "2026-01-01T00:00:00+00:00",
            "status": "warn",
            "summary": {"execution_gate_enabled": True, "mediator_mapped_capability_ids": [16]},
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
                }
            ]
        },
    )

    returned_path = runtime_auditor.write_current_runtime_state_snapshot()

    assert returned_path == output_path
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert "# runtime.md" in content
    assert "TEST" in content
