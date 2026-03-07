from __future__ import annotations

import re

from src.actions.action_result import ActionResult
from src.conversation.deepseek_bridge import DeepSeekBridge
from src.conversation.deepseek_safety_wrapper import DeepSeekSafetyWrapper


class ResponseVerificationExecutor:
    """Invocation-bound analysis verifier. Advisory only, never authorizing."""

    def __init__(self) -> None:
        self._bridge = DeepSeekBridge()
        self._safety = DeepSeekSafetyWrapper()

    def execute(self, request) -> ActionResult:
        text = str((request.params or {}).get("text") or "").strip()
        if not text:
            return ActionResult.failure(
                "I need text to verify. Ask me to verify a statement or previous response.",
                request_id=request.request_id,
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

        raw = self._bridge.analyze(prompt, [], suggested_max_tokens=700)
        clean = self._safety.sanitize(raw)
        if not clean:
            return ActionResult.failure(
                "I couldn't verify that right now.",
                request_id=request.request_id,
            )

        confidence_label, confidence_score = self._derive_confidence(clean)
        verification_recommended = confidence_score < 0.75
        recommendation_line = (
            "Recommendation: Verification is recommended before relying on this claim."
            if verification_recommended
            else "Recommendation: No immediate re-check required."
        )
        message = (
            "Verification Report\n"
            f"Verification Confidence: {confidence_label} ({confidence_score:.2f})\n"
            f"{recommendation_line}\n\n"
            f"{clean}"
        )
        return ActionResult.ok(
            message=message,
            data={
                "verification_text": clean,
                "verification_confidence_label": confidence_label,
                "verification_confidence_score": confidence_score,
                "verification_recommended": verification_recommended,
            },
            request_id=request.request_id,
            authority_class="read_only",
            external_effect=False,
            reversible=True,
        )

    @staticmethod
    def _derive_confidence(report_text: str) -> tuple[str, float]:
        text = (report_text or "").lower()
        confidence_match = re.search(r"\bconfidence\s*:\s*(high|medium|low)\b", text, flags=re.IGNORECASE)
        accuracy_match = re.search(r"\baccuracy\s*:\s*(high|medium|low)\b", text, flags=re.IGNORECASE)
        label = (confidence_match.group(1) if confidence_match else None) or (
            accuracy_match.group(1) if accuracy_match else "medium"
        )
        normalized = str(label).strip().lower()
        if normalized == "high":
            return "High", 0.9
        if normalized == "low":
            return "Low", 0.4
        return "Medium", 0.65
