from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from src.actions.action_result import ActionResult
from src.conversation.deepseek_bridge import DeepSeekBridge
from src.conversation.deepseek_safety_wrapper import DeepSeekSafetyWrapper


class AnalysisDocumentExecutor:
    """Governed, session-scoped analysis document lifecycle."""

    _UNAVAILABLE_MARKERS = (
        "currently unavailable",
        "structured analysis",
        "model is blocked",
        "version mismatch",
    )
    _CREATE_TIMEOUT_SECONDS = 150.0

    def __init__(self) -> None:
        self._bridge = DeepSeekBridge()
        self._safety = DeepSeekSafetyWrapper()

    @staticmethod
    def _speakable_preview(text: str, *, limit: int = 220) -> str:
        clean = re.sub(r"\s+", " ", str(text or "").strip())
        if len(clean) <= limit:
            return clean
        return clean[: limit - 3].rstrip() + "..."

    @staticmethod
    def _failure_result(
        message: str,
        *,
        request_id: str,
        action: str,
        payload: dict[str, Any] | None = None,
    ) -> ActionResult:
        structured = dict(payload or {})
        structured.setdefault("document_action", action)
        structured.setdefault("document_available", False)
        return ActionResult.failure(
            message,
            data=structured,
            structured_data=structured,
            speakable_text=message,
            request_id=request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
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
            message=message,
            data=structured,
            structured_data=structured,
            speakable_text=speakable_text,
            request_id=request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    def execute(self, request) -> ActionResult:
        params = dict(request.params or {})
        action = str(params.get("action") or "create").strip().lower()
        documents = list(params.get("analysis_documents") or [])

        if action == "create":
            return self._create_document(request, params, documents)
        if action == "summarize_doc":
            return self._summarize_document(request, params, documents)
        if action == "explain_section":
            return self._explain_section(request, params, documents)
        if action == "list":
            return self._list_documents(request, documents)

        return self._failure_result(
            "Unsupported analysis document action.",
            request_id=request.request_id,
            action=action or "unknown",
        )

    def _create_document(self, request, params: dict[str, Any], documents: list[dict[str, Any]]) -> ActionResult:
        topic = str(params.get("topic") or "").strip()
        if not topic:
            return self._failure_result(
                "Please provide a topic for the analysis document.",
                request_id=request.request_id,
                action="create",
                payload={"topic": topic},
            )

        prompt = (
            "Create a structured long-form analysis document.\n"
            f"Topic: {topic}\n\n"
            "Return plain text only. Do not use markdown emphasis. Do not use blank lines anywhere in the response.\n"
            "Put each heading and its content on a single line.\n"
            "Format strictly as:\n"
            "Title: ...\n"
            "Executive Summary: ...\n"
            "Section 1 - ...: ...\n"
            "Section 2 - ...: ...\n"
            "Section 3 - ...: ...\n"
            "Key Risks: ...\n"
            "Key Signals To Watch: ...\n"
            "Keep tone neutral, factual, and non-predictive."
        )
        raw = self._bridge.analyze(
            prompt,
            [],
            suggested_max_tokens=500,
            analysis_profile="task_scoped",
            timeout_seconds=self._CREATE_TIMEOUT_SECONDS,
        )
        content = self._safety.sanitize(raw)
        if not content:
            return self._failure_result(
                "I couldn't generate the analysis document right now.",
                request_id=request.request_id,
                action="create",
                payload={"topic": topic},
            )
        if self._analysis_unavailable(content):
            return self._failure_result(
                "Analysis document generation is unavailable in this runtime because structured analysis is currently blocked or unavailable.",
                request_id=request.request_id,
                action="create",
                payload={"topic": topic, "failure_kind": "analysis_unavailable"},
            )
        if not self._looks_complete_document(content):
            return self._failure_result(
                "Analysis document generation returned an incomplete document, so I did not save it as a finished report.",
                request_id=request.request_id,
                action="create",
                payload={"topic": topic, "failure_kind": "incomplete_document"},
            )

        next_id = self._next_id(documents)
        sections = self._extract_sections(content)
        title = self._extract_title(content) or f"Analysis Document {next_id}: {topic}"
        summary = self._extract_summary(content)
        if not summary:
            summary = self._first_text_snippet(content, limit=260)

        doc = {
            "id": next_id,
            "title": title,
            "topic": topic,
            "content": content,
            "summary": summary,
            "sections": sections,
            "source_model": "deepseek_bridge",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        documents.append(doc)
        section_count = len(sections)

        message = (
            f"Analysis document created: Doc {next_id}\n"
            f"Title: {title}\n\n"
            f"Summary:\n{summary}\n\n"
            f"Sections detected: {section_count}\n\n"
            f"Try next:\n"
            f"- summarize doc {next_id}\n"
            f"- explain section 1 of doc {next_id}\n"
            f"- list analysis docs"
        )
        payload = {
            "analysis_documents": documents,
            "document_id": next_id,
            "document_title": title,
            "document_summary": summary,
            "section_count": section_count,
            "follow_up_prompts": [
                f"summarize doc {next_id}",
                f"explain section 1 of doc {next_id}",
                "list analysis docs",
            ],
        }
        return self._ok_result(
            message,
            request_id=request.request_id,
            payload=payload,
            speakable_text=(
                f"Analysis document created. Doc {next_id}: {title}. "
                f"{section_count} section{'s' if section_count != 1 else ''} detected."
            ),
        )

    def _summarize_document(self, request, params: dict[str, Any], documents: list[dict[str, Any]]) -> ActionResult:
        doc = self._resolve_doc(params, documents)
        if doc is None:
            return self._failure_result(
                "I couldn't find that document in this session.",
                request_id=request.request_id,
                action="summarize_doc",
                payload={"requested_doc_id": params.get("doc_id")},
            )

        sections = list(doc.get("sections") or [])
        section_titles = ", ".join(str(s.get("title") or f"Section {s.get('number')}") for s in sections[:5])
        message = (
            f"Document Summary - Doc {doc['id']}\n"
            f"Title: {doc.get('title', 'Untitled')}\n"
            f"Topic: {doc.get('topic', 'Unknown')}\n\n"
            f"{doc.get('summary', '')}\n\n"
            f"Sections: {section_titles or 'No structured sections found.'}\n\n"
            f"Try next:\n"
            f"- explain section 1 of doc {doc['id']}\n"
            f"- explain section 2 of doc {doc['id']}\n"
            f"- list analysis docs"
        )
        payload = {
            "analysis_documents": documents,
            "document_id": int(doc["id"]),
            "document_title": str(doc.get("title") or "Untitled"),
            "document_summary": str(doc.get("summary") or ""),
            "follow_up_prompts": [
                f"explain section 1 of doc {doc['id']}",
                f"explain section 2 of doc {doc['id']}",
                "list analysis docs",
            ],
        }
        return self._ok_result(
            message,
            request_id=request.request_id,
            payload=payload,
            speakable_text=(
                f"Document summary ready for doc {doc['id']}. "
                f"{self._speakable_preview(str(doc.get('summary') or ''), limit=160)}"
            ),
        )

    def _explain_section(self, request, params: dict[str, Any], documents: list[dict[str, Any]]) -> ActionResult:
        doc = self._resolve_doc(params, documents)
        if doc is None:
            return self._failure_result(
                "I couldn't find that document in this session.",
                request_id=request.request_id,
                action="explain_section",
                payload={"requested_doc_id": params.get("doc_id")},
            )

        try:
            section_number = int(params.get("section_number") or 0)
        except Exception:
            section_number = 0
        if section_number <= 0:
            return self._failure_result(
                "Please specify a valid section number.",
                request_id=request.request_id,
                action="explain_section",
                payload={"document_id": int(doc["id"]), "section_number": section_number},
            )

        sections = list(doc.get("sections") or [])
        section = next((s for s in sections if int(s.get("number") or -1) == section_number), None)
        if section is None:
            return self._failure_result(
                f"Section {section_number} is not available in doc {doc['id']}.",
                request_id=request.request_id,
                action="explain_section",
                payload={"document_id": int(doc["id"]), "section_number": section_number},
            )

        section_text = str(section.get("content") or "").strip()
        if not section_text:
            return self._failure_result(
                "That section has no content to explain.",
                request_id=request.request_id,
                action="explain_section",
                payload={"document_id": int(doc["id"]), "section_number": section_number},
            )

        prompt = (
            "Explain this section in clear, practical language.\n\n"
            f"Section title: {section.get('title', f'Section {section_number}')}\n"
            f"Section text:\n{section_text}\n\n"
            "Return:\n- Main point\n- Why it matters\n- Key detail to remember"
        )
        raw = self._bridge.analyze(
            prompt,
            [],
            suggested_max_tokens=450,
            analysis_profile="task_scoped",
        )
        explained = self._safety.sanitize(raw)
        if not explained or self._analysis_unavailable(explained):
            explained = self._first_text_snippet(section_text, limit=420)

        message = (
            f"Section Explanation - Doc {doc['id']} Section {section_number}\n"
            f"Title: {section.get('title', f'Section {section_number}')}\n\n"
            f"{explained}\n\n"
            f"Try next:\n"
            f"- summarize doc {doc['id']}\n"
            f"- explain section {section_number + 1} of doc {doc['id']}\n"
            f"- list analysis docs"
        )
        payload = {
            "analysis_documents": documents,
            "document_id": int(doc["id"]),
            "section_number": section_number,
            "section_title": str(section.get("title") or f"Section {section_number}"),
            "follow_up_prompts": [
                f"summarize doc {doc['id']}",
                f"explain section {section_number + 1} of doc {doc['id']}",
                "list analysis docs",
            ],
        }
        return self._ok_result(
            message,
            request_id=request.request_id,
            payload=payload,
            speakable_text=(
                f"Section explanation ready for doc {doc['id']} section {section_number}. "
                f"{self._speakable_preview(explained, limit=170)}"
            ),
        )

    def _list_documents(self, request, documents: list[dict[str, Any]]) -> ActionResult:
        if not documents:
            return self._failure_result(
                "No analysis documents are available in this session.",
                request_id=request.request_id,
                action="list",
            )

        lines = [f"Analysis Documents ({len(documents)})"]
        for item in sorted(documents, key=lambda d: int(d.get("id", 0))):
            summary = self._first_text_snippet(str(item.get("summary") or ""), limit=80)
            topic = str(item.get("topic") or "").strip()
            meta_parts = [part for part in [topic, summary] if part]
            suffix = f" | {' | '.join(meta_parts)}" if meta_parts else ""
            lines.append(f"- Doc {item.get('id')}: {item.get('title', 'Untitled')}{suffix}")
        lines.extend(["", "Try next: summarize doc 1, explain section 1 of doc 1."])
        payload = {
            "analysis_documents": documents,
            "document_count": len(documents),
            "follow_up_prompts": [
                "summarize doc 1",
                "explain section 1 of doc 1",
            ],
        }
        return self._ok_result(
            "\n".join(lines),
            request_id=request.request_id,
            payload=payload,
            speakable_text=f"Analysis document list ready. {len(documents)} document{'s' if len(documents) != 1 else ''} available.",
        )

    @staticmethod
    def _next_id(documents: list[dict[str, Any]]) -> int:
        existing = [int(doc.get("id") or 0) for doc in documents]
        return (max(existing) + 1) if existing else 1

    @staticmethod
    def _resolve_doc(params: dict[str, Any], documents: list[dict[str, Any]]) -> dict[str, Any] | None:
        if not documents:
            return None
        raw_id = params.get("doc_id")
        if raw_id in (None, ""):
            return sorted(documents, key=lambda d: int(d.get("id", 0)))[-1]
        try:
            doc_id = int(raw_id)
        except Exception:
            return None
        return next((d for d in documents if int(d.get("id") or -1) == doc_id), None)

    @staticmethod
    def _extract_title(text: str) -> str:
        for line in text.splitlines():
            stripped = line.strip()
            stripped = re.sub(r"^\*+\s*", "", stripped)
            stripped = re.sub(r"\s*\*+$", "", stripped)
            if stripped.lower().startswith("title:"):
                return stripped.split(":", 1)[1].strip()
        return ""

    @staticmethod
    def _extract_summary(text: str) -> str:
        for line in text.splitlines():
            stripped = line.strip()
            stripped = re.sub(r"^\*+\s*", "", stripped)
            stripped = re.sub(r"\s*\*+$", "", stripped)
            if stripped.lower().startswith("executive summary:"):
                return stripped.split(":", 1)[1].strip()
        return ""

    @staticmethod
    def _first_text_snippet(text: str, limit: int = 240) -> str:
        clean = re.sub(r"\s+", " ", text).strip()
        if len(clean) <= limit:
            return clean
        return clean[: limit - 3].rstrip() + "..."

    @staticmethod
    def _extract_sections(text: str) -> list[dict[str, Any]]:
        lines = text.splitlines()
        sections: list[dict[str, Any]] = []
        current_title = ""
        current_number = 0
        current_buffer: list[str] = []

        def flush() -> None:
            nonlocal current_number, current_title, current_buffer
            if current_number <= 0:
                return
            content = "\n".join(current_buffer).strip()
            sections.append(
                {
                    "number": current_number,
                    "title": current_title or f"Section {current_number}",
                    "content": content,
                }
            )
            current_buffer = []

        for line in lines:
            stripped = line.strip()
            inline_match = re.match(
                r"^section\s+(\d+)\s*-\s*([^:]+?)\s*:\s*(.+)$",
                stripped,
                flags=re.IGNORECASE,
            )
            if inline_match:
                flush()
                sections.append(
                    {
                        "number": int(inline_match.group(1)),
                        "title": inline_match.group(2).strip(),
                        "content": inline_match.group(3).strip(),
                    }
                )
                current_number = 0
                current_title = ""
                current_buffer = []
                continue

            match = re.match(r"^section\s+(\d+)\s*[-:]\s*(.+)$", stripped, flags=re.IGNORECASE)
            if match:
                flush()
                current_number = int(match.group(1))
                current_title = match.group(2).strip()
                continue
            if current_number > 0:
                current_buffer.append(line)

        flush()
        if not sections:
            sections.append({"number": 1, "title": "Overview", "content": text.strip()})
        return sections

    @classmethod
    def _looks_complete_document(cls, text: str) -> bool:
        title = cls._extract_title(text)
        summary = cls._extract_summary(text)
        sections = cls._extract_sections(text)
        lowered = str(text or "").lower()
        has_key_risks = "key risks:" in lowered
        has_key_signals = "key signals to watch:" in lowered
        return bool(title and summary and len(sections) >= 3 and has_key_risks and has_key_signals)

    @classmethod
    def _analysis_unavailable(cls, text: str) -> bool:
        lowered = str(text or "").strip().lower()
        if not lowered:
            return True
        return any(marker in lowered for marker in cls._UNAVAILABLE_MARKERS)
