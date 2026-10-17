from __future__ import annotations

import re
from dataclasses import dataclass

_RECEIPT_HEADER_RE = re.compile(
    r"^(?:summary:\s*)?(?:reminder\s+saved\s*:\s*sch-|saved\.\s*memory\s+mem-)",
    re.IGNORECASE,
)
_RECEIPT_ID_RE = re.compile(r"\b(?:SCH|MEM)-[A-Z0-9][A-Z0-9_-]*\b", re.IGNORECASE)
_RECEIPT_CONFIRMATION_RE = re.compile(
    r"\b(?:receipt|reminder|memory|saved|created|requested\s+for)\b",
    re.IGNORECASE,
)
_RECEIPT_DETAIL_RE = re.compile(
    r"^(?:text|requested\s+for|tier|scope|source|receipt)\s*:",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ExecutionReceipt:
    """Trusted marker constructed by deterministic execution call sites only."""

    kind: str
    id: str

    def as_payload(self) -> dict[str, str]:
        expected_prefix = {"reminder": "SCH-", "memory": "MEM-"}.get(self.kind)
        if expected_prefix is None or not self.id.startswith(expected_prefix):
            raise ValueError("Execution receipt kind and identifier do not match.")
        return {"kind": self.kind, "id": self.id}


def neutralize_model_receipt_text(message: str) -> tuple[str, bool]:
    """Remove execution-receipt shapes from untrusted model text."""
    clean = str(message or "").strip()
    lines = clean.splitlines()
    receipt_shaped = any(_RECEIPT_HEADER_RE.search(line.strip()) for line in lines)
    if not receipt_shaped:
        receipt_shaped = any(
            _RECEIPT_ID_RE.search(line) and _RECEIPT_CONFIRMATION_RE.search(line)
            for line in lines
        )
    if not receipt_shaped:
        return clean, False

    kept: list[str] = []
    for line in lines:
        stripped = line.strip()
        if _RECEIPT_HEADER_RE.search(stripped):
            continue
        if _RECEIPT_ID_RE.search(stripped):
            continue
        if _RECEIPT_DETAIL_RE.search(stripped):
            continue
        kept.append(line)

    neutralized = "\n".join(kept).strip()
    if not neutralized:
        neutralized = "I removed an unverified action receipt from the model response."
    return neutralized, True
