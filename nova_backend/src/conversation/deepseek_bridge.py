import logging
import os
import re
from typing import List

from src.cognition.cognitive_operation_logger import CognitiveOperationLogger
from src.governor.capability_registry import CapabilityRegistry
from src.governor.exceptions import CapabilityRegistryError
from src.llm import llm_gateway
from src.providers.deepseek_reasoning_provider import (
    DeepSeekReasoningProvider,
    DeepSeekReasoningProviderError,
)
from src.usage.provider_usage_store import provider_usage_store

_CAP_62_ID = 62

from . import prompts

logger = logging.getLogger(__name__)

MAX_TOKENS = 1000
ANALYSIS_TIMEOUT_SECONDS = 90.0


class DeepSeekBridge:
    """Analysis-only cognitive bridge. No capabilities, no execution."""

    _DEEP_REASON_HEADERS = (
        "Core answer:",
        "Key drivers:",
        "Risks and uncertainties:",
        "What to verify next:",
    )

    def __init__(self) -> None:
        self._cognitive_log = CognitiveOperationLogger()
        self._provider = DeepSeekReasoningProvider()
        self._registry = CapabilityRegistry()

    def analyze(
        self,
        user_message: str,
        context: List[dict],
        suggested_max_tokens: int = 800,
        *,
        analysis_profile: str = "deep_reason",
        timeout_seconds: float = ANALYSIS_TIMEOUT_SECONDS,
    ) -> str:
        try:
            if not self._registry.is_enabled(_CAP_62_ID):
                return "I can provide structured analysis, but the governed DeepSeek provider is not enabled."
        except CapabilityRegistryError:
            return "I can provide structured analysis, but the governed DeepSeek provider is not available."

        started_at = self._cognitive_log.started(
            module_name="deepseek_bridge",
            mode="analysis",
            request_id="deepseek_bridge",
        )
        prompt = prompts.build_analysis_prompt(user_message, context, profile=analysis_profile)
        response = ""
        try:
            try:
                provider_result = self._provider.analyze(
                    prompt=prompt,
                    request_id="deepseek_bridge",
                    analysis_profile=analysis_profile,
                    max_tokens=min(MAX_TOKENS, suggested_max_tokens),
                    temperature=0.2,
                    timeout=timeout_seconds,
                )
                if provider_result.route == "budget_blocked":
                    if not self._local_fallback_enabled():
                        return (
                            "DeepSeek analysis is temporarily"
                            " unavailable -- daily budget limit"
                            " reached."
                        )
                    logger.info(
                        "DeepSeek budget-blocked; falling"
                        " through to local reasoning"
                    )
                else:
                    response = provider_result.text
                    if response:
                        if analysis_profile == "deep_reason":
                            return self._normalize_deep_reason_response(response)
                        return response
            except DeepSeekReasoningProviderError as error:
                if not self._local_fallback_enabled():
                    logger.error("DeepSeek provider unavailable: %s", error)
                    return "I can provide structured analysis, but the governed DeepSeek provider is currently unavailable."
                logger.warning("DeepSeek provider unavailable; using explicit local fallback: %s", error)

            response = llm_gateway.generate_chat(
                prompt,
                mode="analysis_only",
                safety_profile="analysis",
                request_id="deepseek_bridge",
                max_tokens=min(MAX_TOKENS, suggested_max_tokens),
                temperature=0.2,
                timeout=timeout_seconds,
            )
            if response:
                provider_usage_store.record_reasoning_event(
                    provider="DeepSeek reasoning lane",
                    route="DeepSeekBridge -> llm_gateway (explicit local fallback)",
                    analysis_profile=analysis_profile,
                    prompt_text=prompt,
                    response_text=response,
                    model_label="local fallback for DeepSeekBridge",
                    request_id="deepseek_bridge",
                    exact_usage_available=False,
                )
                if analysis_profile == "deep_reason":
                    return self._normalize_deep_reason_response(response)
                return response
            logger.error("Analysis call failed via centralized gateway.")
            return "I can provide structured analysis, but it is currently unavailable."
        finally:
            self._cognitive_log.completed(
                module_name="deepseek_bridge",
                mode="analysis",
                started_at=started_at,
                request_id="deepseek_bridge",
                success=bool(response),
            )

    @staticmethod
    def _local_fallback_enabled() -> bool:
        return str(os.getenv("NOVA_ALLOW_LOCAL_REASONING_FALLBACK") or "").strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    @classmethod
    def _normalize_deep_reason_response(cls, text: str) -> str:
        clean = str(text or "").strip()
        if not clean:
            return clean

        if cls._has_required_headers(clean):
            return cls._canonicalize_headers(clean)

        paragraphs = [
            re.sub(r"\s+", " ", chunk).strip(" -")
            for chunk in re.split(r"\n\s*\n+", clean)
            if chunk.strip()
        ]
        if not paragraphs:
            paragraphs = [re.sub(r"\s+", " ", clean).strip()]

        core_answer = cls._strip_known_header_prefix(paragraphs[0])
        remaining = paragraphs[1:]
        if not remaining:
            sentences = [
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", clean)
                if sentence.strip()
            ]
            core_answer = cls._strip_known_header_prefix(" ".join(sentences[:2]).strip() or clean)
            remaining = sentences[2:]

        key_drivers = cls._as_bullets(remaining[:2]) or ["- Primary drivers were not clearly separated in the model output."]
        risks = cls._infer_risks(clean)
        verify_next = cls._infer_verify_next(clean)

        return "\n".join(
            [
                "Core answer:",
                core_answer,
                "",
                "Key drivers:",
                *key_drivers,
                "",
                "Risks and uncertainties:",
                *risks,
                "",
                "What to verify next:",
                *verify_next,
            ]
        ).strip()

    @classmethod
    def _has_required_headers(cls, text: str) -> bool:
        lowered = str(text or "").lower()
        return all(header.lower() in lowered for header in cls._DEEP_REASON_HEADERS)

    @classmethod
    def _canonicalize_headers(cls, text: str) -> str:
        normalized = str(text or "").strip()
        replacements = {
            r"(?im)^core answer\s*:\s*": "Core answer:\n",
            r"(?im)^key drivers\s*:\s*": "Key drivers:\n",
            r"(?im)^risks and uncertainties\s*:\s*": "Risks and uncertainties:\n",
            r"(?im)^what to verify next\s*:\s*": "What to verify next:\n",
        }
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        return normalized.strip()

    @staticmethod
    def _as_bullets(items: list[str]) -> list[str]:
        bullets: list[str] = []
        for item in items:
            clean = re.sub(r"\s+", " ", str(item or "")).strip(" -")
            clean = DeepSeekBridge._strip_known_header_prefix(clean)
            if clean:
                bullets.append(f"- {clean}")
        return bullets

    @classmethod
    def _strip_known_header_prefix(cls, text: str) -> str:
        clean = str(text or "").strip()
        for header in cls._DEEP_REASON_HEADERS:
            if clean.lower().startswith(header.lower()):
                return clean[len(header):].strip() or clean
        return clean

    @classmethod
    def _infer_risks(cls, text: str) -> list[str]:
        lowered = str(text or "").lower()
        hints = []
        if any(token in lowered for token in ("uncertain", "uncertainty", "unclear", "mixed", "limited")):
            hints.append("- Evidence remains mixed or incomplete in the current analysis.")
        if any(token in lowered for token in ("forecast", "predict", "future", "likely")):
            hints.append("- Forward-looking claims may shift as conditions change.")
        if not hints:
            hints.append("- Evidence may be incomplete, so the conclusion should be treated as provisional.")
        return hints

    @staticmethod
    def _infer_verify_next(text: str) -> list[str]:
        lowered = str(text or "").lower()
        hints = []
        if "source" in lowered or "evidence" in lowered:
            hints.append("- Re-check the key claim against primary sources or current system data.")
        if "compare" in lowered or "difference" in lowered:
            hints.append("- Verify the comparison against the most recent concrete metrics.")
        if not hints:
            hints.append("- Verify the main claim against a primary source or current runtime data.")
        return hints
