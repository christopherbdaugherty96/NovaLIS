from __future__ import annotations

from dataclasses import asdict, dataclass

from src.openclaw.task_envelope import TaskEnvelope


STRICT_FOUNDATION_LABEL = "Manual preflight active"
STRICT_FOUNDATION_SUMMARY = (
    "Every manual home-agent envelope is checked against the current strict "
    "manual tool and budget limits before collection begins."
)
MANUAL_FOUNDATION_ALLOWED_TOOLS = frozenset(
    {
        "calendar",
        "news",
        "schedules",
        "summarize",
        "weather",
    }
)
MANUAL_FOUNDATION_MAX_STEPS = 8
MANUAL_FOUNDATION_MAX_DURATION_S = 120
MANUAL_FOUNDATION_MAX_NETWORK_CALLS = 12
MANUAL_FOUNDATION_MAX_FILES_TOUCHED = 2
MANUAL_FOUNDATION_MAX_BYTES_READ = 2_000_000
MANUAL_FOUNDATION_MAX_BYTES_WRITTEN = 0
MANUAL_FOUNDATION_ALLOWED_TRIGGERS = frozenset({"agent_page", "dashboard", "scheduler", "test", "user"})


@dataclass(frozen=True)
class StrictPreflightDecision:
    allowed: bool
    mode: str
    reason: str
    violations: list[str]
    allowed_tools: list[str]
    max_steps: int
    max_duration_s: int
    max_network_calls: int
    max_files_touched: int
    max_bytes_read: int
    max_bytes_written: int
    allowed_triggers: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def strict_foundation_snapshot() -> dict[str, object]:
    return {
        "status": "active",
        "label": STRICT_FOUNDATION_LABEL,
        "summary": STRICT_FOUNDATION_SUMMARY,
        "allowed_tools": sorted(MANUAL_FOUNDATION_ALLOWED_TOOLS),
        "max_steps": MANUAL_FOUNDATION_MAX_STEPS,
        "max_duration_s": MANUAL_FOUNDATION_MAX_DURATION_S,
        "max_network_calls": MANUAL_FOUNDATION_MAX_NETWORK_CALLS,
        "max_files_touched": MANUAL_FOUNDATION_MAX_FILES_TOUCHED,
        "max_bytes_read": MANUAL_FOUNDATION_MAX_BYTES_READ,
        "max_bytes_written": MANUAL_FOUNDATION_MAX_BYTES_WRITTEN,
        "allowed_triggers": sorted(MANUAL_FOUNDATION_ALLOWED_TRIGGERS),
    }


def evaluate_manual_envelope(envelope: TaskEnvelope) -> StrictPreflightDecision:
    violations: list[str] = []
    template_id = str(envelope.template_id or "").strip()
    title = str(envelope.title or "").strip()
    tools = [str(item).strip() for item in list(envelope.tools_allowed or []) if str(item).strip()]
    unsupported_tools = [tool for tool in tools if tool not in MANUAL_FOUNDATION_ALLOWED_TOOLS]
    if not template_id:
        violations.append("template_missing")
    if not title:
        violations.append("title_missing")
    if not tools:
        violations.append("tools_missing")
    if unsupported_tools:
        violations.append("unsupported_tools:" + ", ".join(sorted(unsupported_tools)))
    if int(envelope.max_steps or 0) > MANUAL_FOUNDATION_MAX_STEPS:
        violations.append(f"max_steps_exceeds_{MANUAL_FOUNDATION_MAX_STEPS}")
    if int(envelope.max_duration_s or 0) > MANUAL_FOUNDATION_MAX_DURATION_S:
        violations.append(f"max_duration_exceeds_{MANUAL_FOUNDATION_MAX_DURATION_S}")
    if int(envelope.max_network_calls or 0) > MANUAL_FOUNDATION_MAX_NETWORK_CALLS:
        violations.append(f"max_network_calls_exceeds_{MANUAL_FOUNDATION_MAX_NETWORK_CALLS}")
    if int(envelope.max_files_touched or 0) > MANUAL_FOUNDATION_MAX_FILES_TOUCHED:
        violations.append("manual_foundation_disallows_file_touch")
    if int(envelope.max_bytes_read or 0) > MANUAL_FOUNDATION_MAX_BYTES_READ:
        violations.append(f"max_bytes_read_exceeds_{MANUAL_FOUNDATION_MAX_BYTES_READ}")
    if int(envelope.max_bytes_written or 0) > MANUAL_FOUNDATION_MAX_BYTES_WRITTEN:
        violations.append("manual_foundation_disallows_writes")
    if str(envelope.triggered_by or "").strip() not in MANUAL_FOUNDATION_ALLOWED_TRIGGERS:
        violations.append("trigger_not_allowed")

    reason = "Manual envelope accepted by strict home-agent preflight."
    if violations:
        reason = "Manual envelope blocked by strict home-agent preflight: " + "; ".join(violations)

    return StrictPreflightDecision(
        allowed=not violations,
        mode="manual_foundation",
        reason=reason,
        violations=violations,
        allowed_tools=sorted(MANUAL_FOUNDATION_ALLOWED_TOOLS),
        max_steps=MANUAL_FOUNDATION_MAX_STEPS,
        max_duration_s=MANUAL_FOUNDATION_MAX_DURATION_S,
        max_network_calls=MANUAL_FOUNDATION_MAX_NETWORK_CALLS,
        max_files_touched=MANUAL_FOUNDATION_MAX_FILES_TOUCHED,
        max_bytes_read=MANUAL_FOUNDATION_MAX_BYTES_READ,
        max_bytes_written=MANUAL_FOUNDATION_MAX_BYTES_WRITTEN,
        allowed_triggers=sorted(MANUAL_FOUNDATION_ALLOWED_TRIGGERS),
    )
