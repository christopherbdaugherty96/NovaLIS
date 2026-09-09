"""Durability layout contracts and read-only migration discovery."""

from src.durability.corruption import StateCorruptError, read_json_state, require_state
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
    "require_state",
]
