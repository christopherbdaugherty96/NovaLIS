"""Fail-closed initiation provenance for OpenClaw network tools.

OpenClaw currently has no independently validated, action-bound approval
artifact. Consequently this module deliberately cannot emit ``APPROVED``.
Adding such a path requires a separate authority integration that validates
the approval against the exact action before tool construction.
"""
from __future__ import annotations

from src.governor.disclosure_policy import InitiationClass

_MANUAL_TRIGGERS = frozenset({"agent_page", "dashboard", "manual", "user"})
_AUTOMATIC_TRIGGERS = frozenset({"scheduler", "scheduled"})


def classify_openclaw_initiation(triggered_by: str | None) -> InitiationClass:
    """Classify a run's origin without manufacturing approval.

    Unknown and legacy origins are treated as automatic. This is the safer
    classification because they do not carry independently validated evidence
    of a user's exact-action approval.
    """

    trigger = str(triggered_by or "").strip().lower()
    if trigger in _MANUAL_TRIGGERS:
        return InitiationClass.USER_INITIATED
    if trigger in _AUTOMATIC_TRIGGERS:
        return InitiationClass.AUTOMATIC
    return InitiationClass.AUTOMATIC
