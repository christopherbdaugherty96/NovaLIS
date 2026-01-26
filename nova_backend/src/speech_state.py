"""
Speech State — Phase-2

Single source of truth for the last spoken text.

IMPORTANT:
- Stores output only (what Nova said)
- Does NOT infer intent
- Does NOT trigger behavior
- Does NOT persist to disk
"""

from typing import Optional


class SpeechState:
    """
    In-memory speech tracking.

    Used exclusively to support:
    - "repeat"
    - "what did you say?"

    This object is intentionally simple.
    """

    def __init__(self) -> None:
        self.last_spoken_text: Optional[str] = None


# ------------------------------------------------------------
# Singleton instance (imported by brain_server)
# ------------------------------------------------------------

speech_state = SpeechState()
