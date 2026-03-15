from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
GOVERNOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "governor.py"
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"
STORE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "policies" / "atomic_policy_store.py"
VALIDATOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "policies" / "policy_validator.py"
EVENT_TYPES_PATH = PROJECT_ROOT / "nova_backend" / "src" / "ledger" / "event_types.py"
TOPOLOGY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "capability_topology.py"
EXECUTOR_GATE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "policy_executor_gate.py"


def test_governor_exposes_atomic_policy_validation_entrypoint():
    source = GOVERNOR_PATH.read_text(encoding="utf-8")

    assert "policy_validator" in source
    assert "validate_atomic_policy" in source
    assert "PolicyValidator" in source
    assert "capability_topology" in source
    assert "policy_executor_gate" in source
    assert "simulate_atomic_policy" in source
    assert "run_atomic_policy_once" in source


def test_brain_server_exposes_policy_draft_foundation_commands():
    source = BRAIN_SERVER_PATH.read_text(encoding="utf-8")

    assert "POLICY_STATUS_COMMANDS" in source
    assert "POLICY_CREATE_RE" in source
    assert "POLICY_SHOW_RE" in source
    assert "POLICY_DELETE_RE" in source
    assert "POLICY_SIMULATE_RE" in source
    assert "POLICY_RUN_ONCE_RE" in source
    assert "_compile_atomic_policy_template" in source
    assert "policy create weekday calendar snapshot at 8:00 am" in source
    assert "policy simulate <id>" in source
    assert "policy run <id> once" in source


def test_policy_foundation_has_persistent_store_and_validator_modules():
    store_source = STORE_PATH.read_text(encoding="utf-8")
    validator_source = VALIDATOR_PATH.read_text(encoding="utf-8")
    topology_source = TOPOLOGY_PATH.read_text(encoding="utf-8")
    gate_source = EXECUTOR_GATE_PATH.read_text(encoding="utf-8")

    assert "atomic_policies.json" in store_source
    assert "create_draft(" in store_source
    assert "delete_policy(" in store_source
    assert "record_simulation(" in store_source
    assert "record_manual_run(" in store_source
    assert "POLICY_CAPABILITY_RULES" in validator_source
    assert "Phase-6 foundation" in validator_source
    assert "policy_delegatable" in topology_source
    assert "AUTHORITY_CLASS_ORDER" in topology_source
    assert "PolicyExecutorGateDecision" in gate_source
    assert "Allowed under current Phase-6 delegation rules." in gate_source


def test_ledger_event_types_cover_policy_foundation():
    source = EVENT_TYPES_PATH.read_text(encoding="utf-8")

    assert '"POLICY_VALIDATED"' in source
    assert '"POLICY_VALIDATION_REJECTED"' in source
    assert '"POLICY_DRAFT_CREATED"' in source
    assert '"POLICY_DRAFT_VIEWED"' in source
    assert '"POLICY_DRAFT_DELETED"' in source
    assert '"POLICY_SIMULATED"' in source
    assert '"POLICY_EXECUTION_ATTEMPTED"' in source
    assert '"POLICY_EXECUTION_BLOCKED"' in source
    assert '"POLICY_EXECUTION_COMPLETED"' in source
