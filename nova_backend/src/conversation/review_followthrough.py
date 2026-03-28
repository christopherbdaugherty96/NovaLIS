from __future__ import annotations

from typing import Any, Mapping
from uuid import uuid4

from src.conversation.response_formatter import ResponseFormatter
from src.llm.llm_gateway import generate_chat


def build_review_followthrough_snapshot(
    *,
    payload: Mapping[str, Any] | None,
    source_answer: str = "",
    source_prompt: str = "",
) -> dict[str, Any]:
    review_payload = dict(payload or {})
    review_kind = str(
        review_payload.get("reasoning_mode")
        or review_payload.get("verification_mode")
        or "verification"
    ).strip().lower() or "verification"
    return {
        "review_kind": review_kind,
        "source_answer": str(source_answer or "").strip(),
        "source_prompt": str(source_prompt or "").strip(),
        "summary_line": str(
            review_payload.get("reasoning_summary_line")
            or review_payload.get("verification_summary_line")
            or ""
        ).strip(),
        "top_issue": str(review_payload.get("top_issue") or "").strip(),
        "top_correction": str(review_payload.get("top_correction") or "").strip(),
        "review_text": str(
            review_payload.get("reasoning_text")
            or review_payload.get("verification_text")
            or ""
        ).strip(),
        "accuracy_label": str(
            review_payload.get("reasoning_accuracy_label")
            or review_payload.get("verification_accuracy_label")
            or ""
        ).strip(),
        "confidence_label": str(
            review_payload.get("reasoning_confidence_label")
            or review_payload.get("verification_confidence_label")
            or ""
        ).strip(),
        "recommended": bool(
            review_payload.get("reasoning_recommended")
            if "reasoning_recommended" in review_payload
            else review_payload.get("verification_recommended")
        ),
        "payload": review_payload,
    }


def summarize_review_gaps(snapshot: Mapping[str, Any] | None) -> str:
    data = dict(snapshot or {})
    summary_line = str(data.get("summary_line") or "").strip()
    top_issue = str(data.get("top_issue") or "").strip()
    top_correction = str(data.get("top_correction") or "").strip()
    accuracy_label = str(data.get("accuracy_label") or "").strip()
    confidence_label = str(data.get("confidence_label") or "").strip()

    lines = [
        summary_line or "Bottom line: The review called out a few places to tighten the answer."
    ]
    if top_issue:
        lines.append(f"Main gap: {top_issue}")
    else:
        lines.append("Main gap: No single major gap was called out.")
    if top_correction:
        lines.append(f"Best correction: {top_correction}")
    else:
        lines.append("Best correction: No specific rewrite was proposed.")
    if accuracy_label:
        lines.append(f"Agreement level: {accuracy_label}")
    if confidence_label:
        lines.append(f"Review confidence: {confidence_label}")
    return "\n".join(lines).strip()


def render_original_answer(snapshot: Mapping[str, Any] | None) -> str:
    data = dict(snapshot or {})
    source_answer = str(data.get("source_answer") or "").strip()
    if not source_answer:
        return ""
    return (
        "Bottom line: Here is Nova's original answer before the review.\n\n"
        f"{source_answer}"
    ).strip()


def build_revised_answer_from_review(
    snapshot: Mapping[str, Any] | None,
    *,
    session_id: str,
    request_id: str | None = None,
) -> str:
    data = dict(snapshot or {})
    source_answer = str(data.get("source_answer") or "").strip()
    source_prompt = str(data.get("source_prompt") or "").strip()
    summary_line = str(data.get("summary_line") or "").strip()
    top_issue = str(data.get("top_issue") or "").strip()
    top_correction = str(data.get("top_correction") or "").strip()
    review_text = str(data.get("review_text") or "").strip()

    if not source_answer:
        return ""

    system_prompt = (
        "You are Nova revising one of your own prior answers after an advisory review.\n"
        "Constraints:\n"
        "- Write the final user-facing answer, not the review.\n"
        "- Stay within the original scope of the user's question.\n"
        "- Use the review to correct, narrow, or clarify the prior answer.\n"
        "- Do not mention internal prompts, hidden process, or model routing.\n"
        "- Do not claim new authority, execution rights, or fresh evidence you were not given.\n"
        "- If uncertainty remains, state it plainly.\n"
        "- Start the first line with 'Bottom line:'.\n"
    )
    prompt = (
        "Original user question:\n"
        f"{source_prompt or '(not captured)'}\n\n"
        "Original Nova answer:\n"
        f"{source_answer}\n\n"
        "Review summary:\n"
        f"{summary_line or '(not provided)'}\n"
        f"Main gap: {top_issue or '(not provided)'}\n"
        f"Best correction: {top_correction or '(not provided)'}\n\n"
        "Full review:\n"
        f"{review_text or '(not provided)'}\n\n"
        "Task:\n"
        "Write Nova's final revised answer to the user. Keep it concise but complete."
    )
    revised = generate_chat(
        prompt,
        mode="analysis",
        safety_profile="read_only",
        request_id=request_id or f"review-followthrough-{uuid4()}",
        session_id=session_id,
        system_prompt=system_prompt,
        max_tokens=500,
        temperature=0.2,
        timeout=20.0,
    )
    if revised:
        payload = ResponseFormatter.format_payload(revised, mode="casual")
        return str(payload.get("user_message") or "").strip()

    fallback_lines = [
        "Bottom line: The review suggests a narrower, corrected answer.",
    ]
    if top_correction:
        fallback_lines.extend(
            [
                "",
                top_correction,
            ]
        )
    else:
        fallback_lines.extend(
            [
                "",
                source_answer,
            ]
        )
    if top_issue:
        fallback_lines.extend(
            [
                "",
                f"Main caveat: {top_issue}",
            ]
        )
    return "\n".join(fallback_lines).strip()
