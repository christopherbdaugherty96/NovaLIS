from __future__ import annotations

import re
from enum import Enum


class PersonalOperationsIntent(str, Enum):
    """Private-state questions recognized without granting execution authority."""

    MATTERS_TODAY = "matters_today"
    NEXT = "next"
    CHANGED = "changed"
    WAITING_ON = "waiting_on"
    NEED_TO_FINISH = "need_to_finish"
    RECOMMENDED_NEXT = "recommended_next"
    COMPLETED_TODAY = "completed_today"


_PATTERNS: tuple[tuple[re.Pattern[str], PersonalOperationsIntent], ...] = (
    (re.compile(r"^what matters today$", re.IGNORECASE), PersonalOperationsIntent.MATTERS_TODAY),
    (re.compile(r"^what do i have next$", re.IGNORECASE), PersonalOperationsIntent.NEXT),
    (re.compile(r"^what changed$", re.IGNORECASE), PersonalOperationsIntent.CHANGED),
    (re.compile(r"^what am i waiting on$", re.IGNORECASE), PersonalOperationsIntent.WAITING_ON),
    (
        re.compile(r"^what did i (?:say i )?need(?:ed)? to finish$", re.IGNORECASE),
        PersonalOperationsIntent.NEED_TO_FINISH,
    ),
    (re.compile(r"^what should i do next$", re.IGNORECASE), PersonalOperationsIntent.RECOMMENDED_NEXT),
    (re.compile(r"^what did i finish today$", re.IGNORECASE), PersonalOperationsIntent.COMPLETED_TODAY),
)


def resolve_personal_operations_intent(text: str) -> PersonalOperationsIntent | None:
    """Return a typed private-state intent for the bounded beta vocabulary."""

    canonical = " ".join((text or "").strip().rstrip(".?!").split())
    for pattern, intent in _PATTERNS:
        if pattern.fullmatch(canonical):
            return intent
    return None


def unavailable_personal_operations_response(intent: PersonalOperationsIntent) -> str:
    """Fail closed while the beta has no assembled personal-operations state."""

    subject = {
        PersonalOperationsIntent.MATTERS_TODAY: "what matters today",
        PersonalOperationsIntent.NEXT: "what you have next",
        PersonalOperationsIntent.CHANGED: "what changed",
        PersonalOperationsIntent.WAITING_ON: "what you're waiting on",
        PersonalOperationsIntent.NEED_TO_FINISH: "what you needed to finish",
        PersonalOperationsIntent.RECOMMENDED_NEXT: "what you should do next",
        PersonalOperationsIntent.COMPLETED_TODAY: "what you finished today",
    }[intent]
    return (
        f"I recognize this as a private personal-operations question about {subject}, "
        "but I don't have assembled private state for it yet. "
        "I did not search the public web or run another capability."
    )
