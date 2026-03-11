from __future__ import annotations

from typing import Any

from src.ledger.writer import LedgerWriter
from src.working_context.context_builder import WorkingContextBuilder
from src.working_context.context_router import WorkingContextRouter
from src.working_context.context_state import WorkingContextState


class WorkingContextStore:
    """Mutable session-scoped context store for one active session."""

    def __init__(
        self,
        *,
        session_id: str,
        ledger: LedgerWriter | None = None,
    ) -> None:
        self.session_id = str(session_id or "")
        self._builder = WorkingContextBuilder()
        self._router = WorkingContextRouter()
        self._ledger = ledger
        self._state = WorkingContextState().to_dict()
        self._safe_log("WORKING_CONTEXT_CREATED", {"session_id": self.session_id})

    def to_dict(self) -> dict[str, Any]:
        return dict(self._state)

    def for_explain(self) -> dict[str, Any]:
        slice_payload = self._router.for_explain(self._state)
        self._safe_log(
            "WORKING_CONTEXT_CONSUMED",
            {"session_id": self.session_id, "consumer": "explain"},
        )
        return slice_payload

    def followup_target(self) -> str:
        return self._router.followup_target(self._state)

    def apply_user_turn(self, *, text: str, channel: str, intent_family: str = "") -> None:
        updated, fields, changed = self._builder.update_for_user_turn(
            self._state,
            text=text,
            channel=channel,
            intent_family=intent_family,
        )
        self._state = updated
        if changed:
            self._safe_log(
                "WORKING_CONTEXT_UPDATED",
                {
                    "session_id": self.session_id,
                    "source": "user_turn",
                    "fields_updated": fields,
                },
            )

    def apply_snapshot(self, snapshot: dict[str, Any] | None) -> None:
        updated, fields, changed = self._builder.update_from_snapshot(
            self._state,
            snapshot=snapshot,
        )
        self._state = updated
        if changed:
            self._safe_log(
                "WORKING_CONTEXT_UPDATED",
                {
                    "session_id": self.session_id,
                    "source": "context_snapshot",
                    "fields_updated": fields,
                },
            )

    def apply_patch(self, patch: dict[str, Any] | None, *, source: str) -> None:
        updated, fields, changed = self._builder.apply_patch(self._state, patch=patch)
        self._state = updated
        if changed:
            self._safe_log(
                "WORKING_CONTEXT_UPDATED",
                {
                    "session_id": self.session_id,
                    "source": source,
                    "fields_updated": fields,
                },
            )

    def set_selected_file(self, file_path: str) -> None:
        value = str(file_path or "").strip()
        if not value:
            return
        self.apply_patch(
            {
                "selected_file": value,
                "last_relevant_object": value,
                "current_step": "selection",
            },
            source="selected_file",
        )

    def set_open_report_id(self, report_id: Any) -> None:
        value = str(report_id or "").strip()
        if not value:
            return
        self.apply_patch({"open_report_id": value}, source="report")

    def _safe_log(self, event_type: str, payload: dict[str, Any]) -> None:
        if self._ledger is None:
            return
        try:
            self._ledger.log_event(event_type, payload)
        except Exception:
            return
