from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
GOVERNOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "governor.py"
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"
STORE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "policies" / "atomic_policy_store.py"
VALIDATOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "policies" / "policy_validator.py"
EVENT_TYPES_PATH = PROJECT_ROOT / "nova_backend" / "src" / "ledger" / "event_types.py"


def test_governor_exposes_atomic_policy_validation_entrypoint():
    source = GOVERNOR_PATH.read_text(encoding="utf-8")

    assert "policy_validator" in source
    assert "validate_atomic_policy" in source
    assert "PolicyValidator" in source


def test_brain_server_exposes_policy_draft_foundation_commands():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")

    assert "POLICY_STATUS_COMMANDS" in source
    assert "POLICY_CREATE_RE" in source
    assert "POLICY_SHOW_RE" in source
    assert "POLICY_DELETE_RE" in source
    assert "_compile_atomic_policy_template" in source
    assert "policy create weekday calendar snapshot at 8:00 am" in source


def test_policy_foundation_has_persistent_store_and_validator_modules():
    store_source = STORE_PATH.read_text(encoding="utf-8")
    validator_source = VALIDATOR_PATH.read_text(encoding="utf-8")

    assert "atomic_policies.json" in store_source
    assert "create_draft(" in store_source
    assert "delete_policy(" in store_source
    assert "POLICY_CAPABILITY_RULES" in validator_source
    assert "Phase-6 foundation" in validator_source


def test_ledger_event_types_cover_policy_foundation():
    source = EVENT_TYPES_PATH.read_text(encoding="utf-8")

    assert '"POLICY_VALIDATED"' in source
    assert '"POLICY_VALIDATION_REJECTED"' in source
    assert '"POLICY_DRAFT_CREATED"' in source
    assert '"POLICY_DRAFT_VIEWED"' in source
    assert '"POLICY_DRAFT_DELETED"' in source
