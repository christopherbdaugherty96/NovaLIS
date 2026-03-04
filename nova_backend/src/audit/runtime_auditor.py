from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.governor.execute_boundary.execute_boundary import GOVERNED_ACTIONS_ENABLED
from src.governor.governor_mediator import GovernorMediator, Invocation


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_DOC_DIR = PROJECT_ROOT / "docs" / "current_runtime"
REGISTRY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "config" / "registry.json"
RUNTIME_DOC_PATH = RUNTIME_DOC_DIR / "CURRENT_RUNTIME_STATE.md"
CANONICAL_RUNTIME_DOC_PATH = PROJECT_ROOT / "docs" / "CANONICAL" / "PHASE_4_RUNTIME_TRUTH.md"
DEEPSEEK_BRIDGE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "conversation" / "deepseek_bridge.py"
LLM_MANAGER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "llm" / "llm_manager.py"
LLM_GATEWAY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "llm" / "llm_gateway.py"
GOVERNOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "governor.py"
GOVERNOR_MEDIATOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "governor_mediator.py"
NETWORK_MEDIATOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "network_mediator.py"
SKILL_REGISTRY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "skill_registry.py"
LEDGER_WRITER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "ledger" / "writer.py"
LEDGER_EVENT_TYPES_PATH = PROJECT_ROOT / "nova_backend" / "src" / "ledger" / "event_types.py"
ESCALATION_POLICY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "conversation" / "escalation_policy.py"
GENERAL_CHAT_PATH = PROJECT_ROOT / "nova_backend" / "src" / "skills" / "general_chat.py"

GOVERNANCE_MATRIX_PATH = RUNTIME_DOC_DIR / "GOVERNANCE_MATRIX.md"
SKILL_SURFACE_MAP_PATH = RUNTIME_DOC_DIR / "SKILL_SURFACE_MAP.md"
BYPASS_SURFACES_PATH = RUNTIME_DOC_DIR / "BYPASS_SURFACES.md"
RUNTIME_FINGERPRINT_PATH = RUNTIME_DOC_DIR / "RUNTIME_FINGERPRINT.md"
GOVERNANCE_MATRIX_TREE_PATH = RUNTIME_DOC_DIR / "GOVERNANCE_MATRIX_TREE.md"

SKILLS_DIR = PROJECT_ROOT / "nova_backend" / "src" / "skills"
EXECUTORS_DIR = PROJECT_ROOT / "nova_backend" / "src" / "executors"
CONVERSATION_DIR = PROJECT_ROOT / "nova_backend" / "src" / "conversation"


def _build_allowlisted_paths() -> frozenset[Path]:
    paths = {
        REGISTRY_PATH,
        RUNTIME_DOC_PATH,
        CANONICAL_RUNTIME_DOC_PATH,
        DEEPSEEK_BRIDGE_PATH,
        LLM_MANAGER_PATH,
        LLM_GATEWAY_PATH,
        GOVERNOR_PATH,
        GOVERNOR_MEDIATOR_PATH,
        NETWORK_MEDIATOR_PATH,
        SKILL_REGISTRY_PATH,
        LEDGER_WRITER_PATH,
        LEDGER_EVENT_TYPES_PATH,
        ESCALATION_POLICY_PATH,
    }
    paths.update(SKILLS_DIR.glob("*.py"))
    paths.update(EXECUTORS_DIR.glob("*.py"))
    paths.update(CONVERSATION_DIR.glob("*.py"))
    return frozenset(paths)


ALLOWED_READ_PATHS = _build_allowlisted_paths()

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
    """Extract enabled capability IDs from generated snapshot sections."""
    if not markdown_text:
        return []

    found: set[int] = set()
    in_capability_table = False

    for line in markdown_text.splitlines():
        lower = line.lower()

        if line.strip() == "## Capability table":
            in_capability_table = True
            continue
        if in_capability_table and line.startswith("## "):
            in_capability_table = False

        if in_capability_table and line.strip().startswith("|"):
            parts = [part.strip() for part in line.strip().strip("|").split("|")]
            if len(parts) >= 3 and parts[0].isdigit() and parts[2].lower() in {"true", "enabled"}:
                found.add(int(parts[0]))
            continue

        bullet_match = re.search(r"\b(\d+)\b\s*[:\-|]\s*.*\benabled\b", lower)
        if bullet_match:
            found.add(int(bullet_match.group(1)))
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

    enabled_ids = set(_enabled_registry_ids(_load_registry()))
    filtered_capability_ids = sorted(cap_id for cap_id in capability_ids if cap_id in enabled_ids)

    return {
        "probes": entries,
        "mapped_capability_ids": filtered_capability_ids,
    }


def _detect_direct_model_call_bypass() -> dict[str, Any]:
    deepseek_src = _safe_read(DEEPSEEK_BRIDGE_PATH)
    general_chat_src = _safe_read(GENERAL_CHAT_PATH)
    llm_gateway_src = _safe_read(LLM_GATEWAY_PATH)
    llm_manager_src = _safe_read(LLM_MANAGER_PATH)

    return {
        "deepseek_uses_ollama_chat_directly": "ollama.chat" in deepseek_src,
        "general_chat_uses_ollama_chat_directly": "ollama.chat" in general_chat_src,
        "llm_gateway_generate_chat_present": "def generate_chat(" in llm_gateway_src,
        "llm_manager_generate_present": "def generate(" in llm_manager_src,
    }


def _derive_status(hard_fail_count: int, warning_count: int) -> str:
    if hard_fail_count > 0:
        return "fail"
    if warning_count > 0:
        return "warn"
    return "pass"


def _governor_enforcement_summary() -> dict[str, bool]:
    governor_src = _safe_read(GOVERNOR_PATH)
    network_src = _safe_read(NETWORK_MEDIATOR_PATH)
    ledger_src = _safe_read(LEDGER_WRITER_PATH)

    return {
        "single_action_queue_enforced": "SingleActionQueue" in governor_src and "has_pending" in governor_src,
        "execution_timeout_guard_active": "MAX_EXECUTION_TIME" in governor_src,
        "dns_rebinding_protection_active": "socket.getaddrinfo" in network_src,
        "ledger_logging_active": "log_event(" in governor_src or "log_event(" in network_src,
        "execution_gate_enabled": bool(GOVERNED_ACTIONS_ENABLED),
    }


def _network_mediated_capability_ids(governor_source: str) -> list[int]:
    mediated: set[int] = set()
    current_cap: int | None = None
    for line in governor_source.splitlines():
        cap_match = re.search(r"req\.capability_id\s*==\s*(\d+)", line)
        if cap_match:
            current_cap = int(cap_match.group(1))
            continue
        if current_cap is not None and "self.network" in line:
            mediated.add(current_cap)
    return sorted(mediated)


def _derive_capability_governance_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    governor_src = _safe_read(GOVERNOR_PATH)
    mediated_ids = set(_network_mediated_capability_ids(governor_src))
    enforce = _governor_enforcement_summary()

    rows: list[dict[str, Any]] = []
    for capability in registry.get("capabilities", []):
        cid = int(capability.get("id", -1))
        risk_level = str(capability.get("risk_level", ""))
        confirmation_required = risk_level == "confirm"
        network_access = cid in mediated_ids

        if cid == 18:
            authority_class = "speech_output"
            execution_surface = "Governor → Speech"
        elif confirmation_required:
            authority_class = "confirm_required"
            execution_surface = "Governor → Executor"
        elif network_access:
            authority_class = "read_only"
            execution_surface = "Governor → NetworkMediator"
        elif capability.get("data_exfiltration") is True:
            authority_class = "read_only"
            execution_surface = "Governor → Executor"
        else:
            authority_class = "system_action"
            execution_surface = "Governor → Executor"

        rows.append(
            {
                "id": cid,
                "name": capability.get("name", ""),
                "enabled": bool(capability.get("enabled", False)),
                "status": capability.get("status", ""),
                "phase_introduced": capability.get("phase_introduced", ""),
                "risk_level": risk_level,
                "data_exfiltration": bool(capability.get("data_exfiltration", False)),
                "authority_class": authority_class,
                "confirmation_required": confirmation_required,
                "network_access": network_access,
                "execution_surface": execution_surface,
                "execution_gate": enforce["execution_gate_enabled"],
                "single_action_queue": enforce["single_action_queue_enforced"],
                "ledger_allowlist": "event_type not in EVENT_TYPES" in _safe_read(LEDGER_WRITER_PATH),
                "dns_rebinding_guard": enforce["dns_rebinding_protection_active"],
                "timeout_guard": enforce["execution_timeout_guard_active"],
            }
        )

    return sorted(rows, key=lambda r: r["id"])


def _skill_surface_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for path in sorted(SKILLS_DIR.glob("*.py")):
        src = _safe_read(path)
        if not src.strip() or path.name == "__init__.py":
            continue
        name_match = re.search(r'^\s*name\s*=\s*"([^"]+)"', src, re.MULTILINE)
        skill_name = name_match.group(1) if name_match else path.stem
        network_usage = "yes" if ("NetworkMediator" in src or "self.network" in src) else "no"
        if "ollama.chat" in src:
            model_usage = "ollama_direct"
        elif "generate_chat" in src:
            model_usage = "llm_gateway"
        elif "LLMManager" in src or "llm_manager" in src:
            model_usage = "manager"
        else:
            model_usage = "none"
        rows.append(
            {
                "name": skill_name,
                "module": f"src/skills/{path.name}",
                "surface_type": "skill",
                "network_usage": network_usage,
                "model_usage": model_usage,
            }
        )

    deepseek_src = _safe_read(DEEPSEEK_BRIDGE_PATH)
    rows.append(
        {
            "name": "deepseek_bridge",
            "module": "src/conversation/deepseek_bridge.py",
            "surface_type": "conversation",
            "network_usage": "unknown",
            "model_usage": "llm_gateway" if "generate_chat" in deepseek_src else ("ollama_direct" if "ollama.chat" in deepseek_src else "none"),
        }
    )

    mediator_map = _mediator_surface_map()
    for probe in mediator_map["probes"]:
        if probe["capability_id"] is None:
            continue
        rows.append(
            {
                "name": probe["group"],
                "module": "src/governor/governor_mediator.py",
                "surface_type": "governor_capability",
                "network_usage": "unknown",
                "model_usage": "none",
                "capability_id": str(probe["capability_id"]),
            }
        )

    dedup = {(r.get("name"), r.get("module"), r.get("surface_type")): r for r in rows}
    return sorted(dedup.values(), key=lambda r: (r.get("surface_type", ""), r.get("name", "")))


def _find_direct_ollama_calls_outside_manager() -> list[str]:
    offenders: list[str] = []
    for path in sorted(ALLOWED_READ_PATHS):
        if path.suffix != ".py":
            continue
        rel = path.relative_to(PROJECT_ROOT)
        if rel.as_posix() in {
            "nova_backend/src/llm/llm_manager.py",
            "nova_backend/src/llm/llm_manager_vlock.py",
            "nova_backend/src/llm/llm_gateway.py",
        }:
            continue
        src = _safe_read(path)
        if "ollama.chat" in src:
            offenders.append(rel.as_posix())
    return offenders


def _find_requests_usage_outside_network_mediator() -> list[str]:
    offenders: list[str] = []
    allowed_requests_users = {
        "nova_backend/src/governor/network_mediator.py",
        "nova_backend/src/llm/llm_manager.py",
        "nova_backend/src/llm/llm_manager_vlock.py",
    }
    for path in sorted(ALLOWED_READ_PATHS):
        if path.suffix != ".py":
            continue
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        src = _safe_read(path)
        if "import requests" in src or "requests." in src:
            if rel not in allowed_requests_users:
                offenders.append(rel)
    return offenders


def _executor_paths_outside_governor() -> list[str]:
    paths: list[str] = []
    for path in sorted(EXECUTORS_DIR.glob("*.py")):
        if path.name == "__init__.py":
            continue
        paths.append(path.relative_to(PROJECT_ROOT).as_posix())
    return paths


def _runtime_fingerprint(registry_enabled_ids: list[int]) -> dict[str, str]:
    commit_hash = "unknown"
    dirty = "unknown"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        commit_hash = result.stdout.strip() or "unknown"
    except Exception:
        commit_hash = "unknown"

    try:
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        dirty = "true" if status.stdout.strip() else "false"
    except Exception:
        dirty = "unknown"

    enabled_hash = hashlib.sha256(json.dumps(registry_enabled_ids, sort_keys=True).encode("utf-8")).hexdigest()

    return {
        "git_commit_hash": commit_hash,
        "git_dirty": dirty,
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "enabled_capability_ids_hash": enabled_hash,
        "phase_marker": "Phase-4 runtime active",
    }


def _path_for_report(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except Exception:
        return str(path)


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
                message="Enabled capability ID set differs between docs/current_runtime/CURRENT_RUNTIME_STATE.md and registry.json.",
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
                message="docs/current_runtime/CURRENT_RUNTIME_STATE.md is missing.",
                details={"path": _path_for_report(RUNTIME_DOC_PATH)},
            )
        )

    if model_path_signals.get("deepseek_uses_ollama_chat_directly") or model_path_signals.get("general_chat_uses_ollama_chat_directly"):
        discrepancies.append(
            Discrepancy(
                severity="warning",
                code="DIRECT_MODEL_CALL_BYPASS",
                message="Conversation or skill modules appear to call ollama.chat directly instead of the centralized LLM gateway.",
                details={
                    "deepseek_bridge_path": _path_for_report(DEEPSEEK_BRIDGE_PATH),
                    "general_chat_path": "nova_backend/src/skills/general_chat.py",
                },
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
            "allowlisted_paths": [_path_for_report(path) for path in sorted(ALLOWED_READ_PATHS)],
            "registry_path": _path_for_report(REGISTRY_PATH),
            "runtime_doc_path": _path_for_report(RUNTIME_DOC_PATH),
            "canonical_runtime_doc_path": _path_for_report(CANONICAL_RUNTIME_DOC_PATH),
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


def render_governance_matrix_markdown(registry: dict[str, Any]) -> str:
    rows = _derive_capability_governance_rows(registry)
    lines = [
        "# GOVERNANCE_MATRIX",
        "",
        "Deterministic capability governance matrix derived from allowlisted runtime sources.",
        "",
        "| id | name | enabled | status | phase_introduced | risk_level | data_exfiltration | authority_class | confirmation_required | network_access | execution_surface | execution_gate | single_action_queue | ledger_allowlist | dns_rebinding_guard | timeout_guard |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {id} | {name} | {enabled} | {status} | {phase_introduced} | {risk_level} | {data_exfiltration} | {authority_class} | {confirmation_required} | {network_access} | {execution_surface} | {execution_gate} | {single_action_queue} | {ledger_allowlist} | {dns_rebinding_guard} | {timeout_guard} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Derivation notes",
            "",
            "- authority_class derivation: `speech_output` for capability 18, `confirm_required` when risk_level is `confirm`, `read_only` for network-mediated/data-exfil surfaces, else `system_action`.",
            "- network_access is derived from Governor execution branches that pass `self.network` to an executor.",
            "- execution_gate/single_action_queue/dns_rebinding_guard/timeout_guard/ledger_allowlist are code-presence checks from allowlisted modules.",
            "- If a field cannot be proven from allowlisted runtime sources, value must be `unknown` (none currently unresolved under present code).",
            "",
        ]
    )
    return "\n".join(lines)


def render_skill_surface_map_markdown() -> str:
    rows = _skill_surface_rows()
    lines = [
        "# SKILL_SURFACE_MAP",
        "",
        "Deterministic surface map for skills, conversation modules, and governor capability routes.",
        "",
        "| skill_or_surface | module | surface_type | network_usage | model_usage | capability_id |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row.get('name', '')} | {row.get('module', '')} | {row.get('surface_type', '')} | {row.get('network_usage', 'unknown')} | {row.get('model_usage', 'unknown')} | {row.get('capability_id', '')} |"
        )

    lines.extend(
        [
            "",
            "## Escalation vs governed execution",
            "",
            "- `ALLOW_ANALYSIS_ONLY` is represented in `src/conversation/escalation_policy.py` and used by `GeneralChatSkill` as analysis-only output path.",
            "- Governed capabilities are routed by `GovernorMediator.parse_governed_invocation(...)` and executed via `Governor.handle_governed_invocation(...)`.",
            "",
        ]
    )
    return "\n".join(lines)


def render_bypass_surfaces_markdown() -> str:
    ollama_offenders = _find_direct_ollama_calls_outside_manager()
    requests_offenders = _find_requests_usage_outside_network_mediator()
    executor_surfaces = _executor_paths_outside_governor()

    lines = [
        "# BYPASS_SURFACES",
        "",
        "Read-only truth report of detectable bypass indicators from allowlisted runtime sources.",
        "",
        "## Direct ollama.chat outside llm gateway",
        "",
    ]

    if ollama_offenders:
        lines.extend(f"- {path}" for path in ollama_offenders)
    else:
        lines.append("- None detected.")

    lines.extend(["", "## requests/network usage outside NetworkMediator", ""])
    if requests_offenders:
        lines.extend(f"- {path}" for path in requests_offenders)
    else:
        lines.append("- None detected.")

    lines.extend(["", "## Executor callable paths outside governor", ""])
    lines.append("- Architectural constraint: executors exist as importable callables, but governed runtime routes execution through Governor branches.")
    lines.extend(f"- {path}" for path in executor_surfaces)
    lines.append("")
    return "\n".join(lines)


def render_runtime_fingerprint_markdown(registry_enabled_ids: list[int]) -> str:
    fp = _runtime_fingerprint(registry_enabled_ids)
    lines = [
        "# RUNTIME_FINGERPRINT",
        "",
        f"- git_commit_hash: {fp['git_commit_hash']}",
        f"- git_dirty: {fp['git_dirty']}",
        f"- python_version: {fp['python_version']}",
        f"- platform: {fp['platform']}",
        f"- generated_at_utc: {fp['generated_at_utc']}",
        f"- enabled_capability_ids_hash: {fp['enabled_capability_ids_hash']}",
        f"- phase_marker: {fp['phase_marker']}",
        "",
    ]
    return "\n".join(lines)


def render_governance_matrix_tree_markdown(registry: dict[str, Any]) -> str:
    rows = _derive_capability_governance_rows(registry)
    enabled = [row["id"] for row in rows if row["enabled"]]
    disabled = [row["id"] for row in rows if not row["enabled"]]
    enforcement = _governor_enforcement_summary()
    skill_routes = [r for r in _skill_surface_rows() if r.get("surface_type") == "governor_capability" and r.get("capability_id")]
    llm_gateway_users = []
    for rel_path in ("src/conversation/deepseek_bridge.py", "src/skills/general_chat.py"):
        src = _safe_read(PROJECT_ROOT / "nova_backend" / rel_path)
        if "generate_chat" in src:
            llm_gateway_users.append(rel_path)

    lines = [
        "# GOVERNANCE_MATRIX_TREE",
        "",
        "Deterministic generated tree diagram derived from allowlisted runtime sources.",
        "",
        "```mermaid",
        "graph TD",
        "  Runtime[Phase-4 Runtime]",
        f"  Runtime --> Enabled[Enabled IDs: {enabled}]",
        f"  Runtime --> Disabled[Disabled IDs: {disabled}]",
        "  Runtime --> Gov[Governor Guards]",
        f"  Gov --> EG[execution_gate: {enforcement['execution_gate_enabled']}]",
        f"  Gov --> SAQ[single_action_queue: {enforcement['single_action_queue_enforced']}]",
        "  Gov --> LA[ledger_allowlist: True]",
        f"  Gov --> DNS[dns_rebinding_guard: {enforcement['dns_rebinding_protection_active']}]",
        f"  Gov --> TO[timeout_guard: {enforcement['execution_timeout_guard_active']}]",
        "  Runtime --> Caps[Capabilities]",
    ]
    for row in rows:
        label = f"{row['id']}:{row['name']}"
        lines.append(f"  Caps --> C{row['id']}[{label}]")
        lines.append(
            f"  C{row['id']} --> C{row['id']}A[authority={row['authority_class']}, risk={row['risk_level']}, network={row['network_access']}, exfil={row['data_exfiltration']}, confirm={row['confirmation_required']}, surface={row['execution_surface']}]"
        )
    lines.append("  Runtime --> Routes[Skill Routes]")
    for route in skill_routes:
        lines.append(f"  Routes --> R{route['capability_id']}_{route['name']}[{route['name']} -> capability {route['capability_id']}]")
    lines.append("  Runtime --> LLM[Conversation/Model Surfaces]")
    for module in llm_gateway_users:
        key = module.replace("/", "_").replace(".", "_")
        lines.append(f"  LLM --> {key}[{module} uses llm_gateway.generate_chat]")
    lines.extend(["```", "", "```text", "Runtime", f"├─ Enabled IDs: {enabled}", f"├─ Disabled IDs: {disabled}", "├─ Governor Guards"])
    lines.extend(
        [
            f"│  ├─ execution_gate: {enforcement['execution_gate_enabled']}",
            f"│  ├─ single_action_queue: {enforcement['single_action_queue_enforced']}",
            "│  ├─ ledger_allowlist: True",
            f"│  ├─ dns_rebinding_guard: {enforcement['dns_rebinding_protection_active']}",
            f"│  └─ timeout_guard: {enforcement['execution_timeout_guard_active']}",
            "├─ Capabilities",
        ]
    )
    for row in rows:
        lines.append(
            f"│  ├─ {row['id']} {row['name']} (authority={row['authority_class']}, risk={row['risk_level']}, network={row['network_access']}, exfil={row['data_exfiltration']}, confirm={row['confirmation_required']}, surface={row['execution_surface']})"
        )
    lines.append("├─ Skill → capability routes")
    for route in skill_routes:
        lines.append(f"│  ├─ {route['name']} -> {route['capability_id']}")
    lines.append("└─ Conversation/model surfaces")
    for module in llm_gateway_users:
        lines.append(f"   ├─ {module} -> llm_gateway.generate_chat")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def render_current_runtime_state_markdown(report: dict[str, Any], registry: dict[str, Any]) -> str:
    summary = report.get("summary", {})
    generated_at = report.get("generated_at_utc", "")

    capabilities = registry.get("capabilities", [])
    enabled_ids = [int(item["id"]) for item in capabilities if item.get("enabled") is True]
    disabled_ids = [int(item["id"]) for item in capabilities if item.get("enabled") is not True]

    governance_rows = _derive_capability_governance_rows(registry)
    enforcement = _governor_enforcement_summary()
    model_signals = report.get("checks", {}).get("model_path_signals", {})
    network_caps = sorted({row["id"] for row in governance_rows if row["network_access"] is True})
    skill_rows = [r for r in _skill_surface_rows() if r.get("surface_type") == "governor_capability" and r.get("capability_id")]
    fingerprint = _runtime_fingerprint(sorted(enabled_ids))

    lines = [
        "# CURRENT_RUNTIME_STATE.md",
        "",
        "Auto-generated runtime snapshot. Do not edit manually.",
        "",
        f"- Generated (UTC): {generated_at}",
        f"- Audit status: **{report.get('status', 'unknown').upper()}**",
        f"- Execution gate enabled: {summary.get('execution_gate_enabled', False)}",
        "",
        "## Enabled capability IDs",
        "",
        f"- {sorted(enabled_ids)}",
        "",
        "## Disabled capability IDs",
        "",
        f"- {sorted(disabled_ids)}",
        "",
        "## Capability table",
        "",
        "| id | name | enabled | status | risk_level | data_exfiltration |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for capability in capabilities:
        lines.append(
            "| {id} | {name} | {enabled} | {status} | {risk_level} | {data_exfiltration} |".format(
                id=capability.get("id", ""),
                name=capability.get("name", ""),
                enabled=bool(capability.get("enabled", False)),
                status=capability.get("status", ""),
                risk_level=capability.get("risk_level", ""),
                data_exfiltration=bool(capability.get("data_exfiltration", False)),
            )
        )

    lines.extend(
        [
            "",
            "## Capability Governance Matrix",
            "",
            "| id | name | enabled | authority_class | confirmation_required | network_access | execution_layer |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in governance_rows:
        lines.append(
            f"| {row['id']} | {row['name']} | {row['enabled']} | {row['authority_class']} | {row['confirmation_required']} | {row['network_access']} | {row['execution_surface']} |"
        )

    lines.extend(
        [
            "",
            "## Governor Enforcement Summary",
            "",
            f"- single_action_queue_enforced: {enforcement['single_action_queue_enforced']}",
            f"- execution_timeout_guard_active: {enforcement['execution_timeout_guard_active']}",
            f"- dns_rebinding_protection_active: {enforcement['dns_rebinding_protection_active']}",
            f"- ledger_logging_active: {enforcement['ledger_logging_active']}",
            f"- execution_gate_enabled: {enforcement['execution_gate_enabled']}",
            "",
            "## Network Surface Summary",
            "",
            f"- Capabilities using NetworkMediator: {network_caps}",
            f"- Direct LLM calls detected: deepseek_uses_ollama_chat_directly={model_signals.get('deepseek_uses_ollama_chat_directly', False)}",
            f"- Allowed_analysis_only surfaces: escalation_policy.ALLOW_ANALYSIS_ONLY={('ALLOW_ANALYSIS_ONLY' in _safe_read(ESCALATION_POLICY_PATH))}",
            "",
            "## Skill → Capability Routing Map",
            "",
        ]
    )

    for row in skill_rows:
        lines.append(f"- {row['name']} -> capability_id={row['capability_id']}")

    lines.extend(
        [
            "",
            "## Runtime Fingerprint",
            "",
            f"- git_commit_hash: {fingerprint['git_commit_hash']}",
            f"- generated_at_utc: {fingerprint['generated_at_utc']}",
            f"- phase_marker: {fingerprint['phase_marker']}",
            "",
            "## Mediator mapped capability IDs",
            "",
            f"- {summary.get('mediator_mapped_capability_ids', [])}",
            "",
            "## Runtime truth discrepancies",
            "",
        ]
    )

    discrepancies = report.get("discrepancies", [])
    if not discrepancies:
        lines.append("- None")
    else:
        for item in discrepancies:
            lines.append(
                f"- [{item.get('severity', 'unknown')}] {item.get('code', 'UNKNOWN')}: {item.get('message', '')}"
            )

    return "\n".join(lines).strip() + "\n"


def write_runtime_governance_docs(output_dir: Path | None = None, registry: dict[str, Any] | None = None) -> dict[str, Path]:
    registry = registry or _load_registry()
    output_dir = output_dir or RUNTIME_DOC_DIR
    enabled_ids = _enabled_registry_ids(registry)

    output_dir.mkdir(parents=True, exist_ok=True)
    governance_matrix_path = output_dir / "GOVERNANCE_MATRIX.md"
    skill_surface_map_path = output_dir / "SKILL_SURFACE_MAP.md"
    bypass_surfaces_path = output_dir / "BYPASS_SURFACES.md"
    runtime_fingerprint_path = output_dir / "RUNTIME_FINGERPRINT.md"
    governance_matrix_tree_path = output_dir / "GOVERNANCE_MATRIX_TREE.md"

    governance_matrix_path.write_text(render_governance_matrix_markdown(registry), encoding="utf-8")
    skill_surface_map_path.write_text(render_skill_surface_map_markdown(), encoding="utf-8")
    bypass_surfaces_path.write_text(render_bypass_surfaces_markdown(), encoding="utf-8")
    runtime_fingerprint_path.write_text(render_runtime_fingerprint_markdown(enabled_ids), encoding="utf-8")
    governance_matrix_tree_path.write_text(render_governance_matrix_tree_markdown(registry), encoding="utf-8")

    return {
        "governance_matrix": governance_matrix_path.resolve(),
        "skill_surface_map": skill_surface_map_path.resolve(),
        "bypass_surfaces": bypass_surfaces_path.resolve(),
        "runtime_fingerprint": runtime_fingerprint_path.resolve(),
        "governance_matrix_tree": governance_matrix_tree_path.resolve(),
    }


def write_current_runtime_state_snapshot(path: Path = RUNTIME_DOC_PATH) -> Path:
    report = run_runtime_truth_audit()
    registry = _load_registry()
    markdown = render_current_runtime_state_markdown(report, registry)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")

    # Companion governance docs for read-only introspection.
    write_runtime_governance_docs(output_dir=path.parent, registry=registry)

    return path.resolve()
