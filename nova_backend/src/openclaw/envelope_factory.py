"""
Authority Rank: 1 (co-equal with GovernorMediator) — Envelope Issuer
Role: The sole authorized constructor of TaskEnvelopes. Every OpenClaw run
      must originate from a Nova-issued envelope produced here. Holds no
      instance state — all persisted state lives in EnvelopeStore.
Superseded by: Nothing. This is the supreme issuance authority.

Feature flag: NOVA_FEATURE_ENVELOPE_FACTORY=true activates the issuance path.
When false (default), the legacy direct-construction path in agent_runner.py
remains in effect. Both paths log to the ledger during the transition period.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from src.openclaw.task_envelope import TaskEnvelope


_FEATURE_FLAG_ENV = "NOVA_FEATURE_ENVELOPE_FACTORY"
_DEFAULT_TTL_SECONDS = 300  # 5 minutes


def _feature_enabled() -> bool:
    return os.getenv(_FEATURE_FLAG_ENV, "").strip().lower() in {"1", "true", "yes"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _sha256_snapshot(data: dict[str, Any]) -> str:
    try:
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()
    except Exception:
        return "hash_unavailable"


@dataclass
class IssuedEnvelope:
    """
    The result of a successful EnvelopeFactory.issue() call.
    Carries both the runnable TaskEnvelope and the immutable authority snapshot
    that will be written to the ledger and stored in EnvelopeStore.
    """
    envelope_id: UUID
    envelope: TaskEnvelope
    issuing_channel: str            # "manual", "scheduler", "bridge"
    settings_hash: str              # SHA-256 of relevant settings subset at issuance time
    feature_flags_snapshot: dict[str, bool]
    issued_at: datetime
    expires_at: datetime
    ledger_event: dict[str, Any] = field(default_factory=dict)


class EnvelopeFactoryError(RuntimeError):
    """Raised when the factory refuses to issue an envelope."""


class EnvelopeFactory:
    """
    Stateless envelope constructor.

    Accepted by: agent_runner.py (manual), agent_scheduler.py (scheduler),
    bridge_api.py (bridge).

    Each channel passes its own context; the factory applies the correct
    restrictions and produces a single canonical TaskEnvelope with a
    persistent IssuedEnvelope record.

    Call issue() to get an IssuedEnvelope. Then pass the envelope to
    EnvelopeStore.register() to persist the lifecycle record before running.
    """

    # Channels with their allowed trigger labels
    _CHANNEL_TRIGGERS: dict[str, frozenset[str]] = {
        "manual": frozenset({"agent_page", "dashboard", "user", "test"}),
        "scheduler": frozenset({"scheduler"}),
        "bridge": frozenset({"bridge"}),
    }

    def __init__(
        self,
        *,
        runtime_settings: Any = None,
    ) -> None:
        self._runtime_settings = runtime_settings

    def issue(
        self,
        *,
        template: dict[str, Any],
        channel: str,
        triggered_by: str,
        ttl_seconds: int = _DEFAULT_TTL_SECONDS,
    ) -> IssuedEnvelope:
        """
        Produce a governed TaskEnvelope from a template definition.

        Raises EnvelopeFactoryError if:
        - feature flag is off (caller should fall back to legacy path)
        - home_agent_enabled=False in runtime settings
        - channel is unrecognised
        - triggered_by is not valid for the channel
        - template is missing required fields
        """
        if not _feature_enabled():
            raise EnvelopeFactoryError(
                f"{_FEATURE_FLAG_ENV} is not enabled — use the legacy direct-construction path."
            )

        self._check_home_agent_enabled()
        channel = self._validate_channel(channel)
        triggered_by = self._validate_trigger(channel, triggered_by)
        self._validate_template(template)

        envelope = TaskEnvelope.from_template(template, triggered_by=triggered_by)
        envelope_id = uuid4()
        now = _utc_now()
        expires_at = now + timedelta(seconds=max(60, int(ttl_seconds)))
        settings_hash = self._settings_hash()
        flags = self._feature_flags_snapshot()

        ledger_event = {
            "event_type": "OPENCLAW_RUN_ISSUED",
            "envelope_id": str(envelope_id),
            "template_id": str(template.get("id") or "").strip(),
            "channel": channel,
            "triggered_by": triggered_by,
            "issued_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
            "settings_hash": settings_hash,
            "feature_flags": flags,
            "scope_summary": envelope.scope_summary(),
            "budget_summary": envelope.budget_summary(),
        }

        return IssuedEnvelope(
            envelope_id=envelope_id,
            envelope=envelope,
            issuing_channel=channel,
            settings_hash=settings_hash,
            feature_flags_snapshot=flags,
            issued_at=now,
            expires_at=expires_at,
            ledger_event=ledger_event,
        )

    # ------------------------------------------------------------------
    # Internal checks
    # ------------------------------------------------------------------

    def _check_home_agent_enabled(self) -> None:
        if self._runtime_settings is None:
            return
        try:
            enabled = self._runtime_settings.is_permission_enabled("home_agent_enabled")
        except Exception:
            return
        if not enabled:
            raise EnvelopeFactoryError(
                "home_agent_enabled is off in runtime settings — envelope issuance refused."
            )

    def _validate_channel(self, channel: str) -> str:
        channel = str(channel or "").strip().lower()
        if channel not in self._CHANNEL_TRIGGERS:
            raise EnvelopeFactoryError(
                f"Unknown channel '{channel}'. Must be one of: {sorted(self._CHANNEL_TRIGGERS)}."
            )
        return channel

    def _validate_trigger(self, channel: str, triggered_by: str) -> str:
        triggered_by = str(triggered_by or "").strip()
        allowed = self._CHANNEL_TRIGGERS[channel]
        if triggered_by not in allowed:
            raise EnvelopeFactoryError(
                f"triggered_by='{triggered_by}' is not valid for channel '{channel}'. "
                f"Allowed: {sorted(allowed)}."
            )
        return triggered_by

    def _validate_template(self, template: dict[str, Any]) -> None:
        template_id = str(template.get("id") or "").strip()
        title = str(template.get("title") or "").strip()
        if not template_id:
            raise EnvelopeFactoryError("Template is missing required field 'id'.")
        if not title:
            raise EnvelopeFactoryError(f"Template '{template_id}' is missing required field 'title'.")

    def _settings_hash(self) -> str:
        if self._runtime_settings is None:
            return _sha256_snapshot({})
        try:
            relevant = {
                "home_agent_enabled": self._runtime_settings.is_permission_enabled("home_agent_enabled"),
                "home_agent_scheduler_enabled": self._runtime_settings.is_permission_enabled(
                    "home_agent_scheduler_enabled"
                ),
            }
        except Exception:
            relevant = {}
        return _sha256_snapshot(relevant)

    def _feature_flags_snapshot(self) -> dict[str, bool]:
        return {
            _FEATURE_FLAG_ENV: _feature_enabled(),
        }
