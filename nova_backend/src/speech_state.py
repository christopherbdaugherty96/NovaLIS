"""
Speech State - Phase-2+

Single source of truth for recent spoken output and the latest runtime
speech attempt metadata.

IMPORTANT:
- Stores output only (what Nova said)
- Stores lightweight runtime metadata for inspectability
- Does NOT infer intent
- Does NOT trigger behavior
- Does NOT persist to disk
"""

from datetime import datetime, timezone
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
        self.last_engine: str = ""
        self.last_attempt_status: str = "idle"
        self.last_error: str = ""
        self.last_attempt_at: str = ""

    def record_attempt(
        self,
        *,
        engine: str,
        status: str,
        error: str = "",
        spoken_text: str | None = None,
    ) -> None:
        self.last_engine = str(engine or "").strip()
        self.last_attempt_status = str(status or "idle").strip()
        self.last_error = str(error or "").strip()
        self.last_attempt_at = datetime.now(timezone.utc).isoformat()
        if spoken_text is not None:
            self.last_spoken_text = str(spoken_text or "").strip() or None

    def stop(self) -> None:
        """
        Clear the last spoken text.

        Internal state reset only.
        """
        self.last_spoken_text = None
        self.last_attempt_status = "stopped"
        self.last_error = ""
        self.last_attempt_at = datetime.now(timezone.utc).isoformat()

    def snapshot(self) -> dict[str, str]:
        return {
            "last_spoken_text": str(self.last_spoken_text or ""),
            "last_engine": self.last_engine,
            "last_attempt_status": self.last_attempt_status,
            "last_error": self.last_error,
            "last_attempt_at": self.last_attempt_at,
        }


# ------------------------------------------------------------
# Singleton instance (imported by brain_server)
# ------------------------------------------------------------

speech_state = SpeechState()
