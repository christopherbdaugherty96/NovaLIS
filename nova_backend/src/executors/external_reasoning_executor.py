from __future__ import annotations

from types import SimpleNamespace

from src.actions.action_result import ActionResult
from src.executors.response_verification_executor import ResponseVerificationExecutor


class ExternalReasoningExecutor:
    """Governed same-thread second-opinion lane. Advisory only, never authorizing."""

    _PROVIDER_LABEL = "DeepSeek"
    _ROUTE_LABEL = "Governed second-opinion lane"
    _ROUTE_DETAIL = "Governor -> ExternalReasoningExecutor -> DeepSeekBridge -> llm_gateway"
    _AUTHORITY_LABEL = "Advisory only"
    _GOVERNANCE_NOTE = (
        "This review can critique Nova's answer, but it cannot take actions or widen Nova's authority."
    )

    def __init__(self) -> None:
        self._verification = ResponseVerificationExecutor()

    def execute(self, request) -> ActionResult:
        text = str((request.params or {}).get("text") or "").strip()
        if not text:
            return ActionResult.failure(
                "I need an answer or exchange to review before I can give a second opinion.",
                data={
                    "reasoning_available": False,
                    "failure_kind": "missing_text",
                    "reasoning_provider": self._PROVIDER_LABEL,
                    "reasoning_provider_label": self._PROVIDER_LABEL,
                    "reasoning_route": self._ROUTE_DETAIL,
                    "reasoning_route_label": self._ROUTE_LABEL,
                    "reasoning_mode": "second_opinion",
                    "reasoning_authority": "analysis_only",
                    "reasoning_authority_label": self._AUTHORITY_LABEL,
                    "reasoning_governance_note": self._GOVERNANCE_NOTE,
                },
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
                speakable_text="I need an answer or exchange to review first.",
                structured_data={
                    "reasoning_available": False,
                    "failure_kind": "missing_text",
                    "reasoning_provider": self._PROVIDER_LABEL,
                    "reasoning_provider_label": self._PROVIDER_LABEL,
                    "reasoning_route": self._ROUTE_DETAIL,
                    "reasoning_route_label": self._ROUTE_LABEL,
                    "reasoning_mode": "second_opinion",
                    "reasoning_authority": "analysis_only",
                    "reasoning_authority_label": self._AUTHORITY_LABEL,
                    "reasoning_governance_note": self._GOVERNANCE_NOTE,
                },
                outcome_reason="Missing text for external reasoning review.",
            )

        base_request = SimpleNamespace(
            capability_id=31,
            params={"text": text, "review_mode": "second_opinion"},
            request_id=request.request_id,
        )
        base_result = self._verification.execute(base_request)
        base_payload = dict(base_result.structured_data or {})

        shared_payload = {
            "reasoning_available": bool(base_result.success),
            "reasoning_provider": self._PROVIDER_LABEL,
            "reasoning_provider_label": self._PROVIDER_LABEL,
            "reasoning_route": self._ROUTE_DETAIL,
            "reasoning_route_label": self._ROUTE_LABEL,
            "reasoning_mode": "second_opinion",
            "reasoning_authority": "analysis_only",
            "reasoning_authority_label": self._AUTHORITY_LABEL,
            "reasoning_governance_note": self._GOVERNANCE_NOTE,
            "analysis_profile": "task_scoped",
        }

        if not base_result.success:
            failure_kind = str(base_payload.get("failure_kind") or "analysis_unavailable").strip() or "analysis_unavailable"
            message = str(base_result.message or "Governed second opinion is unavailable right now.").strip()
            if failure_kind == "analysis_unavailable":
                message = (
                    "Governed second opinion is unavailable right now because the analysis lane is blocked or unavailable."
                )
            payload = {
                **shared_payload,
                "failure_kind": failure_kind,
            }
            return ActionResult.failure(
                message,
                data=payload,
                structured_data=payload,
                speakable_text="Governed second opinion is unavailable right now.",
                request_id=request.request_id,
                authority_class="read_only",
                external_effect=False,
                reversible=True,
                outcome_reason=message,
            )

        accuracy_label = str(base_payload.get("verification_accuracy_label") or "").strip()
        accuracy_score = float(base_payload.get("verification_accuracy_score") or 0.0)
        confidence_label = str(base_payload.get("verification_confidence_label") or "").strip()
        confidence_score = float(base_payload.get("verification_confidence_score") or 0.0)
        issue_count = int(base_payload.get("issue_count") or 0)
        correction_count = int(base_payload.get("correction_count") or 0)
        reasoning_text = str(base_payload.get("verification_text") or "").strip()
        follow_up_prompts = list(base_payload.get("follow_up_prompts") or [])

        recommendation_line = (
            "Recommendation: Ask Nova to revise the answer before relying on it."
            if bool(base_payload.get("verification_recommended"))
            else "Recommendation: No immediate re-check is required."
        )

        message = (
            "Governed Second Opinion\n"
            f"Provider: {self._PROVIDER_LABEL}\n"
            f"Route: {self._ROUTE_LABEL}\n"
            f"Authority: {self._AUTHORITY_LABEL}\n"
            f"Agreement Level: {accuracy_label} ({accuracy_score:.2f})\n"
            f"Review Confidence: {confidence_label} ({confidence_score:.2f})\n"
            f"Gaps or concerns found: {issue_count}\n"
            f"Suggested improvements: {correction_count}\n"
            f"{recommendation_line}\n"
            f"Note: {self._GOVERNANCE_NOTE}\n\n"
            f"{reasoning_text}\n\n"
            "Try next:\n"
            "- ask Nova to revise the answer\n"
            "- summarize the gaps only\n"
            "- return to Nova's original answer"
        )
        speakable_text = (
            "Second opinion ready. "
            f"Agreement level {accuracy_label}. "
            f"Review confidence {confidence_label}. "
            f"Gaps noted {issue_count}. "
            f"Suggested improvements {correction_count}. "
            "Advisory only. Nova remains in control."
        )
        payload = {
            **shared_payload,
            "reasoning_text": reasoning_text,
            "reasoning_accuracy_label": accuracy_label,
            "reasoning_accuracy_score": accuracy_score,
            "reasoning_confidence_label": confidence_label,
            "reasoning_confidence_score": confidence_score,
            "reasoning_recommended": bool(base_payload.get("verification_recommended")),
            "issue_count": issue_count,
            "correction_count": correction_count,
            "follow_up_prompts": follow_up_prompts,
            "reasoning_visible_label": "Governed second opinion",
        }
        return ActionResult.ok(
            message=message,
            data=payload,
            structured_data=payload,
            speakable_text=speakable_text,
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )
