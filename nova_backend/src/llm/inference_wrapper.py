# src/llm/inference_wrapper.py

"""
Low-level Ollama inference call.
Kept isolated so wrapper changes are hash-tracked by LLM version lock.
"""

from __future__ import annotations

from typing import Dict, Any

import requests

from .ilic import validate_and_lock_base_url


def run_inference(
    *,
    base_url: str,
    model: str,
    prompt: str,
    system: str,
    options: Dict[str, Any],
    timeout,
    allow_redirects: bool,
    trust_env: bool,
) -> str:
    """Execute a single local Ollama generate call and return text."""
    locked = validate_and_lock_base_url(base_url)

    session = requests.Session()
    session.trust_env = trust_env
    if not trust_env:
        session.proxies = {}

    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": options,
    }

    response = session.post(
        f"{locked.base_url}/api/generate",
        json=payload,
        timeout=timeout,
        allow_redirects=allow_redirects,
    )
    response.raise_for_status()

    body = response.json()
    return (body.get("response") or "").strip()
