from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

from src.context.active_window import get_active_window
from src.context.browser_context import get_browser_context
from src.context.system_context import get_system_context
from src.ledger.writer import LedgerWriter
from src.perception.cursor_locator import locate_cursor


ActiveWindowProvider = Callable[[], dict[str, Any]]
BrowserContextProvider = Callable[[dict[str, Any]], dict[str, Any]]
SystemContextProvider = Callable[[], dict[str, Any]]
CursorProvider = Callable[[], dict[str, Any]]


@dataclass(frozen=True)
class ContextSnapshot:
    request_id: str
    invocation_source: str
    captured_at: str
    active_window: dict[str, Any]
    browser: dict[str, Any]
    system: dict[str, Any]
    cursor: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "invocation_source": self.invocation_source,
            "captured_at": self.captured_at,
            "active_window": dict(self.active_window),
            "browser": dict(self.browser),
            "system": dict(self.system),
            "cursor": dict(self.cursor),
        }


class ContextSnapshotService:
    """Collects read-only environment signals for invocation-time analysis."""

    ALLOWED_INVOCATION_SOURCES = frozenset({"ui", "voice", "text"})

    def __init__(
        self,
        *,
        active_window_provider: ActiveWindowProvider | None = None,
        browser_context_provider: BrowserContextProvider | None = None,
        system_context_provider: SystemContextProvider | None = None,
        cursor_provider: CursorProvider | None = None,
        ledger: LedgerWriter | None = None,
    ) -> None:
        self._active_window_provider = active_window_provider or get_active_window
        self._browser_context_provider = browser_context_provider or get_browser_context
        self._system_context_provider = system_context_provider or get_system_context
        self._cursor_provider = cursor_provider or locate_cursor
        self._ledger = ledger

    def capture_snapshot(self, *, request_id: str, invocation_source: str) -> dict[str, Any]:
        source = str(invocation_source or "").strip().lower()
        if source not in self.ALLOWED_INVOCATION_SOURCES:
            raise ValueError("Context snapshot requires explicit invocation source.")

        self._safe_log(
            "CONTEXT_SNAPSHOT_REQUESTED",
            {
                "request_id": request_id,
                "invocation_source": source,
            },
        )

        try:
            active_window = dict(self._active_window_provider() or {})
            browser = dict(self._browser_context_provider(active_window) or {})
            system = dict(self._system_context_provider() or {})
            cursor = dict(self._cursor_provider() or {})

            snapshot = ContextSnapshot(
                request_id=request_id,
                invocation_source=source,
                captured_at=datetime.now(timezone.utc).isoformat(),
                active_window=active_window,
                browser=browser,
                system=system,
                cursor=cursor,
            )
            self._safe_log(
                "CONTEXT_SNAPSHOT_COMPLETED",
                {
                    "request_id": request_id,
                    "invocation_source": source,
                    "success": True,
                },
            )
            return snapshot.to_dict()
        except Exception as error:
            self._safe_log(
                "CONTEXT_SNAPSHOT_COMPLETED",
                {
                    "request_id": request_id,
                    "invocation_source": source,
                    "success": False,
                    "error": str(error),
                },
            )
            raise

    def _safe_log(self, event_type: str, payload: dict[str, Any]) -> None:
        if self._ledger is None:
            return
        try:
            self._ledger.log_event(event_type, payload)
        except Exception:
            return
