from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from src.ledger.writer import LedgerWriter
from src.perception.ocr_pipeline import OCRPipeline
from src.perception.vision_analyzer import VisionAnalyzer


log = logging.getLogger("nova.live_screen")
LIVE_SCREEN_MAX_UPLOAD_BYTES = 12 * 1024 * 1024

ledger_writer = LedgerWriter()
ocr_pipeline = OCRPipeline()
vision_analyzer = VisionAnalyzer()


def build_live_screen_router() -> APIRouter:
    router = APIRouter(tags=["live_screen"])

    @router.post("/api/live-screen/analyze")
    async def analyze_live_screen_frame(
        image: UploadFile = File(...),
        query: str = Form(""),
        source_label: str = Form(""),
    ) -> dict[str, object]:
        image_bytes = await image.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="A shared screen frame is required.")
        if len(image_bytes) > LIVE_SCREEN_MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=400, detail="That shared frame is too large. Try sharing a smaller view.")

        suffix = Path(str(image.filename or "shared-screen.png")).suffix or ".png"
        temp_path = ""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(image_bytes)
                temp_path = temp_file.name

            hint = str(source_label or "").strip()
            context_snapshot = {
                "active_window": {"title": hint},
                "browser": {"page_title": hint},
            }
            ocr_text = ocr_pipeline.extract_text(temp_path)
            analysis = vision_analyzer.analyze(
                image_path=temp_path,
                ocr_text=ocr_text,
                context_snapshot=context_snapshot,
                working_context={"task_type": "analysis"},
                user_query=str(query or "").strip(),
            )
            summary = str(analysis.get("summary") or "Live screen help is ready.").strip()
            next_steps = [
                str(item).strip()
                for item in list(analysis.get("next_steps") or [])
                if str(item).strip()
            ]
            payload = {
                "summary": summary,
                "next_steps": next_steps[:4],
                "ocr_text": ocr_text,
                "analysis": analysis,
                "page_kind": str(analysis.get("page_kind") or "").strip(),
                "what_matters": str(analysis.get("what_matters") or "").strip(),
                "key_actions": list(analysis.get("key_actions") or [])[:4],
                "follow_up_prompts": [str(item).strip() for item in list(analysis.get("follow_up_prompts") or []) if str(item).strip()][:4],
                "source_label": hint,
                "analysis_available": True,
            }
            try:
                ledger_writer.log_event(
                    "LIVE_SCREEN_ANALYZED",
                    {
                        "success": True,
                        "source_label": hint,
                        "query": str(query or "").strip(),
                    },
                )
            except Exception:
                pass
            return payload
        except HTTPException:
            raise
        except Exception as exc:
            log.exception("Live screen analysis failed")
            try:
                ledger_writer.log_event(
                    "LIVE_SCREEN_ANALYZED",
                    {
                        "success": False,
                        "source_label": str(source_label or "").strip(),
                        "query": str(query or "").strip(),
                        "error": str(exc),
                    },
                )
            except Exception:
                pass
            raise HTTPException(
                status_code=500,
                detail="I couldn't analyze that shared screen frame.",
            ) from exc
        finally:
            if temp_path:
                try:
                    Path(temp_path).unlink(missing_ok=True)
                except Exception:
                    pass

    return router
