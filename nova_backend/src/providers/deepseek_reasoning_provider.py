from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

from src.governor.network_mediator import NetworkMediator, NetworkMediatorError
from src.usage.provider_usage_store import provider_usage_store

_log = logging.getLogger(__name__)


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


def _check_budget_gate(
    *,
    analysis_profile: str,
    request_id: str,
    model: str,
) -> str:
    """Pre-call budget gate. Returns budget state.

    If "limit", emits PROVIDER_USAGE_BLOCKED. Caller must not
    proceed with the network call when state is "limit".
    """
    try:
        from src.usage.provider_budget_policy import (
            DEFAULT_POLICIES,
            ProviderUsageTotals,
            compute_budget_state,
        )

        policy = DEFAULT_POLICIES.get("deepseek")
        if policy is None:
            return "normal"

        snapshot = provider_usage_store.snapshot()
        daily_tokens = int(
            snapshot.get("estimated_total_tokens") or 0
        )
        daily_cost = float(
            snapshot.get("estimated_cost_usd") or 0.0
        )
        daily_calls = int(snapshot.get("event_count") or 0)

        usage = ProviderUsageTotals(
            daily_tokens=daily_tokens,
            daily_cost_usd=daily_cost,
            daily_call_count=daily_calls,
        )
        budget_state = compute_budget_state(usage, policy)

        if budget_state == "limit":
            event_meta = {
                "provider_id": "deepseek",
                "model": model,
                "analysis_profile": analysis_profile,
                "request_id": request_id,
                "daily_tokens": daily_tokens,
                "daily_cost_usd": round(daily_cost, 6),
                "daily_call_count": daily_calls,
                "budget_state": "limit",
                "policy_daily_token_limit": (
                    policy.daily_token_limit
                ),
                "policy_daily_cost_limit_usd": (
                    policy.daily_cost_limit_usd
                ),
                "enforcement": "hard",
            }
            try:
                from src.ledger.writer import LedgerWriter

                ledger = LedgerWriter()
                ledger.log_event(
                    "PROVIDER_USAGE_BLOCKED", event_meta,
                )
            except Exception:
                _log.debug(
                    "Budget gate ledger event failed",
                    exc_info=True,
                )
            _log.warning(
                "DeepSeek budget blocked: %d/%d daily tokens"
                " (profile=%s, request=%s)",
                daily_tokens,
                policy.daily_token_limit,
                analysis_profile,
                request_id,
            )

        return budget_state
    except Exception:
        _log.debug("Budget gate check failed", exc_info=True)
        return "normal"


def _log_budget_event(
    *,
    usage_snapshot: dict[str, Any],
    analysis_profile: str,
    request_id: str,
    model: str,
) -> str:
    """Post-call budget logging. Records usage and warns if needed."""
    from src.usage.provider_budget_policy import (
        DEFAULT_POLICIES,
        ProviderUsageTotals,
        compute_budget_state,
    )

    policy = DEFAULT_POLICIES.get("deepseek")
    if policy is None:
        return "normal"

    daily_tokens = int(
        usage_snapshot.get("estimated_total_tokens") or 0
    )
    daily_cost = float(
        usage_snapshot.get("estimated_cost_usd") or 0.0
    )
    daily_calls = int(usage_snapshot.get("event_count") or 0)

    usage = ProviderUsageTotals(
        daily_tokens=daily_tokens,
        daily_cost_usd=daily_cost,
        daily_call_count=daily_calls,
    )
    budget_state = compute_budget_state(usage, policy)

    event_meta = {
        "provider_id": "deepseek",
        "model": model,
        "analysis_profile": analysis_profile,
        "request_id": request_id,
        "daily_tokens": daily_tokens,
        "daily_cost_usd": round(daily_cost, 6),
        "daily_call_count": daily_calls,
        "budget_state": budget_state,
        "policy_daily_token_limit": policy.daily_token_limit,
        "policy_daily_cost_limit_usd": policy.daily_cost_limit_usd,
        "enforcement": "hard",
    }

    try:
        from src.ledger.writer import LedgerWriter

        ledger = LedgerWriter()
        ledger.log_event("PROVIDER_USAGE_RECORDED", event_meta)

        if budget_state == "warning":
            ledger.log_event("PROVIDER_BUDGET_WARNING", event_meta)
            _log.info(
                "DeepSeek budget warning: %d/%d daily tokens"
                " (profile=%s, request=%s)",
                daily_tokens,
                policy.daily_token_limit,
                analysis_profile,
                request_id,
            )
        elif budget_state == "limit":
            ledger.log_event("PROVIDER_USAGE_BLOCKED", {
                **event_meta,
                "crossed_during_call": True,
            })
            _log.warning(
                "DeepSeek budget crossed limit during call: "
                "%d/%d daily tokens"
                " (profile=%s, request=%s)",
                daily_tokens,
                policy.daily_token_limit,
                analysis_profile,
                request_id,
            )
    except Exception:
        _log.debug("Budget ledger event failed", exc_info=True)

    return budget_state


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

        budget_gate_state = _check_budget_gate(
            analysis_profile=analysis_profile,
            request_id=request_id,
            model=model,
        )
        if budget_gate_state == "limit":
            return DeepSeekReasoningResult(
                text=(
                    "DeepSeek analysis is temporarily unavailable"
                    " — daily budget limit reached. Nova will"
                    " use local reasoning as a fallback."
                ),
                provider="DeepSeek",
                model=model,
                route="budget_blocked",
                request_id=str(request_id or "").strip(),
                usage_meta={
                    "policy_budget_state": "limit",
                    "analysis_profile": analysis_profile,
                    "blocked": True,
                    "enforcement": "hard",
                },
            )

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
        policy_budget_state = _log_budget_event(
            usage_snapshot=usage_snapshot,
            analysis_profile=analysis_profile,
            request_id=request_id,
            model=model,
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
                "policy_budget_state": policy_budget_state,
                "analysis_profile": analysis_profile,
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
