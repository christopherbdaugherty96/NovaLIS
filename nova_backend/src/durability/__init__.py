"""Durability layout, corruption, maintenance, and snapshot contracts."""

from src.durability.corruption import (
    StateCorruptError,
    read_json_state,
    read_jsonl_state,
    require_state,
)
from src.durability.recovery_candidate import (
    RecoveryCandidateActivationError,
    RecoveryCandidateActivationResult,
    RecoveryCandidateError,
    RecoveryCandidateResult,
    RecoveryCandidateValidationError,
    RecoveryCandidateValidationResult,
    activate_recovery_candidate,
    active_recovery_generation,
    create_recovery_candidate,
    validate_recovery_candidate,
)
from src.durability.snapshot import (
    SnapshotError,
    SnapshotResult,
    SnapshotSourceConflictError,
    SnapshotValidationError,
    create_snapshot,
    validate_snapshot,
    validate_state_file,
)
from src.durability.state_layout import (
    LogicalStore,
    MigrationCandidate,
    MigrationFinding,
    canonical_user_data_root,
    detect_migration_state,
    logical_store_registry,
)

__all__ = [
    "LogicalStore",
    "MigrationCandidate",
    "MigrationFinding",
    "canonical_user_data_root",
    "detect_migration_state",
    "logical_store_registry",
    "StateCorruptError",
    "read_json_state",
    "read_jsonl_state",
    "require_state",
    "SnapshotError",
    "SnapshotResult",
    "SnapshotSourceConflictError",
    "SnapshotValidationError",
    "create_snapshot",
    "validate_state_file",
    "validate_snapshot",
    "RecoveryCandidateError",
    "RecoveryCandidateActivationError",
    "RecoveryCandidateActivationResult",
    "RecoveryCandidateResult",
    "RecoveryCandidateValidationError",
    "RecoveryCandidateValidationResult",
    "create_recovery_candidate",
    "validate_recovery_candidate",
    "activate_recovery_candidate",
    "active_recovery_generation",
]
