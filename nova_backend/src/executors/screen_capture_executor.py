from __future__ import annotations

from typing import Any

from src.actions.action_result import ActionResult
from src.context.context_snapshot_service import ContextSnapshotService
from src.ledger.writer import LedgerWriter
from src.perception.cursor_locator import build_cursor_region
from src.perception.screen_capture import ScreenCaptureEngine


class ScreenCaptureExecutor:
    """Governed capture of an invocation-time on-screen region."""

    ALLOWED_INVOCATION_SOURCES = frozenset({"ui", "voice", "text"})

    def __init__(
        self,
        *,
        ledger: LedgerWriter | None = None,
        context_service: ContextSnapshotService | None = None,
        capture_engine: ScreenCaptureEngine | None = None,
    ) -> None:
        self.ledger = ledger or LedgerWriter()
        self.context_service = context_service or ContextSnapshotService(ledger=self.ledger)
        self.capture_engine = capture_engine or ScreenCaptureEngine()

    @staticmethod
    def _failure_result(
        message: str,
        *,
        request_id: str,
        failure_kind: str,
        payload: dict[str, Any] | None = None,
    ) -> ActionResult:
        structured = dict(payload or {})
        structured.setdefault("capture_available", False)
        structured.setdefault("capture_failure_kind", failure_kind)
        return ActionResult.failure(
            message,
            data=structured,
            structured_data=structured,
            speakable_text=message,
            request_id=request_id,
            authority_class="persistent_change",
            external_effect=False,
            reversible=False,
            outcome_reason=message,
        )

    @staticmethod
    def _ok_result(
        message: str,
        *,
        request_id: str,
        payload: dict[str, Any],
        speakable_text: str,
    ) -> ActionResult:
        structured = dict(payload)
        return ActionResult.ok(
            message,
            data=structured,
            structured_data=structured,
            speakable_text=speakable_text,
            request_id=request_id,
            authority_class="persistent_change",
            external_effect=False,
            reversible=False,
        )

    def execute(self, request) -> ActionResult:
        params = dict(request.params or {})
        invocation_source = str(params.get("invocation_source") or "").strip().lower()
        if invocation_source not in self.ALLOWED_INVOCATION_SOURCES:
            return self._failure_result(
                "Screen capture requires explicit invocation source (voice, ui, or text).",
                request_id=request.request_id,
                failure_kind="invalid_invocation_source",
                payload={"invocation_source": invocation_source or "unknown"},
            )

        region_size = self._parse_region_size(params.get("region_size"), default=800)
        self._safe_log(
            "SCREEN_CAPTURE_REQUESTED",
            {
                "request_id": request.request_id,
                "invocation_source": invocation_source,
                "region_size": region_size,
            },
        )

        provided_snapshot = params.get("context_snapshot")
        if isinstance(provided_snapshot, dict):
            snapshot = dict(provided_snapshot)
        else:
            try:
                snapshot = self.context_service.capture_snapshot(
                    request_id=request.request_id,
                    invocation_source=invocation_source,
                )
            except Exception as error:
                self._safe_log(
                    "SCREEN_CAPTURE_COMPLETED",
                    {
                        "request_id": request.request_id,
                        "success": False,
                        "error": str(error),
                    },
                )
                return self._failure_result(
                    "I could not collect context for screen capture.",
                    request_id=request.request_id,
                    failure_kind="context_unavailable",
                )

        cursor = dict(snapshot.get("cursor") or {})
        bounds = build_cursor_region(cursor, size=region_size)
        capture = self.capture_engine.capture_region(bounds)
        if not bool(capture.get("ok")):
            raw_error = str(capture.get("error") or "Screen capture failed.")
            failure_kind = str(capture.get("failure_kind") or "").strip().lower()
            missing_dependency = str(capture.get("missing_dependency") or "").strip()
            message = self._render_capture_failure_message(
                raw_error,
                failure_kind=failure_kind,
                missing_dependency=missing_dependency,
            )
            failure_data = {
                "context_snapshot": snapshot,
                "capture_error": raw_error,
                "capture_bounds": dict(bounds),
            }
            if failure_kind:
                failure_data["capture_failure_kind"] = failure_kind
            if missing_dependency:
                failure_data["missing_dependency"] = missing_dependency
            self._safe_log(
                "SCREEN_CAPTURE_COMPLETED",
                {
                    "request_id": request.request_id,
                    "success": False,
                    "error": raw_error,
                    "failure_kind": failure_kind,
                    "missing_dependency": missing_dependency or None,
                },
            )
            return self._failure_result(
                message,
                request_id=request.request_id,
                failure_kind=failure_kind or "capture_failed",
                payload=failure_data,
            )

        image_path = str(capture.get("image_path") or "")
        active_window = dict(snapshot.get("active_window") or {})
        window_title = str(active_window.get("title") or "").strip()
        window_app = str(active_window.get("app") or "").strip()
        context_line = window_title or window_app
        self._safe_log(
            "SCREEN_CAPTURE_COMPLETED",
            {
                "request_id": request.request_id,
                "success": True,
                "image_path": image_path,
                "bounds": dict(capture.get("bounds") or bounds),
            },
        )
        payload = {
            "context_snapshot": snapshot,
            "working_context_delta": self._build_working_context_delta(snapshot),
            "capture": {
                "image_path": image_path,
                "bounds": dict(capture.get("bounds") or bounds),
            },
            "widget": {
                "type": "screen_capture",
                "data": {
                    "image_path": image_path,
                    "bounds": dict(capture.get("bounds") or bounds),
                    "follow_up_prompts": ["analyze this screen", "explain this"],
                },
            },
        }
        return self._ok_result(
            (
                "Captured the screen region around your cursor."
                + (f" Active context: {context_line}." if context_line else "")
                + "\nTry next: analyze this screen or explain this."
            ),
            request_id=request.request_id,
            payload=payload,
            speakable_text=(
                "Screen region captured."
                + (f" Active context {context_line}." if context_line else "")
            ),
        )

    @staticmethod
    def _parse_region_size(value: Any, *, default: int) -> int:
        try:
            parsed = int(value)
        except Exception:
            parsed = default
        return max(128, min(parsed, 1600))

    def _safe_log(self, event_type: str, payload: dict[str, Any]) -> None:
        try:
            self.ledger.log_event(event_type, payload)
        except Exception:
            return

    @staticmethod
    def _render_capture_failure_message(
        raw_error: str,
        *,
        failure_kind: str,
        missing_dependency: str,
    ) -> str:
        if failure_kind == "missing_dependency":
            dependency = missing_dependency or "required local capture dependency"
            return (
                f"Screen capture is unavailable in this runtime because the required dependency "
                f"'{dependency}' is missing. Install it, then try again."
            )
        if failure_kind == "dependency_unavailable":
            return (
                "Screen capture is unavailable in this runtime because the local capture dependency "
                "could not be loaded."
            )
        if failure_kind == "invalid_bounds":
            return (
                "Screen capture is unavailable because this runtime could not read valid screen bounds "
                "for the current cursor region."
            )
        if raw_error:
            return f"Screen capture is unavailable right now. {raw_error}"
        return "Screen capture is unavailable right now."

    @staticmethod
    def _build_working_context_delta(snapshot: dict[str, Any]) -> dict[str, Any]:
        active_window = dict(snapshot.get("active_window") or {})
        browser = dict(snapshot.get("browser") or {})
        return {
            "active_app": str(active_window.get("app") or "").strip(),
            "active_window": str(active_window.get("title") or "").strip(),
            "active_url": str(browser.get("url") or "").strip(),
            "current_step": "capture",
        }
