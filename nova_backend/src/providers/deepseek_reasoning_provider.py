from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Any

from src.governor.network_mediator import NetworkMediator, NetworkMediatorError
from src.usage.provider_usage_store import provider_usage_store


class DeepSeekReasoningProviderError(RuntimeError):
    """Raised when the governed DeepSeek reasoning provider cannot run."""


LEGACY_MODEL_NAMES = frozenset({"deepseek-chat", "deepseek-reasoner"})
DEFAULT_DEEPSEEK_MODEL = "deepseek-v4-flash"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
CAPABILITY_ID = 62
ROUTE_LABEL = "DeepSeek Chat Completions API via NetworkMediator"

_TOOLISH_PATTERNS = (
    re.compile(r"<function_call[^>]*>", re.IGNORECASE),
    re.compile(r"<tool_use[^>]*>", re.IGNORECASE),
    re.compile(r"<\|tool_call\|>", re.IGNORECASE),
    re.compile(r"\btool_call\b", re.IGNORECASE),
    re.compile(r"\bfunction\s*:\s*(?P<name>[A-Za-z0-9_.-]+)?", re.IGNORECASE),
    re.compile(r"\bcapability\s*[_-]?id\s*[:=]?\s*(?P<capability_id>\d+)", re.IGNORECASE),
    re.compile(r"\bconfirmed\s*[:=]\s*true\b", re.IGNORECASE),
    re.compile(r'[{]\s*"(?:tool|function_call|function|action)"\s*:', re.IGNORECASE),
    re.compile(r"```(?:tool_call|function_call)[^\n]*\n.*?```", re.IGNORECASE | re.DOTALL),
)
_ACTIONISH_PATTERNS = (
    re.compile(r"\b(shopify|store)\b.{0,80}\b(write|update|change|set|publish|refund|fulfill|delete)\b", re.IGNORECASE),
    re.compile(r"\b(write|update|change|set|publish|refund|fulfill|delete)\b.{0,80}\b(shopify|store)\b", re.IGNORECASE),
    re.compile(r"\b(email|mail|message)\b.{0,80}\b(send|draft|open|submit)\b", re.IGNORECASE),
    re.compile(r"\b(send|draft|open|submit)\b.{0,80}\b(email|mail|message)\b", re.IGNORECASE),
    re.compile(r"\b(print|printer|rj\s*print)\b.{0,80}\b(print|send|submit|queue)\b", re.IGNORECASE),
    re.compile(r"\b(print|send|submit|queue)\b.{0,80}\b(print|printer|rj\s*print)\b", re.IGNORECASE),
    re.compile(r"\b(file|directory|folder)\b.{0,80}\b(delete|remove|rm|rmdir|unlink|write|overwrite)\b", re.IGNORECASE),
    re.compile(r"\b(delete|remove|rm|rmdir|unlink|write|overwrite)\b.{0,80}\b(file|directory|folder)\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class ReasoningSuggestion:
    """Inert model-suggested action language. Never executable."""

    kind: str
    text: str
    blocked_reason: str
    executable: bool = False
    confirmed: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "text": self.text,
            "blocked_reason": self.blocked_reason,
            "executable": False,
            "confirmed": False,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class DeepSeekReasoningResult:
    text: str
    provider: str
    model: str
    route: str
    request_id: str
    suggestions: tuple[ReasoningSuggestion, ...] = tuple()
    usage_meta: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "provider": self.provider,
            "model": self.model,
            "route": self.route,
            "request_id": self.request_id,
            "suggestions": [item.as_dict() for item in self.suggestions],
            "usage_meta": dict(self.usage_meta),
        }


class DeepSeekReasoningProvider:
    """Governed network advisory provider for Cap 62.

    This adapter returns text and inert suggestions only. It never returns
    Invocation, ActionRequest, confirmed params, or dispatchable tool calls.
    """

    def __init__(self, *, network: NetworkMediator | None = None) -> None:
        self._network = network or NetworkMediator()

    @staticmethod
    def configured_model() -> str:
        model = str(os.getenv("DEEPSEEK_MODEL") or DEFAULT_DEEPSEEK_MODEL).strip().lower()
        return model or DEFAULT_DEEPSEEK_MODEL

    @classmethod
    def validate_model(cls, model: str | None = None) -> str:
        normalized = str(model or cls.configured_model()).strip().lower()
        if normalized in LEGACY_MODEL_NAMES:
            raise DeepSeekReasoningProviderError(
                "Legacy DeepSeek model names deepseek-chat and deepseek-reasoner are not allowed. "
                "Use deepseek-v4-flash or deepseek-v4-pro."
            )
        if normalized not in {"deepseek-v4-flash", "deepseek-v4-pro"}:
            raise DeepSeekReasoningProviderError(
                f"Unsupported DeepSeek model: {normalized or '<empty>'}. "
                "Use deepseek-v4-flash or deepseek-v4-pro."
            )
        return normalized

    def analyze(
        self,
        *,
        prompt: str,
        system_prompt: str = "",
        request_id: str = "deepseek_bridge",
        analysis_profile: str = "analysis",
        max_tokens: int = 800,
        temperature: float = 0.2,
        timeout: float = 90.0,
    ) -> DeepSeekReasoningResult:
        api_key = str(os.getenv("DEEPSEEK_API_KEY") or "").strip()
        if not api_key:
            raise DeepSeekReasoningProviderError("DEEPSEEK_API_KEY is not configured.")

        model = self.validate_model()
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        str(system_prompt or "").strip()
                        or "You are an advisory reasoning provider for Nova. Return analysis only. Do not call tools."
                    ),
                },
                {"role": "user", "content": str(prompt or "").strip()},
            ],
            "max_tokens": int(max(1, max_tokens)),
            "temperature": float(temperature),
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self._network.request(
                CAPABILITY_ID,
                "POST",
                DEEPSEEK_API_URL,
                json_payload=payload,
                headers=headers,
                as_json=True,
                timeout=timeout,
                request_id=request_id,
            )
        except NetworkMediatorError as exc:
            raise DeepSeekReasoningProviderError(str(exc)) from exc

        data = dict(response.get("data") or {})
        raw_text = self._extract_text(data)
        if not raw_text:
            raise DeepSeekReasoningProviderError("DeepSeek returned an empty response.")

        clean_text, suggestions = self._extract_advisory_text(raw_text)
        usage = self._extract_usage(data)
        usage_snapshot = provider_usage_store.record_reasoning_event(
            provider="DeepSeek external reasoning provider",
            route=ROUTE_LABEL,
            analysis_profile=analysis_profile,
            prompt_text=prompt,
            response_text=clean_text,
            model_label=model,
            request_id=request_id,
            exact_usage_available=usage["exact_usage_available"],
            exact_input_tokens=usage["input_tokens"],
            exact_output_tokens=usage["output_tokens"],
            exact_total_tokens=usage["total_tokens"],
        )
        return DeepSeekReasoningResult(
            text=clean_text,
            provider="DeepSeek",
            model=model,
            route=ROUTE_LABEL,
            request_id=str(request_id or "").strip(),
            suggestions=tuple(suggestions),
            usage_meta={
                "exact_input_tokens": usage["input_tokens"],
                "exact_output_tokens": usage["output_tokens"],
                "exact_total_tokens": usage["total_tokens"],
                "exact_usage_available": usage["exact_usage_available"],
                "budget_state": str(usage_snapshot.get("budget_state") or "normal"),
                "budget_state_label": str(usage_snapshot.get("budget_state_label") or "Normal"),
            },
        )

    @staticmethod
    def _extract_text(payload: dict[str, Any]) -> str:
        choices = list(payload.get("choices") or [])
        if choices:
            message = dict(dict(choices[0]).get("message") or {})
            content = message.get("content")
            if isinstance(content, str):
                return content.strip()
            if isinstance(content, list):
                parts = [
                    str(dict(part).get("text") or "").strip()
                    for part in content
                    if isinstance(part, dict)
                ]
                return "\n".join(part for part in parts if part).strip()
        return str(payload.get("output_text") or "").strip()

    @staticmethod
    def _extract_usage(payload: dict[str, Any]) -> dict[str, Any]:
        usage = dict(payload.get("usage") or {})
        input_tokens = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
        total_tokens = int(usage.get("total_tokens") or 0)
        if total_tokens <= 0 and (input_tokens > 0 or output_tokens > 0):
            total_tokens = input_tokens + output_tokens
        return {
            "input_tokens": max(0, input_tokens),
            "output_tokens": max(0, output_tokens),
            "total_tokens": max(0, total_tokens),
            "exact_usage_available": bool(total_tokens > 0 or input_tokens > 0 or output_tokens > 0),
        }

    @classmethod
    def _extract_advisory_text(cls, text: str) -> tuple[str, list[ReasoningSuggestion]]:
        clean = str(text or "").strip()
        suggestions: list[ReasoningSuggestion] = []
        if not clean:
            return "", suggestions

        for pattern in _TOOLISH_PATTERNS:
            for match in list(pattern.finditer(clean)):
                suggestions.append(
                    ReasoningSuggestion(
                        kind="blocked_tool_or_capability_call",
                        text=match.group(0),
                        blocked_reason="External reasoning output is advisory only and cannot call tools or capabilities.",
                        metadata={k: v for k, v in match.groupdict().items() if v},
                    )
                )
            clean = pattern.sub("[advisory suggestion removed]", clean)

        for pattern in _ACTIONISH_PATTERNS:
            for match in list(pattern.finditer(clean)):
                suggestions.append(
                    ReasoningSuggestion(
                        kind="blocked_action_suggestion",
                        text=match.group(0),
                        blocked_reason="Suggested actions must be reviewed by Nova and routed through existing governed authority paths.",
                    )
                )
            clean = pattern.sub("[advisory action suggestion removed]", clean)

        clean = re.sub(r"\bconfirmed\s*[:=]\s*true\b", "[confirmation removed]", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\n{3,}", "\n\n", clean)
        clean = re.sub(r"[ \t]{2,}", " ", clean)
        return clean.strip(), suggestions
