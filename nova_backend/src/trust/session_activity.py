"""Deterministic, receipt-backed activity recap for one live Nova session.

This module is deliberately presentation-only.  It does not create authority,
execute capabilities, or invent action receipts.  Governed activity comes from
strictly correlated ledger receipts; unsupported requests are represented by
separate in-memory session facts with ``attempted=False``.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable, Mapping
from uuid import uuid4

from src.semantic.contracts import OutcomeSemantics, OutcomeState
from src.trust.receipt_store import get_session_action_receipts


class ActivityOrigin(str, Enum):
    """Trusted server-side classification for receipt provenance."""

    USER_ACTION = "user_action"
    BACKGROUND_READ = "background_read"


TRUSTED_ACTIVITY_ORIGIN_PARAM = "_nova_trusted_activity_origin"
TRUSTED_SESSION_ID_PARAM = "_nova_trusted_session_id"
_BACKGROUND_READ_COMMANDS: frozenset[str] = frozenset(
    {
        "awareness brief",
        "auralis today",
        "calendar",
        "calendar update",
        "current weather",
        "headlines",
        "latest news",
        "news",
        "system status",
        "top news",
        "weather",
        "weather update",
    }
)


def normalize_activity_origin(value: object) -> str:
    """Return an allowlisted activity origin, defaulting conservatively."""
    if isinstance(value, ActivityOrigin):
        return value.value
    normalized = str(value or "").strip().lower()
    if normalized == ActivityOrigin.BACKGROUND_READ.value:
        return ActivityOrigin.BACKGROUND_READ.value
    return ActivityOrigin.USER_ACTION.value


def activity_origin_for_request(
    *,
    silent_widget_refresh: bool,
    command_text: str,
) -> str:
    """Classify only allowlisted silent read surfaces as background activity."""
    normalized = " ".join(str(command_text or "").strip().lower().rstrip(".?!").split())
    if silent_widget_refresh and normalized in _BACKGROUND_READ_COMMANDS:
        return ActivityOrigin.BACKGROUND_READ.value
    return ActivityOrigin.USER_ACTION.value


def record_rejected_or_unsupported(
    session_state: dict[str, Any],
    *,
    label: str,
    reason: str,
) -> dict[str, Any]:
    """Record a non-receipt fact for a request that never entered execution."""
    fact = {
        "fact_id": f"session-fact-{uuid4()}",
        "session_id": str(session_state.get("session_id") or "").strip(),
        "activity_origin": ActivityOrigin.USER_ACTION.value,
        "classification": "rejected_or_unsupported",
        "attempted": False,
        "label": _clean_label(label, fallback="Unsupported request"),
        "reason": str(reason or "").strip()[:240],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    facts = [
        item
        for item in list(session_state.get("session_activity_facts") or [])
        if isinstance(item, dict)
    ]
    facts.append(fact)
    session_state["session_activity_facts"] = facts[-50:]
    return fact


def render_session_activity_recap(
    *,
    session_id: str,
    activity_facts: Iterable[Mapping[str, Any]] = (),
    receipts: Iterable[Mapping[str, Any]] | None = None,
) -> str:
    """Render only facts correlated to the exact current server session."""
    trusted_session_id = str(session_id or "").strip()
    if not trusted_session_id:
        return _empty_recap()

    source_receipts = (
        list(receipts)
        if receipts is not None
        else get_session_action_receipts(trusted_session_id)
    )
    items = correlate_action_receipts(
        source_receipts,
        session_id=trusted_session_id,
        require_trusted_correlation=True,
    )
    items.extend(_unsupported_activity_items(trusted_session_id, activity_facts))
    items.sort(key=lambda item: (str(item.get("timestamp_utc") or ""), str(item.get("stable_id") or "")))

    if not items:
        return _empty_recap()

    lines = ["What I can verify from current-session evidence:"]
    for item in items:
        lines.append(_render_item(item))
    lines.extend(
        [
            "",
            "Evidence boundary: I included only receipts and deterministic facts "
            "correlated to this session. I did not infer actions from the conversation transcript.",
        ]
    )
    return "\n".join(lines)


def correlate_action_receipts(
    receipts: Iterable[Mapping[str, Any]],
    *,
    session_id: str = "",
    require_trusted_correlation: bool = False,
) -> list[dict[str, Any]]:
    """Return one canonical outcome item per correlated action request.

    Strict session recaps require the server-issued session, request, and origin
    fields. Other read-only projections may also classify older receipt shapes;
    those rows remain isolated rather than being correlated by inference.
    """
    trusted_session_id = str(session_id or "").strip()
    grouped: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(reversed(list(receipts))):
        if not isinstance(raw, Mapping):
            continue
        receipt_session_id = str(raw.get("session_id") or "").strip()
        if trusted_session_id and receipt_session_id != trusted_session_id:
            continue
        request_id = str(raw.get("request_id") or "").strip()
        origin = str(raw.get("activity_origin") or "").strip().lower()
        event_type = str(raw.get("event_type") or "").strip()
        if event_type not in {"ACTION_ATTEMPTED", "ACTION_COMPLETED"}:
            continue
        trusted_origin = origin in {item.value for item in ActivityOrigin}
        if require_trusted_correlation and (not request_id or not trusted_origin):
            continue
        if not request_id:
            request_id = f"uncorrelated-{index}"
        if not trusted_origin:
            origin = ActivityOrigin.USER_ACTION.value
        normalized_receipt = dict(raw)
        normalized_receipt["activity_origin"] = origin
        group = grouped.setdefault(
            request_id,
            {
                "request_id": request_id,
                "receipts": [],
                "timestamp_utc": str(raw.get("timestamp_utc") or ""),
            },
        )
        group["receipts"].append(normalized_receipt)
        group["timestamp_utc"] = min(
            str(group.get("timestamp_utc") or str(raw.get("timestamp_utc") or "")),
            str(raw.get("timestamp_utc") or ""),
        )

    items: list[dict[str, Any]] = []
    for request_id, group in grouped.items():
        correlated = list(group.get("receipts") or [])
        attempted = next(
            (item for item in correlated if item.get("event_type") == "ACTION_ATTEMPTED"),
            None,
        )
        completed = next(
            (item for item in reversed(correlated) if item.get("event_type") == "ACTION_COMPLETED"),
            None,
        )
        origins = {
            str(item.get("activity_origin") or "").strip().lower()
            for item in correlated
        }
        try:
            capability_id = int(
                (completed or {}).get("capability_id")
                or (attempted or {}).get("capability_id")
                or 0
            )
        except (TypeError, ValueError):
            capability_id = 0
        capability_name = _clean_label(
            str((attempted or {}).get("capability_name") or ""),
            fallback=f"Capability {capability_id}" if capability_id else "Governed action",
        )
        source_label = str(
            (completed or {}).get("capability_name")
            or (attempted or {}).get("capability_name")
            or (f"Capability {capability_id}" if capability_id else "Governed action")
        ).strip()

        if len(origins) != 1:
            classification = "unknown_unverified"
            reason = "The correlated receipts disagree about activity origin."
            origin = ActivityOrigin.USER_ACTION.value
        else:
            origin = next(iter(origins))
            classification, reason = _classify_correlated_receipts(
                origin=origin,
                attempted=attempted,
                completed=completed,
            )

        items.append(
            {
                "stable_id": request_id,
                "timestamp_utc": str(group.get("timestamp_utc") or ""),
                "classification": classification,
                "label": capability_name,
                "source_label": source_label,
                "capability_id": capability_id,
                "activity_origin": origin,
                "reason": reason,
                "attempted": attempted is not None,
                "outcome_timestamp_utc": str(
                    (completed or attempted or {}).get("timestamp_utc") or ""
                ),
            }
        )
    return items


def _classify_correlated_receipts(
    *,
    origin: str,
    attempted: Mapping[str, Any] | None,
    completed: Mapping[str, Any] | None,
) -> tuple[str, str]:
    if completed is None:
        return (
            "unknown_unverified",
            "Execution was attempted, but no correlated completion receipt is available.",
        )

    raw_state = str(completed.get("outcome_state") or "").strip().lower()
    status = str(completed.get("status") or "").strip().lower()
    success = completed.get("success")
    if (
        origin == ActivityOrigin.BACKGROUND_READ.value
        and success is True
        and status == "completed"
        and not raw_state
    ):
        return "background_read", ""

    semantics = OutcomeSemantics.from_action_metadata(completed)
    reason = str(semantics.reason or "").strip()
    if semantics.state is OutcomeState.EFFECT_VERIFIED:
        return "effect_verified", reason
    if semantics.state is OutcomeState.ACCEPTED_UNVERIFIED:
        return "accepted_unverified", reason
    if semantics.state in {OutcomeState.FAILED, OutcomeState.PARTIAL_FAILURE}:
        return "failed", reason
    if semantics.state is OutcomeState.REJECTED:
        return "rejected_or_unsupported", reason

    return "unknown_unverified", reason


def _unsupported_activity_items(
    session_id: str,
    facts: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for fact in facts:
        if not isinstance(fact, Mapping):
            continue
        if str(fact.get("session_id") or "").strip() != session_id:
            continue
        if str(fact.get("classification") or "") != "rejected_or_unsupported":
            continue
        if fact.get("attempted") is not False:
            continue
        fact_id = str(fact.get("fact_id") or "").strip()
        if not fact_id:
            continue
        items.append(
            {
                "stable_id": fact_id,
                "timestamp_utc": str(fact.get("timestamp_utc") or ""),
                "classification": "rejected_or_unsupported",
                "label": _clean_label(
                    str(fact.get("label") or ""),
                    fallback="Unsupported request",
                ),
                "capability_id": 0,
                "activity_origin": ActivityOrigin.USER_ACTION.value,
                "reason": str(fact.get("reason") or "").strip(),
                "attempted": False,
            }
        )
    return items


def _render_item(item: Mapping[str, Any]) -> str:
    classification = str(item.get("classification") or "unknown_unverified")
    label = str(item.get("label") or "Governed action")
    capability_id = int(item.get("capability_id") or 0)
    capability_suffix = f" (Cap {capability_id})" if capability_id else ""
    reason = str(item.get("reason") or "").strip()

    messages = {
        "background_read": "background read completed; no external change is claimed",
        "effect_verified": "effect verified by recorded outcome evidence",
        "accepted_unverified": "request accepted; visible effect was not verified",
        "failed": "failed",
        "unknown_unverified": "outcome unknown or unverified",
        "rejected_or_unsupported": "rejected or unsupported; no action was attempted",
    }
    message = messages.get(classification, messages["unknown_unverified"])
    if reason and classification in {"failed", "unknown_unverified", "rejected_or_unsupported"}:
        message = f"{message} ({reason})"
    return f"- {label}{capability_suffix}: {message}."


def _clean_label(value: str, *, fallback: str) -> str:
    cleaned = " ".join(str(value or "").replace("_", " ").split()).strip()
    if not cleaned:
        return fallback
    return cleaned[0].upper() + cleaned[1:]


def _empty_recap() -> str:
    return (
        "I do not have correlated action evidence for this session. "
        "I will not infer actions from the conversation transcript."
    )
