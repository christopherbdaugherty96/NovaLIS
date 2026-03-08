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
        "MODEL_NETWORK_CALL",
        "MODEL_NETWORK_CALL_FAILED",
        "MODEL_UPDATED",
        "SPEECH_RENDERED",
        "EXECUTION_TIMEOUT",
        "EXECUTION_MEMORY_EXCEEDED",
        "EXECUTION_CPU_EXCEEDED",
        "COGNITIVE_ANALYSIS_STARTED",
        "COGNITIVE_ANALYSIS_COMPLETED",
    }
)
