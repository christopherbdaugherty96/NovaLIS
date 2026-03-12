from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from src.actions.action_result import ActionResult
from src.context.context_snapshot_service import ContextSnapshotService
from src.executors.screen_analysis_executor import ScreenAnalysisExecutor
from src.ledger.writer import LedgerWriter
from src.perception.explain_anything import ExplainAnythingRouter


class ExplainAnythingExecutor:
    """
    Universal context explainer.

    Invocation-bound only:
    - uses explicit invocation source (voice/ui/text)
    - routes to read-only file explanation or screen analysis
    - does not perform autonomous actions
    """

    ALLOWED_INVOCATION_SOURCES = frozenset({"ui", "voice", "text"})
    MAX_FILE_CHARS = 120_000

    def __init__(
        self,
        *,
        ledger: LedgerWriter | None = None,
        context_service: ContextSnapshotService | None = None,
        screen_analysis_executor: ScreenAnalysisExecutor | None = None,
        router: ExplainAnythingRouter | None = None,
    ) -> None:
        self.ledger = ledger or LedgerWriter()
        self.context_service = context_service or ContextSnapshotService(ledger=self.ledger)
        self.screen_analysis_executor = screen_analysis_executor or ScreenAnalysisExecutor(ledger=self.ledger)
        self.router = router or ExplainAnythingRouter()

    def execute(self, request) -> ActionResult:
        params = dict(request.params or {})
        invocation_source = str(params.get("invocation_source") or "").strip().lower()
        query_text = str(params.get("query") or "").strip()
        working_context = dict(params.get("working_context") or {})
        if not query_text:
            query_text = str(working_context.get("task_goal") or working_context.get("last_relevant_object") or "").strip()
        self._safe_log(
            "EXPLAIN_ANYTHING_REQUESTED",
            {
                "request_id": request.request_id,
                "invocation_source": invocation_source or "unknown",
                "query": query_text,
            },
        )
        if invocation_source not in self.ALLOWED_INVOCATION_SOURCES:
            result = ActionResult.failure(
                "Explain mode requires explicit invocation source (voice, ui, or text).",
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
            self._safe_log(
                "EXPLAIN_ANYTHING_COMPLETED",
                {
                    "request_id": request.request_id,
                    "success": False,
                    "route": "invalid_invocation_source",
                },
            )
            return result

        try:
            context_snapshot = self.context_service.capture_snapshot(
                request_id=request.request_id,
                invocation_source=invocation_source,
            )
        except Exception:
            context_snapshot = {}

        route = self.router.decide(params=params, context_snapshot=context_snapshot)
        if route.kind == "file":
            result = self._explain_file(request, route.file_path, context_snapshot)
            self._safe_log(
                "EXPLAIN_ANYTHING_COMPLETED",
                {
                    "request_id": request.request_id,
                    "success": bool(result.success),
                    "route": "file",
                },
            )
            return result

        if route.kind in {"screen", "webpage"}:
            downstream_params = dict(params)
            downstream_params.setdefault("invocation_source", invocation_source)
            if query_text:
                downstream_params["query"] = query_text
            downstream_params["context_snapshot"] = context_snapshot
            if isinstance(params.get("working_context"), dict):
                downstream_params["working_context"] = dict(params.get("working_context") or {})
            delegated = SimpleNamespace(params=downstream_params, request_id=request.request_id)
            result = self.screen_analysis_executor.execute(delegated)
            self._safe_log(
                "EXPLAIN_ANYTHING_COMPLETED",
                {
                    "request_id": request.request_id,
                    "success": bool(result.success),
                    "route": route.kind,
                },
            )
            return result

        result = ActionResult.failure(
            self.router.clarification_message(),
            data={"context_snapshot": context_snapshot},
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )
        self._safe_log(
            "EXPLAIN_ANYTHING_COMPLETED",
            {
                "request_id": request.request_id,
                "success": False,
                "route": "clarify",
            },
        )
        return result

    def _explain_file(self, request, file_path_text: str, context_snapshot: dict[str, Any]) -> ActionResult:
        path = Path(file_path_text).expanduser()
        if not path.exists() or not path.is_file():
            return ActionResult.failure(
                "I could not find that file to explain.",
                data={"context_snapshot": context_snapshot},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )

        if not self.router.is_supported_file(str(path)):
            return ActionResult.failure(
                "That file type is not supported yet. Try a text-based file.",
                data={"context_snapshot": context_snapshot, "file_path": str(path)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )

        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                content = handle.read(self.MAX_FILE_CHARS + 1)
        except Exception:
            return ActionResult.failure(
                "I could not read that file.",
                data={"context_snapshot": context_snapshot, "file_path": str(path)},
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )

        was_truncated = len(content) > self.MAX_FILE_CHARS
        if was_truncated:
            content = content[: self.MAX_FILE_CHARS]
        summary = self._summarize_file_content(content)
        if was_truncated:
            summary = f"{summary} (I summarized the first {self.MAX_FILE_CHARS} characters.)"
        message = f"File explanation for {path.name}\n\n{summary}"
        working_context_delta = {
            "task_type": "document_review" if path.suffix.lower() in {".txt", ".md", ".pdf", ".log"} else "code_analysis",
            "selected_file": str(path),
            "last_relevant_object": path.name,
            "current_step": "analysis",
        }
        return ActionResult.ok(
            message=message,
            data={
                "context_snapshot": context_snapshot,
                "analysis": {
                    "type": "file",
                    "file_path": str(path),
                    "summary": summary,
                },
                "widget": {
                    "type": "file_explanation",
                    "data": {"file_path": str(path), "summary": summary},
                },
                "working_context_delta": working_context_delta,
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def _safe_log(self, event_type: str, payload: dict[str, Any]) -> None:
        try:
            self.ledger.log_event(event_type, payload)
        except Exception:
            return

    @staticmethod
    def _summarize_file_content(content: str) -> str:
        text = str(content or "")
        compact = re.sub(r"\s+", " ", text).strip()
        if not compact:
            return "The file is empty."

        module_error = re.search(r"ModuleNotFoundError:\s+No module named ['\"]([^'\"]+)['\"]", text)
        if module_error:
            package_name = module_error.group(1).strip()
            return (
                f"This looks like a Python import error: module '{package_name}' is missing. "
                f"A typical fix is installing it with 'pip install {package_name}'."
            )

        key_error = re.search(r"KeyError:\s*['\"]?([^'\"\n]+)", text)
        if key_error:
            key_name = key_error.group(1).strip()
            return (
                f"This appears to be a KeyError for '{key_name}', meaning a dictionary key was requested "
                "but not present."
            )

        preview = compact[:260]
        if len(compact) > 260:
            preview += "..."
        return f"Here is the main content signal: {preview}"
