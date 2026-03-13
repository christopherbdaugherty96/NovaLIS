from __future__ import annotations

from typing import Any

from src.actions.action_result import ActionResult
from src.executors.screen_capture_executor import ScreenCaptureExecutor
from src.ledger.writer import LedgerWriter
from src.perception.ocr_pipeline import OCRPipeline
from src.perception.vision_analyzer import VisionAnalyzer


class ScreenAnalysisExecutor:
    """Governed OCR + visual explanation after explicit capture invocation."""

    def __init__(
        self,
        *,
        ledger: LedgerWriter | None = None,
        capture_executor: ScreenCaptureExecutor | None = None,
        ocr_pipeline: OCRPipeline | None = None,
        vision_analyzer: VisionAnalyzer | None = None,
    ) -> None:
        self.ledger = ledger or LedgerWriter()
        self.capture_executor = capture_executor or ScreenCaptureExecutor(ledger=self.ledger)
        self.ocr_pipeline = ocr_pipeline or OCRPipeline()
        self.vision_analyzer = vision_analyzer or VisionAnalyzer()

    def execute(self, request) -> ActionResult:
        try:
            request_params = dict(request.params or {})
            working_context = request_params.get("working_context")
            capture_result = self.capture_executor.execute(request)
            if not capture_result.success:
                self._safe_log(
                    "SCREEN_ANALYSIS_COMPLETED",
                    {"request_id": request.request_id, "success": False, "error": capture_result.message},
                )
                return capture_result

            payload = dict(capture_result.data or {})
            capture = dict(payload.get("capture") or {})
            image_path = str(capture.get("image_path") or "")
            ocr_text = self.ocr_pipeline.extract_text(image_path)
            analysis = self.vision_analyzer.analyze(
                image_path=image_path,
                ocr_text=ocr_text,
                context_snapshot=payload.get("context_snapshot"),
                working_context=working_context if isinstance(working_context, dict) else None,
                user_query=str(request_params.get("query") or ""),
            )
            base_summary = str(analysis.get("summary") or "Screen analysis completed.").strip()
            summary_lines = ["What I found", base_summary]
            next_steps = [str(item).strip() for item in list(analysis.get("next_steps") or []) if str(item).strip()]
            if ocr_text.strip():
                summary_lines.extend(["", "Readable text detected", self._preview_text(ocr_text)])
            else:
                summary_lines.extend(["", "Readable text detected", "No substantial OCR text was extracted from this capture."])
            if next_steps:
                summary_lines.extend(["", "Suggested next steps:"])
                summary_lines.extend([f"- {item}" for item in next_steps[:4]])
            summary = "\n".join(summary_lines)
            self._safe_log(
                "SCREEN_ANALYSIS_COMPLETED",
                {"request_id": request.request_id, "success": True, "image_path": image_path},
            )

            merged_data = dict(payload)
            merged_data["ocr_text"] = ocr_text
            merged_data["analysis"] = analysis
            merged_data["working_context_delta"] = self._build_working_context_delta(
                context_snapshot=payload.get("context_snapshot"),
                analysis=analysis,
                user_query=str(request_params.get("query") or ""),
            )
            merged_data["widget"] = {
                "type": "screen_analysis",
                "data": {
                    "summary": summary,
                    "ocr_text": ocr_text,
                    "capture": capture,
                    "next_steps": next_steps,
                    "follow_up_prompts": next_steps[:4] or ["explain this", "what does this mean"],
                },
            }

            return ActionResult.ok(
                message=summary,
                data=merged_data,
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
            )
        except Exception as error:
            self._safe_log(
                "SCREEN_ANALYSIS_COMPLETED",
                {"request_id": request.request_id, "success": False, "error": str(error)},
            )
            return ActionResult.failure(
                "I could not analyze the captured screen region.",
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
    def _build_working_context_delta(
        *,
        context_snapshot: Any,
        analysis: dict[str, Any],
        user_query: str,
    ) -> dict[str, Any]:
        snapshot = dict(context_snapshot or {})
        active_window = dict(snapshot.get("active_window") or {})
        browser = dict(snapshot.get("browser") or {})
        signals = dict(analysis.get("signals") or {})
        diagnostic = str(signals.get("diagnostic") or "").strip().lower()
        browser_active = bool(browser.get("is_browser"))
        inferred_task = "research" if browser_active else "analysis"
        if diagnostic == "python_download_guidance":
            inferred_task = "software_install"
        elif diagnostic in {"module_not_found", "key_error"}:
            inferred_task = "error_debugging"
        delta: dict[str, Any] = {
            "task_type": inferred_task,
            "active_app": str(active_window.get("app") or "").strip(),
            "active_window": str(active_window.get("title") or "").strip(),
            "active_url": str(signals.get("active_url") or browser.get("url") or "").strip(),
            "cursor_target": str(signals.get("page_title") or signals.get("ocr_snippet") or "").strip(),
            "last_relevant_object": str(signals.get("page_title") or "screen_region").strip(),
            "current_step": "analysis",
        }
        recommended_download = str(signals.get("recommended_download") or "").strip()
        if recommended_download:
            delta["last_relevant_object"] = recommended_download
            delta["current_step"] = "selection"
        query = str(user_query or "").strip()
        if query:
            delta["task_goal"] = query
            delta["recent_relevant_turns"] = [query]
        return delta

    @staticmethod
    def _preview_text(text: str, limit: int = 240) -> str:
        compact = " ".join(str(text or "").split()).strip()
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3].rstrip() + "..."
