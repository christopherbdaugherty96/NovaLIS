from __future__ import annotations

import logging
from time import perf_counter
from typing import Any

from src.ledger.writer import LedgerWriter


logger = logging.getLogger(__name__)


class CognitiveOperationLogger:
    """Best-effort observability for analysis-only cognitive operations."""

    def __init__(self, ledger_writer: LedgerWriter | None = None) -> None:
        self._ledger = ledger_writer or LedgerWriter()

    def started(self, *, module_name: str, mode: str, request_id: str = "") -> float:
        started_at = perf_counter()
        self._log_safe(
            "COGNITIVE_ANALYSIS_STARTED",
            {
                "module": module_name,
                "mode": mode,
                "request_id": request_id,
            },
        )
        return started_at

    def completed(
        self,
        *,
        module_name: str,
        mode: str,
        started_at: float,
        request_id: str = "",
        success: bool,
        confidence: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        payload: dict[str, Any] = {
            "module": module_name,
            "mode": mode,
            "request_id": request_id,
            "success": bool(success),
            "duration_ms": int(max(0, (perf_counter() - started_at) * 1000)),
        }
        if confidence is not None:
            payload["confidence"] = float(confidence)
        if metadata:
            payload.update(metadata)
        self._log_safe("COGNITIVE_ANALYSIS_COMPLETED", payload)

    def _log_safe(self, event_type: str, metadata: dict[str, Any]) -> None:
        try:
            self._ledger.log_event(event_type, metadata)
        except Exception as exc:  # pragma: no cover - best-effort only
            logger.debug("Cognitive operation ledger logging failed: %s", exc)
