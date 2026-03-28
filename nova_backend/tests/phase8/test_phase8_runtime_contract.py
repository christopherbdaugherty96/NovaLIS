from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_STATE_PATH = PROJECT_ROOT / "docs" / "current_runtime" / "CURRENT_RUNTIME_STATE.md"
REGISTRY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "config" / "registry.json"


def test_phase8_runtime_truth_reports_active_narrow_foundation():
    content = RUNTIME_STATE_PATH.read_text(encoding="utf-8")

    assert "| Phase 8 | ACTIVE |" in content
    assert "Manual strict preflight is active." in content
    assert "Scheduled home-agent runtime is available behind explicit settings control" in content
    assert "broader envelope-governed execution still remains deferred" in content


def test_all_active_capabilities_now_have_human_readable_descriptions():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    active_capabilities = [item for item in registry["capabilities"] if item["status"] == "active"]

    missing = [item["id"] for item in active_capabilities if not str(item.get("description", "")).strip()]

    assert not missing, f"Active capabilities missing descriptions: {missing}"


def test_phase8_runtime_capability_table_no_longer_uses_placeholder_descriptions():
    content = RUNTIME_STATE_PATH.read_text(encoding="utf-8")

    assert "Governed runtime capability" not in content
