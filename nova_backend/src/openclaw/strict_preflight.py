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
        "project_read",
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
    if any(tool in {"weather", "news"} for tool in tools) and not list(envelope.allowed_hostnames or []):
        violations.append("allowed_hostnames_missing")
    budget_checks = [
        ("max_steps", envelope.max_steps, MANUAL_FOUNDATION_MAX_STEPS),
        ("max_duration_s", envelope.max_duration_s, MANUAL_FOUNDATION_MAX_DURATION_S),
        ("max_network_calls", envelope.max_network_calls, MANUAL_FOUNDATION_MAX_NETWORK_CALLS),
        ("max_files_touched", envelope.max_files_touched, MANUAL_FOUNDATION_MAX_FILES_TOUCHED),
        ("max_bytes_read", envelope.max_bytes_read, MANUAL_FOUNDATION_MAX_BYTES_READ),
        ("max_bytes_written", envelope.max_bytes_written, MANUAL_FOUNDATION_MAX_BYTES_WRITTEN),
    ]
    for label, value, limit in budget_checks:
        if value is None or int(value) < 0:
            violations.append(f"{label}_invalid")
        elif label == "max_bytes_written" and int(value) > limit:
            violations.append("manual_foundation_disallows_writes")
        elif int(value) > limit:
            violations.append(f"{label}_exceeds_{limit}")
    triggered_by = str(envelope.triggered_by or "").strip()
    if not triggered_by:
        violations.append("trigger_missing")
    elif triggered_by not in MANUAL_FOUNDATION_ALLOWED_TRIGGERS:
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
