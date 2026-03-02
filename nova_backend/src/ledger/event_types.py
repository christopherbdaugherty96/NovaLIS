"""Canonical ledger event taxonomy for Phase-4 runtime."""

_ACTION = "ACTION"

EVENT_TYPES = frozenset(
    {
        f"{_ACTION}_ATTEMPTED",
        f"{_ACTION}_COMPLETED",
        "SEARCH_QUERY",
        "WEBPAGE_LAUNCH",
        "EXTERNAL_NETWORK_CALL",
        "NETWORK_CALL_FAILED",
        "MODEL_UPDATED",
        "EXECUTION_TIMEOUT",
        "EXECUTION_MEMORY_EXCEEDED",
    }
)
