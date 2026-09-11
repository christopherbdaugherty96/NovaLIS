"""Durability layout, corruption, maintenance, and snapshot contracts."""

from src.durability.corruption import (
    StateCorruptError,
    read_json_state,
    read_jsonl_state,
    require_state,
)
from src.durability.snapshot import (
    SnapshotError,
    SnapshotResult,
    SnapshotSourceConflictError,
    SnapshotValidationError,
    create_snapshot,
    validate_snapshot,
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
    "validate_snapshot",
]
