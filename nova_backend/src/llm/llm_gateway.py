from __future__ import annotations

import logging

from src.llm.llm_manager import llm_manager

logger = logging.getLogger(__name__)


def generate_chat(
    prompt: str,
    *,
    mode: str,
    safety_profile: str,
    request_id: str,
    session_id: str | None = None,
    system_prompt: str | None = None,
    max_tokens: int = 400,
    temperature: float = 0.3,
) -> str | None:
    """Centralized non-authorizing local model gateway (text in, text out)."""
    del mode, safety_profile

    try:
        response_text = llm_manager.generate(
            prompt,
            system_prompt=system_prompt or "",
            temperature=temperature,
            max_tokens=max_tokens,
            request_id=request_id,
            session_id=session_id,
        )
    except Exception as error:
        logger.error("LLM gateway call failed: %s", error)
        return None

    return (response_text or "").strip() or None
