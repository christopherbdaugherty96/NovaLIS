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
                user_query=str((request.params or {}).get("query") or ""),
            )
            summary = str(analysis.get("summary") or "Screen analysis completed.").strip()
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
                user_query=str((request.params or {}).get("query") or ""),
            )
            merged_data["widget"] = {
                "type": "screen_analysis",
                "data": {
                    "summary": summary,
                    "ocr_text": ocr_text,
                    "capture": capture,
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
        browser_active = bool(browser.get("is_browser"))
        delta: dict[str, Any] = {
            "task_type": "research" if browser_active else "analysis",
            "active_app": str(active_window.get("app") or "").strip(),
            "active_window": str(active_window.get("title") or "").strip(),
            "active_url": str(browser.get("url") or "").strip(),
            "cursor_target": str(signals.get("page_title") or signals.get("ocr_snippet") or "").strip(),
            "last_relevant_object": str(signals.get("page_title") or "screen_region").strip(),
            "current_step": "analysis",
        }
        query = str(user_query or "").strip()
        if query:
            delta["task_goal"] = query
            delta["recent_relevant_turns"] = [query]
        return delta
