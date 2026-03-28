from __future__ import annotations

import os
from typing import Any

from src.governor.network_mediator import NetworkMediator, NetworkMediatorError
from src.settings.runtime_settings_store import runtime_settings_store
from src.usage.provider_usage_store import provider_usage_store


class OpenAIResponsesLaneError(RuntimeError):
    """Raised when the narrow OpenAI metered lane cannot complete a request."""


class OpenAIResponsesLane:
    """Narrow OpenAI Responses API lane for governed metered summaries."""

    API_URL = "https://api.openai.com/v1/responses"
    CAPABILITY_ID = 62
    ROUTE_LABEL = "OpenAI Responses API via NetworkMediator"
    MODEL_PRICING_PER_MILLION = {
        "gpt-5.4": {"input": 2.50, "output": 15.00},
        "gpt-5.4-mini": {"input": 0.750, "output": 4.500},
        "gpt-5.4-nano": {"input": 0.20, "output": 1.25},
    }

    def __init__(self, *, network: NetworkMediator | None = None) -> None:
        self._network = network or NetworkMediator()

    def plan_for_openclaw_fallback(self) -> dict[str, Any]:
        settings_snapshot = runtime_settings_store.snapshot()
        provider_policy = dict(settings_snapshot.get("provider_policy") or {})
        usage_budget = dict(settings_snapshot.get("usage_budget") or {})
        provider_usage_store.configure_budget(
            daily_token_budget=int(usage_budget.get("daily_metered_token_budget") or 4000),
            warning_ratio=float(usage_budget.get("warning_ratio") or 0.8),
        )
        usage_snapshot = provider_usage_store.snapshot()

        api_key = str(os.getenv("OPENAI_API_KEY") or "").strip()
        permission_enabled = runtime_settings_store.is_permission_enabled("metered_openai_enabled")
        routing_mode = str(provider_policy.get("routing_mode") or "local_first").strip() or "local_first"
        preferred_model = str(provider_policy.get("preferred_openai_model") or "gpt-5.4-mini").strip() or "gpt-5.4-mini"
        budget_state = str(usage_snapshot.get("budget_state") or "normal").strip() or "normal"

        if routing_mode != "budgeted_fallback":
            return {
                "allowed": False,
                "reason": "Automatic OpenAI fallback stays off unless routing mode is set to budgeted fallback.",
                "routing_mode": routing_mode,
                "preferred_model": preferred_model,
                "budget_state": budget_state,
            }
        if not permission_enabled:
            return {
                "allowed": False,
                "reason": "Metered OpenAI lane is paused in Settings.",
                "routing_mode": routing_mode,
                "preferred_model": preferred_model,
                "budget_state": budget_state,
            }
        if not api_key:
            return {
                "allowed": False,
                "reason": "OPENAI_API_KEY is not configured.",
                "routing_mode": routing_mode,
                "preferred_model": preferred_model,
                "budget_state": budget_state,
            }
        if budget_state == "limit":
            return {
                "allowed": False,
                "reason": "Metered OpenAI budget limit has been reached for today.",
                "routing_mode": routing_mode,
                "preferred_model": preferred_model,
                "budget_state": budget_state,
            }
        return {
            "allowed": True,
            "reason": "Budgeted OpenAI fallback is allowed.",
            "routing_mode": routing_mode,
            "preferred_model": preferred_model,
            "budget_state": budget_state,
        }

    def summarize_task_report(
        self,
        *,
        prompt: str,
        system_prompt: str,
        model: str,
        request_id: str,
        max_output_tokens: int = 220,
        task_label: str = "OpenClaw task report",
    ) -> dict[str, Any]:
        api_key = str(os.getenv("OPENAI_API_KEY") or "").strip()
        if not api_key:
            raise OpenAIResponsesLaneError("OPENAI_API_KEY is not configured.")

        payload = {
            "model": model,
            "input": [
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": str(system_prompt or "").strip()}],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": str(prompt or "").strip()}],
                },
            ],
            "max_output_tokens": int(max_output_tokens),
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = self._network.request(
                self.CAPABILITY_ID,
                "POST",
                self.API_URL,
                json_payload=payload,
                headers=headers,
                as_json=True,
                timeout=45.0,
                request_id=request_id,
            )
        except NetworkMediatorError as exc:
            raise OpenAIResponsesLaneError(str(exc)) from exc

        data = dict(response.get("data") or {})
        text = self._extract_text(data)
        if not text:
            raise OpenAIResponsesLaneError("OpenAI returned an empty response.")

        usage = self._extract_usage(data)
        estimated_cost_usd = self._estimate_cost_usd(
            model=model,
            input_tokens=usage["input_tokens"],
            output_tokens=usage["output_tokens"],
        )
        usage_snapshot = provider_usage_store.record_reasoning_event(
            provider="OpenAI metered lane",
            route=self.ROUTE_LABEL,
            analysis_profile="openclaw_task_report",
            prompt_text=prompt,
            response_text=text,
            model_label=model,
            request_id=request_id,
            exact_usage_available=usage["exact_usage_available"],
            exact_input_tokens=usage["input_tokens"],
            exact_output_tokens=usage["output_tokens"],
            exact_total_tokens=usage["total_tokens"],
            estimated_cost_usd=estimated_cost_usd,
        )
        return {
            "text": text,
            "usage_meta": self._usage_meta(
                model=model,
                task_label=task_label,
                usage=usage,
                estimated_cost_usd=estimated_cost_usd,
                usage_snapshot=usage_snapshot,
            ),
        }

    @classmethod
    def _extract_text(cls, payload: dict[str, Any]) -> str:
        direct = str(payload.get("output_text") or "").strip()
        if direct:
            return direct

        outputs = list(payload.get("output") or [])
        chunks: list[str] = []
        for item in outputs:
            if not isinstance(item, dict):
                continue
            for content in list(item.get("content") or []):
                if not isinstance(content, dict):
                    continue
                text_value = str(content.get("text") or content.get("output_text") or "").strip()
                if text_value:
                    chunks.append(text_value)
        if chunks:
            return "\n".join(chunks).strip()

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
        return ""

    @staticmethod
    def _extract_usage(payload: dict[str, Any]) -> dict[str, Any]:
        usage = dict(payload.get("usage") or {})
        input_tokens = int(usage.get("input_tokens") or usage.get("prompt_tokens") or 0)
        output_tokens = int(usage.get("output_tokens") or usage.get("completion_tokens") or 0)
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
    def _estimate_cost_usd(cls, *, model: str, input_tokens: int, output_tokens: int) -> float:
        pricing = cls.MODEL_PRICING_PER_MILLION.get(str(model or "").strip())
        if not pricing:
            return 0.0
        input_cost = (max(0, int(input_tokens)) / 1_000_000.0) * float(pricing["input"])
        output_cost = (max(0, int(output_tokens)) / 1_000_000.0) * float(pricing["output"])
        return round(input_cost + output_cost, 6)

    @staticmethod
    def _usage_meta(
        *,
        model: str,
        task_label: str,
        usage: dict[str, Any],
        estimated_cost_usd: float,
        usage_snapshot: dict[str, Any],
    ) -> dict[str, Any]:
        total_tokens = int(usage.get("total_tokens") or 0)
        measurement_label = "Exact tokens" if bool(usage.get("exact_usage_available")) else "Estimated tokens"
        token_phrase = (
            f"{total_tokens:,} exact tokens"
            if total_tokens > 0 and bool(usage.get("exact_usage_available"))
            else "metered usage recorded"
        )
        summary = (
            f"{task_label} used OpenAI {model}. "
            f"{token_phrase}. "
            f"Budget state: {str(usage_snapshot.get('budget_state_label') or 'Normal').strip()}."
        )
        if estimated_cost_usd > 0:
            summary = f"{summary} Estimated cost this run: ${estimated_cost_usd:.4f}."
        return {
            "route": "openai_metered",
            "route_label": "OpenAI metered lane",
            "provider_label": "OpenAI",
            "model_label": str(model or "").strip() or "OpenAI",
            "metered": True,
            "local_only": False,
            "measurement_label": measurement_label,
            "estimated_input_tokens": int(usage_snapshot.get("estimated_input_tokens") or 0),
            "estimated_output_tokens": int(usage_snapshot.get("estimated_output_tokens") or 0),
            "estimated_total_tokens": int(usage_snapshot.get("estimated_total_tokens") or 0),
            "exact_input_tokens": int(usage.get("input_tokens") or 0),
            "exact_output_tokens": int(usage.get("output_tokens") or 0),
            "exact_total_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost_usd,
            "budget_state": str(usage_snapshot.get("budget_state") or "normal").strip() or "normal",
            "budget_state_label": str(usage_snapshot.get("budget_state_label") or "Normal").strip() or "Normal",
            "summary": summary,
        }
