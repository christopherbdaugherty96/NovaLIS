from __future__ import annotations

import logging
from typing import Any


logger = logging.getLogger(__name__)


def generate_chat(
    prompt: str,
    *,
    mode: str,
    safety_profile: str,
    request_id: str,
    system_prompt: str | None = None,
    max_tokens: int = 400,
    temperature: float = 0.3,
) -> str | None:
    """Centralized non-authorizing local model gateway (text in, text out)."""
    del mode, safety_profile, request_id

    try:
        import ollama
    except Exception:
        return None

    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = ollama.chat(
            model="phi3:mini",
            messages=messages,
            options={"temperature": temperature, "num_predict": max_tokens},
        )
    except Exception as error:
        logger.error("LLM gateway call failed: %s", error)
        return None

    text = response.get("message", {}).get("content", "")
    return (text or "").strip() or None
