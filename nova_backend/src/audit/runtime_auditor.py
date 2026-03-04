from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.governor.execute_boundary.execute_boundary import GOVERNED_ACTIONS_ENABLED
from src.governor.governor_mediator import GovernorMediator, Invocation


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = PROJECT_ROOT / "src" / "config" / "registry.json"
RUNTIME_DOC_PATH = PROJECT_ROOT.parent / "docs" / "runtime" / "CURRENT_RUNTIME_STATE.md"
CANONICAL_RUNTIME_DOC_PATH = PROJECT_ROOT.parent / "docs" / "CANONICAL" / "PHASE_4_RUNTIME_TRUTH.md"
DEEPSEEK_BRIDGE_PATH = PROJECT_ROOT / "src" / "conversation" / "deepseek_bridge.py"
LLM_MANAGER_PATH = PROJECT_ROOT / "src" / "llm" / "llm_manager.py"

# Read-only allowlist for v1 auditor scope.
ALLOWED_READ_PATHS = (
    REGISTRY_PATH,
    RUNTIME_DOC_PATH,
    CANONICAL_RUNTIME_DOC_PATH,
    DEEPSEEK_BRIDGE_PATH,
    LLM_MANAGER_PATH,
)

# Minimal explicit phrase probes used to map mediator surfaces.
MEDIATOR_TRIGGER_PROBES: dict[str, str] = {
    "search for weather in ann arbor": "search",
    "look up nasa": "search",
    "research battery technology": "search",
    "open github": "open_website",
    "open documents": "open_folder",
    "speak that": "speak",
    "read that": "speak",
    "say it": "speak",
    "volume up": "volume",
    "volume down": "volume",
    "set volume 45": "volume",
    "play": "media",
    "pause": "media",
    "resume": "media",
    "brightness up": "brightness",
    "brightness down": "brightness",
    "set brightness 50": "brightness",
    "system check": "diagnostics",
    "system status": "diagnostics",
    "report market update": "report",
    "summarize ai safety": "report",
}


@dataclass(frozen=True)
class Discrepancy:
    severity: str  # hard_fail | warning
    code: str
    message: str
    details: dict[str, Any]


def _safe_read(path: Path) -> str:
    if path not in ALLOWED_READ_PATHS:
        raise ValueError(f"Path not allowlisted for auditor: {path}")
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _load_registry() -> dict[str, Any]:
    raw = _safe_read(REGISTRY_PATH)
    if not raw:
        return {"schema_version": None, "phase": None, "capabilities": []}
    return json.loads(raw)


def _enabled_registry_ids(registry: dict[str, Any]) -> list[int]:
    ids = [int(item["id"]) for item in registry.get("capabilities", []) if item.get("enabled") is True]
    return sorted(ids)


def _extract_enabled_ids_from_markdown(markdown_text: str) -> list[int]:
    """Best-effort extraction for lines like: `- 16: enabled` or table rows containing enabled=true."""
    if not markdown_text:
        return []

    found: set[int] = set()

    for line in markdown_text.splitlines():
        lower = line.lower()

        bullet_match = re.search(r"\b(\d+)\b\s*[:\-|]\s*.*\benabled\b", lower)
        if bullet_match:
            found.add(int(bullet_match.group(1)))
            continue

 
        table_match = re.search(r"^\|\s*(\d+)\s*\|\s*[^|]+\|\s*(enabled|true)\s*\|", lower)

        table_match = re.search(r"\|\s*(\d+)\s*\|.*\|\s*(true|enabled)\s*\|", lower)
        origin/main
        if table_match:
            found.add(int(table_match.group(1)))
            continue

    return sorted(found)


def _mediator_surface_map() -> dict[str, Any]:
    entries = []
    capability_ids = set()

    for phrase, group in MEDIATOR_TRIGGER_PROBES.items():
        parsed = GovernorMediator.parse_governed_invocation(phrase, session_id="audit-runtime")
        cap_id = parsed.capability_id if isinstance(parsed, Invocation) else None
        if cap_id is not None:
            capability_ids.add(cap_id)
        entries.append(
            {
                "probe": phrase,
                "group": group,
                "capability_id": cap_id,
                "matched": cap_id is not None,
            }
        )

    return {
        "probes": entries,
        "mapped_capability_ids": sorted(capability_ids),
    }


def _detect_direct_model_call_bypass() -> dict[str, Any]:
    deepseek_src = _safe_read(DEEPSEEK_BRIDGE_PATH)
    llm_manager_src = _safe_read(LLM_MANAGER_PATH)

    return {
        "deepseek_uses_ollama_chat_directly": "ollama.chat(" in deepseek_src,
        "llm_manager_generate_present": "def generate(" in llm_manager_src,
    }


def _derive_status(hard_fail_count: int, warning_count: int) -> str:
    if hard_fail_count > 0:
        return "fail"
    if warning_count > 0:
        return "warn"
    return "pass"


def _build_discrepancies(
    runtime_doc_enabled_ids: list[int],
    registry_enabled_ids: list[int],
    mediator_mapped_ids: list[int],
    model_path_signals: dict[str, Any],
    execution_gate_enabled: bool,
) -> list[Discrepancy]:
    discrepancies: list[Discrepancy] = []

    runtime_doc_set = set(runtime_doc_enabled_ids)
    registry_enabled_set = set(registry_enabled_ids)
    mediator_mapped_set = set(mediator_mapped_ids)

    if runtime_doc_set != registry_enabled_set:
        discrepancies.append(
            Discrepancy(
                severity="hard_fail",
                code="ENABLED_ID_SET_MISMATCH",
                message="Enabled capability ID set differs between docs/runtime/CURRENT_RUNTIME_STATE.md and registry.json.",
                details={
                    "registry_enabled_ids": sorted(registry_enabled_set),
                    "doc_enabled_ids": sorted(runtime_doc_set),
                    "missing_in_doc": sorted(registry_enabled_set - runtime_doc_set),
                    "extra_in_doc": sorted(runtime_doc_set - registry_enabled_set),
                },
            )
        )

    missing_mediator_routes = sorted(registry_enabled_set - mediator_mapped_set)
    if missing_mediator_routes:
        discrepancies.append(
            Discrepancy(
                severity="hard_fail",
                code="ENABLED_CAPABILITY_MISSING_MEDIATOR_ROUTE",
                message="One or more enabled capabilities are not matched by known mediator routes.",
                details={"missing_capability_ids": missing_mediator_routes},
            )
        )

    disabled_but_routable = sorted(mediator_mapped_set - registry_enabled_set)
    if disabled_but_routable:
        discrepancies.append(
            Discrepancy(
                severity="warning",
                code="MEDIATOR_ROUTES_TO_DISABLED_CAPABILITY",
                message="Mediator routes include capabilities that are currently disabled in registry.",
                details={"disabled_or_non_enabled_capability_ids": disabled_but_routable},
            )
        )

    if not execution_gate_enabled:
        discrepancies.append(
            Discrepancy(
                severity="warning",
                code="EXECUTION_GATE_DISABLED",
                message="Global execution gate is disabled (GOVERNED_ACTIONS_ENABLED=False).",
                details={"governed_actions_enabled": execution_gate_enabled},
            )
        )

    if not RUNTIME_DOC_PATH.exists():
        discrepancies.append(
            Discrepancy(
                severity="warning",
                code="RUNTIME_DOC_MISSING",
                message="docs/runtime/CURRENT_RUNTIME_STATE.md is missing.",
                details={"path": str(RUNTIME_DOC_PATH.relative_to(PROJECT_ROOT.parent))},
            )
        )

    if model_path_signals.get("deepseek_uses_ollama_chat_directly"):
        discrepancies.append(
            Discrepancy(
                severity="warning",
                code="DIRECT_MODEL_CALL_BYPASS",
                message="DeepSeekBridge appears to call ollama.chat directly instead of a centralized LLM gateway.",
                details={"path": str(DEEPSEEK_BRIDGE_PATH.relative_to(PROJECT_ROOT))},
            )
        )

    return discrepancies


def run_runtime_truth_audit() -> dict[str, Any]:
    registry = _load_registry()
    registry_enabled_ids = _enabled_registry_ids(registry)

    runtime_doc_text = _safe_read(RUNTIME_DOC_PATH)
    runtime_doc_enabled_ids = _extract_enabled_ids_from_markdown(runtime_doc_text)

    mediator_map = _mediator_surface_map()
    mediator_mapped_ids = mediator_map["mapped_capability_ids"]
    model_signals = _detect_direct_model_call_bypass()
    execution_gate_enabled = bool(GOVERNED_ACTIONS_ENABLED)

    discrepancies = _build_discrepancies(
        runtime_doc_enabled_ids=runtime_doc_enabled_ids,
        registry_enabled_ids=registry_enabled_ids,
        mediator_mapped_ids=mediator_mapped_ids,
        model_path_signals=model_signals,
        execution_gate_enabled=execution_gate_enabled,
    )

    hard_fail_count = sum(1 for item in discrepancies if item.severity == "hard_fail")
    warning_count = sum(1 for item in discrepancies if item.severity == "warning")

    status = _derive_status(hard_fail_count=hard_fail_count, warning_count=warning_count)

    return {
        "auditor": "runtime_truth_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "summary": {
            "hard_fail_count": hard_fail_count,
            "warning_count": warning_count,
            "registry_enabled_ids": registry_enabled_ids,
            "runtime_doc_enabled_ids": runtime_doc_enabled_ids,
            "mediator_mapped_capability_ids": mediator_mapped_ids,
            "execution_gate_enabled": execution_gate_enabled,
        },
        "inputs": {
            "allowlisted_paths": [str(path.relative_to(PROJECT_ROOT.parent)) for path in ALLOWED_READ_PATHS],
            "registry_path": str(REGISTRY_PATH.relative_to(PROJECT_ROOT.parent)),
            "runtime_doc_path": str(RUNTIME_DOC_PATH.relative_to(PROJECT_ROOT.parent)),
            "canonical_runtime_doc_path": str(CANONICAL_RUNTIME_DOC_PATH.relative_to(PROJECT_ROOT.parent)),
        },
        "checks": {
            "model_path_signals": model_signals,
            "mediator_surface": mediator_map,
        },
        "discrepancies": [asdict(item) for item in discrepancies],
    }


def render_runtime_truth_markdown(report: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    lines = [
        "# Runtime Truth Audit Report",
        "",
        f"- Generated (UTC): {report.get('generated_at_utc', '')}",
        f"- Status: **{report.get('status', 'unknown').upper()}**",
        f"- Hard failures: {summary.get('hard_fail_count', 0)}",
        f"- Warnings: {summary.get('warning_count', 0)}",
        f"- Execution gate enabled: {summary.get('execution_gate_enabled', False)}",
        "",
        "## Enabled Capability Set Comparison",
        "",
        f"- Registry enabled IDs: {summary.get('registry_enabled_ids', [])}",
        f"- Runtime doc enabled IDs: {summary.get('runtime_doc_enabled_ids', [])}",
        "",
        "## Mediator Surface",
        "",
        f"- Mediator mapped capability IDs from explicit probes: {summary.get('mediator_mapped_capability_ids', [])}",
        "",
        "## Discrepancies",
        "",
    ]

    discrepancies = report.get("discrepancies", [])
    if not discrepancies:
        lines.append("- None.")
    else:
        for item in discrepancies:
            lines.append(
                f"- [{item.get('severity', 'unknown')}] {item.get('code', 'UNKNOWN')}: {item.get('message', '')}"
            )

    return "\n".join(lines).strip() + "\n"
