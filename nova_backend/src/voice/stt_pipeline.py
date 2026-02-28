from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class STTAckConfig:
    enabled: bool = True
    text: str = "Got it."


def build_ack_payload(config: STTAckConfig) -> dict | None:
    """Build a lightweight acknowledgement payload for STT interactions."""
    if not config.enabled:
        return None
    return {"type": "ack", "message": config.text}
