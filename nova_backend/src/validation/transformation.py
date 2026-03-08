from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TransformationCheck:
    ok: bool
    reason: str = ""


class TransformationValidator:
    """Conservative check: presentation must preserve explicit factual lines."""

    def validate(self, raw_text: str, presented_text: str) -> TransformationCheck:
        raw_lines = [line.strip() for line in (raw_text or "").splitlines() if line.strip()]
        shown = (presented_text or "").strip().lower()
        for line in raw_lines[:8]:
            sample = line.lower()
            if len(sample) > 16 and sample not in shown:
                return TransformationCheck(False, "potential epistemic transformation detected")
        return TransformationCheck(True)
