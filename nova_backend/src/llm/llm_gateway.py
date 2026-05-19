from __future__ import annotations

import logging
from typing import Callable, Generator

from src.llm.llm_manager import llm_manager

logger = logging.getLogger(__name__)


def is_model_update_pending() -> bool:
    """Return whether inference is blocked pending explicit model confirmation."""
    return bool(getattr(llm_manager, "inference_blocked", False))


def confirm_model_update() -> bool:
    """Confirm a pending model update and return True when unblocked."""
    was_blocked = bool(getattr(llm_manager, "inference_blocked", False))
    llm_manager.confirm_model_update()
    return was_blocked and not bool(getattr(llm_manager, "inference_blocked", False))


def model_status_snapshot() -> dict:
    """Return current model status for diagnostics (active/fallback/blocked)."""
    return llm_manager.status_snapshot()


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
    timeout: float | None = None,
    on_chunk: Callable[[str], None] | None = None,
) -> str | None:
    """Centralized non-authorizing local model gateway (text in, text out).

    If *on_chunk* is provided, streams tokens through the callback
    for early UX delivery while still returning the complete text.
    """
    del mode, safety_profile

    try:
        response_text = llm_manager.generate(
            prompt,
            system_prompt=system_prompt or "",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            request_id=request_id,
            session_id=session_id,
            on_chunk=on_chunk,
        )
    except Exception as error:
        logger.error("LLM gateway call failed: %s", error)
        return None

    return (response_text or "").strip() or None


def generate_chat_stream(
    prompt: str,
    *,
    mode: str,
    safety_profile: str,
    request_id: str,
    session_id: str | None = None,
    system_prompt: str | None = None,
    max_tokens: int = 400,
    temperature: float = 0.3,
    timeout: float | None = None,
) -> Generator[str, None, None]:
    """Streaming variant of generate_chat for advisory LLM fallback.

    Yields text chunks as they arrive from Ollama. Non-authorizing:
    same gateway boundary as generate_chat.
    """
    del mode, safety_profile

    try:
        yield from llm_manager.generate_stream(
            prompt,
            system_prompt=system_prompt or "",
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            request_id=request_id,
            session_id=session_id,
        )
    except Exception as error:
        logger.error("LLM gateway stream call failed: %s", error)
        return
