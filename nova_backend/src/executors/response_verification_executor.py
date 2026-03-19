from __future__ import annotations

import re

from src.actions.action_result import ActionResult
from src.conversation.deepseek_bridge import DeepSeekBridge
from src.conversation.deepseek_safety_wrapper import DeepSeekSafetyWrapper


class ResponseVerificationExecutor:
    """Invocation-bound analysis verifier. Advisory only, never authorizing."""

    _UNAVAILABLE_MARKERS = (
        "currently unavailable",
        "structured analysis",
        "model is blocked",
        "version mismatch",
    )

    def __init__(self) -> None:
        self._bridge = DeepSeekBridge()
        self._safety = DeepSeekSafetyWrapper()

    @staticmethod
    def _speakable_report_summary(
        *,
        accuracy_label: str,
        confidence_label: str,
        issue_count: int,
        correction_count: int,
        verification_recommended: bool,
    ) -> str:
        recommendation = (
            "Verification is recommended before relying on this claim."
            if verification_recommended
            else "No immediate re-check is required."
        )
        return (
            "Verification complete. "
            f"Claim reliability {accuracy_label}. "
            f"Report confidence {confidence_label}. "
            f"Potential issues found {issue_count}. "
            f"Suggested corrections {correction_count}. "
            f"{recommendation}"
        )

    @staticmethod
    def _failure_result(
        message: str,
        *,
        request_id: str,
        failure_kind: str,
    ) -> ActionResult:
        payload = {
            "verification_available": False,
            "failure_kind": failure_kind,
        }
        return ActionResult.failure(
            message,
            data=payload,
            structured_data=payload,
            speakable_text=message,
            request_id=request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
            outcome_reason=message,
        )

    def execute(self, request) -> ActionResult:
        text = str((request.params or {}).get("text") or "").strip()
        if not text:
            return self._failure_result(
                "I need text to verify. Ask me to verify a statement or previous response.",
                request_id=request.request_id,
                failure_kind="missing_text",
            )

        prompt = (
            "Verify the following text for factual reliability.\n\n"
            f"Text:\n{text}\n\n"
            "Return exactly these sections:\n"
            "Accuracy: <high|medium|low>\n"
            "Potential Issues:\n"
            "- ...\n"
            "Suggested Corrections:\n"
            "- ...\n"
            "Confidence: <high|medium|low>\n"
            "Do not include execution instructions."
        )

        raw = self._bridge.analyze(
            prompt,
            [],
            suggested_max_tokens=700,
            analysis_profile="task_scoped",
        )
        clean = self._safety.sanitize(raw)
        if not clean:
            return self._failure_result(
                "I couldn't verify that right now.",
                request_id=request.request_id,
                failure_kind="empty_analysis",
            )
        if self._verification_unavailable(clean):
            return self._failure_result(
                "Verification is unavailable in this runtime because structured analysis is currently blocked or unavailable.",
                request_id=request.request_id,
                failure_kind="analysis_unavailable",
            )
        if not self._looks_structured(clean):
            return self._failure_result(
                "Verification returned an incomplete report, so I did not present it as a finished check.",
                request_id=request.request_id,
                failure_kind="incomplete_report",
            )

        accuracy_label, accuracy_score = self._derive_section_label(clean, "accuracy", default="medium")
        confidence_label, confidence_score = self._derive_section_label(clean, "confidence", default=accuracy_label)
        issue_count = self._count_bullets(clean, "Potential Issues")
        correction_count = self._count_bullets(clean, "Suggested Corrections")
        verification_recommended = (
            accuracy_score < 0.75
            or issue_count > 0
            or correction_count > 0
        )
        recommendation_line = (
            "Recommendation: Verification is recommended before relying on this claim."
            if verification_recommended
            else "Recommendation: No immediate re-check required."
        )
        message = (
            "Verification Report\n"
            f"Claim Reliability: {accuracy_label} ({accuracy_score:.2f})\n"
            f"Report Confidence: {confidence_label} ({confidence_score:.2f})\n"
            f"Potential issues found: {issue_count}\n"
            f"Suggested corrections: {correction_count}\n"
            f"{recommendation_line}\n\n"
            f"{clean}\n\n"
            "Try next:\n"
            "- verify a revised version\n"
            "- summarize the issues only\n"
            "- show me the safest corrected version"
        )
        payload = {
            "verification_text": clean,
            "verification_accuracy_label": accuracy_label,
            "verification_accuracy_score": accuracy_score,
            "verification_confidence_label": confidence_label,
            "verification_confidence_score": confidence_score,
            "verification_recommended": verification_recommended,
            "issue_count": issue_count,
            "correction_count": correction_count,
            "follow_up_prompts": [
                "verify a revised version",
                "summarize the issues only",
                "show me the safest corrected version",
            ],
        }
        return ActionResult.ok(
            message=message,
            data=payload,
            structured_data=payload,
            speakable_text=self._speakable_report_summary(
                accuracy_label=accuracy_label,
                confidence_label=confidence_label,
                issue_count=issue_count,
                correction_count=correction_count,
                verification_recommended=verification_recommended,
            ),
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    @classmethod
    def _verification_unavailable(cls, report_text: str) -> bool:
        lowered = str(report_text or "").strip().lower()
        if not lowered:
            return True
        return any(marker in lowered for marker in cls._UNAVAILABLE_MARKERS)

    @staticmethod
    def _looks_structured(report_text: str) -> bool:
        lowered = str(report_text or "").lower()
        required_sections = (
            "accuracy:",
            "potential issues:",
            "suggested corrections:",
            "confidence:",
        )
        return all(section in lowered for section in required_sections)

    @staticmethod
    def _section_text(report_text: str, section_name: str) -> str:
        text = str(report_text or "")
        match = re.search(
            rf"{re.escape(section_name)}\s*:\s*(.+?)(?:\n[A-Z][A-Za-z ]+:\s*|\Z)",
            text,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not match:
            return ""
        return match.group(1).strip()

    @classmethod
    def _derive_section_label(cls, report_text: str, section_name: str, default: str = "medium") -> tuple[str, float]:
        text = (report_text or "").lower()
        match = re.search(rf"\b{re.escape(section_name)}\s*:\s*(high|medium|low)\b", text, flags=re.IGNORECASE)
        label = (match.group(1) if match else None) or default
        normalized = str(label).strip().lower()
        if normalized == "high":
            return "High", 0.9
        if normalized == "low":
            return "Low", 0.4
        return "Medium", 0.65

    @classmethod
    def _count_bullets(cls, report_text: str, section_name: str) -> int:
        block = cls._section_text(report_text, section_name)
        if not block:
            return 0
        bullet_lines = []
        for line in block.splitlines():
            stripped = line.strip()
            if not stripped.startswith("-"):
                continue
            payload = stripped.lstrip("-").strip().lower()
            if payload in {"none", "none.", "none noted", "none identified", "not applicable", "n/a"}:
                continue
            bullet_lines.append(line)
        if bullet_lines:
            return len(bullet_lines)
        lowered = block.strip().lower()
        normalized = lowered.lstrip("-").strip()
        if not normalized or normalized in {"none", "none.", "none noted", "none identified", "not applicable", "n/a"}:
            return 0
        if normalized.startswith("none identified") or normalized.startswith("none noted") or normalized.startswith("not applicable"):
            return 0
        return 1
