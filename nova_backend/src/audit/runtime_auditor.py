from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.governor.execute_boundary.execute_boundary import GOVERNED_ACTIONS_ENABLED
from src.governor.governor_mediator import GovernorMediator, Invocation
from src.build_phase import BUILD_PHASE, PHASE_4_2_ENABLED


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_DOC_DIR = PROJECT_ROOT / "docs" / "current_runtime"
REGISTRY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "config" / "registry.json"
RUNTIME_DOC_PATH = RUNTIME_DOC_DIR / "CURRENT_RUNTIME_STATE.md"
CANONICAL_RUNTIME_DOC_PATH = PROJECT_ROOT / "docs" / "PHASE_4_RUNTIME_TRUTH.md"
DEEPSEEK_BRIDGE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "conversation" / "deepseek_bridge.py"
LLM_MANAGER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "llm" / "llm_manager.py"
LLM_GATEWAY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "llm" / "llm_gateway.py"
GOVERNOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "governor.py"
GOVERNOR_MEDIATOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "governor_mediator.py"
NETWORK_MEDIATOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "network_mediator.py"
EXECUTE_BOUNDARY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "execute_boundary" / "execute_boundary.py"
SKILL_REGISTRY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "skill_registry.py"
LEDGER_WRITER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "ledger" / "writer.py"
LEDGER_EVENT_TYPES_PATH = PROJECT_ROOT / "nova_backend" / "src" / "ledger" / "event_types.py"
ESCALATION_POLICY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "conversation" / "escalation_policy.py"
GENERAL_CHAT_PATH = PROJECT_ROOT / "nova_backend" / "src" / "skills" / "general_chat.py"
BRAIN_SERVER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "brain_server.py"
SESSION_HANDLER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "websocket" / "session_handler.py"
BRIDGE_API_PATH = PROJECT_ROOT / "nova_backend" / "src" / "api" / "bridge_api.py"
SETTINGS_API_PATH = PROJECT_ROOT / "nova_backend" / "src" / "api" / "settings_api.py"
OPENCLAW_AGENT_API_PATH = PROJECT_ROOT / "nova_backend" / "src" / "api" / "openclaw_agent_api.py"
STATIC_DASHBOARD_PATH = PROJECT_ROOT / "nova_backend" / "static" / "dashboard.js"
STATIC_INDEX_PATH = PROJECT_ROOT / "nova_backend" / "static" / "index.html"
BUILD_PHASE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "build_phase.py"
ATOMIC_POLICY_STORE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "policies" / "atomic_policy_store.py"
POLICY_VALIDATOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "policies" / "policy_validator.py"
POLICY_EXECUTOR_GATE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "policy_executor_gate.py"
CAPABILITY_TOPOLOGY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "governor" / "capability_topology.py"
EXTERNAL_REASONING_EXECUTOR_PATH = PROJECT_ROOT / "nova_backend" / "src" / "executors" / "external_reasoning_executor.py"
DEEPSEEK_SAFETY_WRAPPER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "conversation" / "deepseek_safety_wrapper.py"
OPENCLAW_AGENT_RUNTIME_STORE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "openclaw" / "agent_runtime_store.py"
OPENCLAW_AGENT_RUNNER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "openclaw" / "agent_runner.py"
OPENCLAW_AGENT_PERSONALITY_BRIDGE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "openclaw" / "agent_personality_bridge.py"
OPENCLAW_STRICT_PREFLIGHT_PATH = PROJECT_ROOT / "nova_backend" / "src" / "openclaw" / "strict_preflight.py"
OPENCLAW_AGENT_SCHEDULER_PATH = PROJECT_ROOT / "nova_backend" / "src" / "openclaw" / "agent_scheduler.py"
OPENAI_RESPONSES_LANE_PATH = PROJECT_ROOT / "nova_backend" / "src" / "providers" / "openai_responses_lane.py"
ASSISTIVE_NOTICING_PATH = PROJECT_ROOT / "nova_backend" / "src" / "working_context" / "assistive_noticing.py"
CONNECTOR_PACKAGE_REGISTRY_PATH = PROJECT_ROOT / "nova_backend" / "src" / "connectors" / "package_registry.py"
CONNECTOR_PACKAGES_PATH = PROJECT_ROOT / "nova_backend" / "src" / "config" / "connector_packages.json"

GOVERNANCE_MATRIX_PATH = RUNTIME_DOC_DIR / "GOVERNANCE_MATRIX.md"
SKILL_SURFACE_MAP_PATH = RUNTIME_DOC_DIR / "SKILL_SURFACE_MAP.md"
BYPASS_SURFACES_PATH = RUNTIME_DOC_DIR / "BYPASS_SURFACES.md"
RUNTIME_FINGERPRINT_PATH = RUNTIME_DOC_DIR / "RUNTIME_FINGERPRINT.md"
GOVERNANCE_MATRIX_TREE_PATH = RUNTIME_DOC_DIR / "GOVERNANCE_MATRIX_TREE.md"

SKILLS_DIR = PROJECT_ROOT / "nova_backend" / "src" / "skills"
EXECUTORS_DIR = PROJECT_ROOT / "nova_backend" / "src" / "executors"
CONVERSATION_DIR = PROJECT_ROOT / "nova_backend" / "src" / "conversation"
WORKING_CONTEXT_DIR = PROJECT_ROOT / "nova_backend" / "src" / "working_context"
API_DIR = PROJECT_ROOT / "nova_backend" / "src" / "api"
PERSONALITY_DIR = PROJECT_ROOT / "nova_backend" / "src" / "personality"
SETTINGS_DIR = PROJECT_ROOT / "nova_backend" / "src" / "settings"
OPENCLAW_DIR = PROJECT_ROOT / "nova_backend" / "src" / "openclaw"
PROVIDERS_DIR = PROJECT_ROOT / "nova_backend" / "src" / "providers"
TASKS_DIR = PROJECT_ROOT / "nova_backend" / "src" / "tasks"
WEBSOCKET_DIR = PROJECT_ROOT / "nova_backend" / "src" / "websocket"
CONNECTORS_DIR = PROJECT_ROOT / "nova_backend" / "src" / "connectors"


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
        EXECUTE_BOUNDARY_PATH,
        SKILL_REGISTRY_PATH,
        LEDGER_WRITER_PATH,
        LEDGER_EVENT_TYPES_PATH,
        ESCALATION_POLICY_PATH,
        BRAIN_SERVER_PATH,
        SESSION_HANDLER_PATH,
        BRIDGE_API_PATH,
        SETTINGS_API_PATH,
        OPENCLAW_AGENT_API_PATH,
        STATIC_DASHBOARD_PATH,
        STATIC_INDEX_PATH,
        BUILD_PHASE_PATH,
        OPENCLAW_AGENT_RUNTIME_STORE_PATH,
        OPENCLAW_AGENT_RUNNER_PATH,
        OPENCLAW_AGENT_PERSONALITY_BRIDGE_PATH,
        OPENCLAW_STRICT_PREFLIGHT_PATH,
        OPENCLAW_AGENT_SCHEDULER_PATH,
        OPENAI_RESPONSES_LANE_PATH,
        CONNECTOR_PACKAGE_REGISTRY_PATH,
        CONNECTOR_PACKAGES_PATH,
    }
    paths.update(SKILLS_DIR.glob("*.py"))
    paths.update(EXECUTORS_DIR.glob("*.py"))
    paths.update(CONVERSATION_DIR.glob("*.py"))
    paths.update(WORKING_CONTEXT_DIR.glob("*.py"))
    paths.update(API_DIR.glob("*.py"))
    paths.update(PERSONALITY_DIR.glob("*.py"))
    paths.update(SETTINGS_DIR.glob("*.py"))
    paths.update(OPENCLAW_DIR.glob("*.py"))
    paths.update(PROVIDERS_DIR.glob("*.py"))
    paths.update(TASKS_DIR.glob("*.py"))
    paths.update(WEBSOCKET_DIR.glob("*.py"))
    paths.update(CONNECTORS_DIR.glob("*.py"))
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
    "weather": "weather_snapshot",
    "news": "news_snapshot",
    "calendar": "calendar_snapshot",
    "take a screenshot": "screen_capture",
    "analyze screen": "screen_analysis",
    "explain this": "explain_anything",
    "what is this": "explain_anything",
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
    "summarize headline 2": "headline_summary",
    "summarize headlines 1 and 3": "headline_summary",
    "daily brief": "intelligence_brief",
    "show topic memory map": "topic_memory_map",
    "verify this": "response_verification",
    "second opinion": "external_reasoning_review",
    "morning brief": "openclaw_execute",
    "summarize doc 2": "analysis_document",
    "update story ai regulation": "story_tracker_update",
    "show story ai regulation": "story_tracker_view",
    "memory list": "memory_governance",
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


def _stable_hash_bytes(path: Path) -> bytes:
    """Normalize text file line endings so runtime hashes are cross-platform stable."""
    if not path.exists():
        return b""
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


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
        stripped = line.strip()
        lower = stripped.lower()

        if lower in {"## capability table", "## active capabilities"}:
            in_capability_table = True
            continue
        if in_capability_table and line.startswith("## "):
            in_capability_table = False

        if in_capability_table and stripped.startswith("|"):
            parts = [part.strip() for part in stripped.strip("|").split("|")]
            if not parts or not parts[0].isdigit():
                continue

            # Legacy table: | id | name | enabled | status | ... |
            if len(parts) >= 3 and parts[2].lower() in {"true", "false", "enabled", "disabled"}:
                if parts[2].lower() in {"true", "enabled"}:
                    found.add(int(parts[0]))
                continue

            # New canonical table: | ID | Capability | Registry Status | Runtime Enabled | Runtime State |
            if len(parts) >= 4 and parts[3].lower() in {"true", "enabled"}:
                found.add(int(parts[0]))
            continue

        bullet_match = re.search(r"^\s*-\s*(\d+)\b\s*[:\-|]\s*.*\benabled\b", lower)
        if bullet_match:
            found.add(int(bullet_match.group(1)))
            continue

    return sorted(found)


def _mediator_surface_map() -> dict[str, Any]:
    entries = []
    capability_ids = set()

    for phrase, group in MEDIATOR_TRIGGER_PROBES.items():
        parsed = GovernorMediator.parse_governed_invocation(phrase, session_id="audit-runtime")
        cap_id = getattr(parsed, "capability_id", None)
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
    boundary_src = _safe_read(EXECUTE_BOUNDARY_PATH)
    brain_src = _safe_read(BRAIN_SERVER_PATH)
    websocket_src = _safe_read(SESSION_HANDLER_PATH)

    return {
        "single_action_queue_enforced": "SingleActionQueue" in governor_src and "has_pending" in governor_src,
        "execution_timeout_guard_active": "_release_after_timeout" in boundary_src and "cancel_futures=True" in boundary_src,
        "dns_rebinding_protection_active": (
            "describe_http_rebinding_violation" in brain_src and "describe_websocket_rebinding_violation" in websocket_src
        ) or "socket.getaddrinfo" in network_src,
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
        description = str(capability.get("description") or "").strip()
        authority_class = str(capability.get("authority_class") or "").strip() or None
        confirmation_required = capability.get("requires_confirmation")
        reversible = capability.get("reversible")
        external_effect = capability.get("external_effect")

        if authority_class is None:
            if cid == 18:
                authority_class = "speech_output"
            elif risk_level == "confirm":
                authority_class = "confirm_required"
            elif cid in mediated_ids or capability.get("data_exfiltration") is True:
                authority_class = "read_only"
            else:
                authority_class = "system_action"

        if confirmation_required is None:
            confirmation_required = risk_level == "confirm"
        if reversible is None:
            reversible = True
        if external_effect is None:
            external_effect = False

        network_access = authority_class == "read_only_network" or cid in mediated_ids

        if cid == 18:
            execution_surface = "Governor -> Speech"
        elif network_access:
            execution_surface = "Governor -> NetworkMediator"
        else:
            execution_surface = "Governor -> Executor"

        rows.append(
            {
                "id": cid,
                "name": capability.get("name", ""),
                "description": description,
                "enabled": bool(capability.get("enabled", False)),
                "status": capability.get("status", ""),
                "phase_introduced": capability.get("phase_introduced", ""),
                "risk_level": risk_level,
                "data_exfiltration": bool(capability.get("data_exfiltration", False)),
                "authority_class": authority_class,
                "confirmation_required": bool(confirmation_required),
                "reversible": bool(reversible),
                "external_effect": bool(external_effect),
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
    registry = _load_registry()
    governor_src = _safe_read(GOVERNOR_PATH)
    skill_registry_src = _safe_read(SKILL_REGISTRY_PATH)
    network_mediated_ids = set(_network_mediated_capability_ids(governor_src))
    capability_network_map = {
        int(item.get("id")): ("yes" if int(item.get("id")) in network_mediated_ids else "no")
        for item in registry.get("capabilities", [])
        if item.get("id") is not None
    }
    live_skill_modules = {
        match.group(1)
        for match in re.finditer(r"from\s+src\.skills\.([a-zA-Z0-9_]+)\s+import", skill_registry_src)
    }

    for path in sorted(SKILLS_DIR.glob("*.py")):
        src = _safe_read(path)
        if not src.strip() or path.name == "__init__.py":
            continue
        if path.stem not in live_skill_modules:
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
            "network_usage": "no",
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
                "network_usage": capability_network_map.get(int(probe["capability_id"]), "no"),
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
    request_usage_re = re.compile(
        r"\b(?:import\s+requests\b|from\s+requests\s+import\b|requests\.(?:get|post|put|delete|patch|request|Session))"
    )
    for path in sorted(ALLOWED_READ_PATHS):
        if path.suffix != ".py":
            continue
        rel = path.relative_to(PROJECT_ROOT).as_posix()
        src = _safe_read(path)
        if request_usage_re.search(src):
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


def _runtime_surface_hash() -> str:
    """Deterministic hash over allowlisted runtime sources for cross-environment parity."""
    digest = hashlib.sha256()
    runtime_doc_root = RUNTIME_DOC_DIR.resolve()
    for path in sorted(ALLOWED_READ_PATHS):
        resolved = path.resolve()
        if resolved.is_relative_to(runtime_doc_root):
            # Exclude generated runtime docs to avoid self-referential hash drift.
            continue
        try:
            rel = resolved.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            rel = resolved.as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\n")
        if resolved.exists():
            digest.update(_stable_hash_bytes(resolved))
        digest.update(b"\n")
    return digest.hexdigest()


def _runtime_fingerprint(registry_enabled_ids: list[int]) -> dict[str, str]:
    runtime_surface_hash = _runtime_surface_hash()
    enabled_hash = hashlib.sha256(json.dumps(registry_enabled_ids, sort_keys=True).encode("utf-8")).hexdigest()
    payload = {
        "enabled_capability_ids": registry_enabled_ids,
        "runtime_surface_hash": runtime_surface_hash,
        "phase_marker": f"Build phase {BUILD_PHASE}",
    }
    runtime_fingerprint_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "runtime_surface_hash": runtime_surface_hash,
        "enabled_capability_ids_hash": enabled_hash,
        "runtime_fingerprint_hash": runtime_fingerprint_hash,
        "phase_marker": f"Build phase {BUILD_PHASE}",
    }


def _runtime_profile_context(registry: dict[str, Any]) -> dict[str, Any]:
    selected = os.getenv("NOVA_RUNTIME_PROFILE", "default").strip() or "default"
    profiles = registry.get("profiles") or {}
    if not isinstance(profiles, dict):
        return {"profile": selected, "groups": [], "known": False}
    profile = profiles.get(selected)
    if not isinstance(profile, dict):
        return {"profile": selected, "groups": [], "known": False}
    groups = profile.get("groups") or []
    if not isinstance(groups, list):
        groups = []
    return {"profile": selected, "groups": [str(g) for g in groups], "known": True}


def _phase_4_status(registry: dict[str, Any]) -> str:
    brain_src = _safe_read(BRAIN_SERVER_PATH)
    session_handler_src = _safe_read(SESSION_HANDLER_PATH)
    governor_src = _safe_read(GOVERNOR_PATH)
    enabled_ids = set(_enabled_registry_ids(registry))
    required_ids = {16, 17, 18, 19, 20, 21, 22, 31, 32, 48, 49, 50, 51, 52, 53, 54}

    foundation_present = all(
        path.exists()
        for path in (
            GOVERNOR_PATH,
            GOVERNOR_MEDIATOR_PATH,
            NETWORK_MEDIATOR_PATH,
            EXECUTE_BOUNDARY_PATH,
            PROJECT_ROOT / "nova_backend" / "src" / "governor" / "single_action_queue.py",
            PROJECT_ROOT / "nova_backend" / "src" / "governor" / "capability_registry.py",
            LEDGER_WRITER_PATH,
        )
    )
    execution_spine_wired = all(
        token in governor_src
        for token in ("ExecuteBoundary", "SingleActionQueue", "NetworkMediator", "LedgerWriter")
    )
    invocation_runtime_wired = (
        "GovernorMediator.parse_governed_invocation" in session_handler_src
        and "GovernorMediator.mediate" in session_handler_src
        and "handle_governed_invocation" in brain_src
    )
    capability_surface_complete = required_ids.issubset(enabled_ids)
    full_package_live = all(
        (
            foundation_present,
            execution_spine_wired,
            invocation_runtime_wired,
            capability_surface_complete,
            GOVERNED_ACTIONS_ENABLED is True,
        )
    )

    if BUILD_PHASE >= 5 and full_package_live:
        return "COMPLETE"
    if foundation_present and invocation_runtime_wired and GOVERNED_ACTIONS_ENABLED is True:
        return "ACTIVE"
    if foundation_present or GOVERNED_ACTIONS_ENABLED is True:
        return "PARTIAL"
    return "DESIGN"


def _phase_42_status() -> str:
    dashboard_src = _safe_read(STATIC_DASHBOARD_PATH)
    session_handler_src = _safe_read(SESSION_HANDLER_PATH)
    agents_present = (PROJECT_ROOT / "nova_backend" / "src" / "agents").exists()
    personality_present = (PROJECT_ROOT / "nova_backend" / "src" / "personality").exists()
    validation_present = (PROJECT_ROOT / "nova_backend" / "src" / "validation").exists()
    brain_src = _safe_read(BRAIN_SERVER_PATH)
    build_src = _safe_read(BUILD_PHASE_PATH)
    compile_gate_present = "PHASE_4_2_ENABLED" in build_src
    runtime_wired = all(
        token in "\n".join((brain_src, session_handler_src))
        for token in (
            "PersonalityAgent",
            "_extract_phase42_query",
            "_build_phase42_agents",
            "personality_agent.arm_deep_mode()",
            "phase42_message, apply_personality=False",
        )
    )
    report_surface_present = (
        "renderIntelligenceBriefWidget" in dashboard_src
        and "Follow-up analysis" in dashboard_src
        and "phase42: follow up on this report with deeper analysis" in dashboard_src
    )
    full_package_live = all(
        (
            agents_present,
            personality_present,
            validation_present,
            compile_gate_present,
            runtime_wired,
            report_surface_present,
            PHASE_4_2_ENABLED,
        )
    )

    if BUILD_PHASE >= 5 and full_package_live:
        return "COMPLETE"
    if (
        agents_present
        and personality_present
        and validation_present
        and compile_gate_present
        and runtime_wired
        and PHASE_4_2_ENABLED
    ):
        return "ACTIVE"
    return "DESIGN ONLY"


def _calendar_integration_present() -> bool:
    skill_registry_src = _safe_read(SKILL_REGISTRY_PATH).lower()
    governor_src = _safe_read(GOVERNOR_PATH).lower()
    # The calendar widget send lives in session_handler.py, not brain_server.py
    session_handler_src = _safe_read(SESSION_HANDLER_PATH)
    brain_src = _safe_read(BRAIN_SERVER_PATH).lower()
    dashboard_src = _safe_read(STATIC_DASHBOARD_PATH).lower()
    index_src = _safe_read(STATIC_INDEX_PATH).lower()
    parsed = GovernorMediator.parse_governed_invocation("calendar", session_id="audit-runtime")
    mediated_calendar = isinstance(parsed, Invocation) and parsed.capability_id == 57
    calendar_widget_wired = (
        'send_widget_message(ws, "calendar"' in session_handler_src
        and "last_calendar_summary" in brain_src
    )

    return (
        "calendarskill" in skill_registry_src
        and mediated_calendar
        and "req.capability_id == 57" in governor_src
        and calendar_widget_wired
        and 'case "calendar"' in dashboard_src
        and "morningstate.calendar" in dashboard_src
        and "coming soon" not in index_src
    )


def _phase_5_status(registry: dict[str, Any]) -> str:
    dashboard_src = _safe_read(STATIC_DASHBOARD_PATH)
    index_src = _safe_read(STATIC_INDEX_PATH)
    brain_src = _safe_read(BRAIN_SERVER_PATH)
    session_handler_src = _safe_read(SESSION_HANDLER_PATH)
    command_runtime_src = "\n".join((brain_src, session_handler_src))
    enabled_ids = set(_enabled_registry_ids(registry))
    phase_5_foundation_present = all(
        path.exists()
        for path in (
            PROJECT_ROOT / "nova_backend" / "src" / "memory" / "governed_memory_store.py",
            PROJECT_ROOT / "nova_backend" / "src" / "working_context" / "project_threads.py",
            PROJECT_ROOT / "nova_backend" / "src" / "personality" / "tone_profile_store.py",
            PROJECT_ROOT / "nova_backend" / "src" / "tasks" / "notification_schedule_store.py",
            PROJECT_ROOT / "nova_backend" / "src" / "patterns" / "pattern_review_store.py",
        )
    )
    memory_capability_enabled = 61 in enabled_ids
    memory_surface_present = (
        all(token in command_runtime_src for token in ("memory overview", "list memories", "memory show"))
        and "renderMemoryOverviewWidget" in dashboard_src
        and 'id="page-memory"' in index_src
    )
    continuity_surface_present = (
        "workspace home" in command_runtime_src
        and "renderWorkspaceHomeWidget" in dashboard_src
        and 'id="page-home"' in index_src
    )
    tone_surface_present = (
        "TONE_STATUS_COMMANDS" in command_runtime_src
        and "send_tone_profile_widget" in command_runtime_src
        and "showToneModal" in dashboard_src
        and "ToneProfileStore" in brain_src
    )
    scheduling_surface_present = (
        "show schedules" in command_runtime_src
        and "showScheduleModal" in dashboard_src
        and "NotificationScheduleStore" in brain_src
    )
    pattern_review_surface_present = (
        all(token in command_runtime_src for token in ("pattern status", "review patterns"))
        and "renderPatternReviewWidget" in dashboard_src
        and "PatternReviewStore" in brain_src
    )
    full_package_live = all(
        (
            phase_5_foundation_present,
            memory_capability_enabled,
            memory_surface_present,
            continuity_surface_present,
            tone_surface_present,
            scheduling_surface_present,
            pattern_review_surface_present,
        )
    )

    if BUILD_PHASE >= 6 and full_package_live:
        return "COMPLETE"
    if BUILD_PHASE >= 5 and phase_5_foundation_present and memory_capability_enabled:
        return "ACTIVE"
    if BUILD_PHASE >= 5 or memory_capability_enabled:
        return "PARTIAL"
    return "DESIGN"


def _phase_6_status() -> str:
    dashboard_src = _safe_read(STATIC_DASHBOARD_PATH)
    index_src = _safe_read(STATIC_INDEX_PATH)
    brain_src = _safe_read(BRAIN_SERVER_PATH)
    session_handler_src = _safe_read(SESSION_HANDLER_PATH)
    command_runtime_src = "\n".join((brain_src, session_handler_src))

    foundation_present = all(
        path.exists()
        for path in (
            ATOMIC_POLICY_STORE_PATH,
            POLICY_VALIDATOR_PATH,
            POLICY_EXECUTOR_GATE_PATH,
            CAPABILITY_TOPOLOGY_PATH,
        )
    )
    review_commands_present = all(
        token in command_runtime_src
        for token in (
            "policy overview",
            "policy simulate <id>",
            "policy run <id> once",
        )
    )
    review_surface_present = (
        "renderPolicyCenterPage" in dashboard_src
        and 'id="page-policy"' in index_src
        and "policy_overview" in dashboard_src
        and "policy_run" in dashboard_src
    )
    trust_loop_complete = (
        "renderTrustCenterPage" in dashboard_src
        and 'id="page-trust"' in index_src
        and 'id="trust-center-policy-summary"' in index_src
        and "policy_capability_readiness" in command_runtime_src
        and "selectedPolicyCapabilityKey" in dashboard_src
    )
    capability_map_present = (
        "getPolicyReadinessBuckets" in dashboard_src
        and 'id="policy-center-readiness"' in index_src
        and 'id="btn-policy-capability-map"' in index_src
        and "POLICY_CAPABILITY_MAP_COMMANDS" in command_runtime_src
        and "POLICY_CAPABILITY_MAP_VIEWED" in command_runtime_src
    )

    if foundation_present and review_commands_present and review_surface_present and trust_loop_complete and capability_map_present:
        return "COMPLETE"
    if foundation_present and review_commands_present and review_surface_present:
        return "ACTIVE"
    if foundation_present and review_commands_present:
        return "PARTIAL"
    if foundation_present:
        return "FOUNDATION"
    return "DESIGN"


def _governed_remote_bridge_present() -> bool:
    brain_src = _safe_read(BRAIN_SERVER_PATH)
    bridge_api_src = _safe_read(BRIDGE_API_PATH)
    return (
        "build_bridge_router" in brain_src
        and '"/api/openclaw/bridge/message"' in bridge_api_src
        and "openclaw_bridge" in bridge_api_src
    )


def _openclaw_home_agent_foundation_present() -> bool:
    dashboard_src = _safe_read(STATIC_DASHBOARD_PATH)
    index_src = _safe_read(STATIC_INDEX_PATH)
    agent_api_src = _safe_read(OPENCLAW_AGENT_API_PATH)
    return (
        OPENCLAW_AGENT_API_PATH.exists()
        and OPENCLAW_AGENT_RUNTIME_STORE_PATH.exists()
        and OPENCLAW_AGENT_RUNNER_PATH.exists()
        and OPENCLAW_AGENT_PERSONALITY_BRIDGE_PATH.exists()
        and 'id="page-agent"' in index_src
        and "renderOpenClawAgentPage" in dashboard_src
        and "/api/openclaw/agent/status" in agent_api_src
        and "home_agent_enabled" in agent_api_src
    )


def _connector_package_foundation_summary() -> dict[str, Any]:
    try:
        from src.connectors.package_registry import ConnectorPackageRegistry

        registry = ConnectorPackageRegistry()
    except Exception:
        return {"present": False, "active_count": 0, "package_ids": []}

    active_packages = registry.active_packages()
    return {
        "present": bool(active_packages),
        "active_count": len(active_packages),
        "package_ids": [package.id for package in active_packages],
    }


def _phase_8_status() -> str:
    if not _openclaw_home_agent_foundation_present():
        return "DESIGN"
    if OPENCLAW_AGENT_SCHEDULER_PATH.exists():
        return "ACTIVE"
    return "FOUNDATION"


def _phase_7_status(registry: dict[str, Any]) -> str:
    enabled_ids = set(_enabled_registry_ids(registry))
    dashboard_src = _safe_read(STATIC_DASHBOARD_PATH)
    index_src = _safe_read(STATIC_INDEX_PATH)
    governor_src = _safe_read(GOVERNOR_PATH)
    mediator_src = _safe_read(GOVERNOR_MEDIATOR_PATH)
    brain_src = _safe_read(BRAIN_SERVER_PATH)
    settings_api_src = _safe_read(SETTINGS_API_PATH)
    bridge_src = _safe_read(DEEPSEEK_BRIDGE_PATH)
    capability_enabled = 62 in enabled_ids
    executor_present = EXTERNAL_REASONING_EXECUTOR_PATH.exists()
    safety_wrapper_present = DEEPSEEK_SAFETY_WRAPPER_PATH.exists()
    gateway_mediated = "generate_chat" in bridge_src and "ollama.chat" not in bridge_src
    governor_wired = "req.capability_id == 62" in governor_src
    mediator_wired = "SECOND_OPINION_RE" in mediator_src and "second opinion" in MEDIATOR_TRIGGER_PROBES
    trust_surface_present = (
        'id="trust-center-reasoning-summary"' in index_src
        and 'id="trust-center-reasoning-grid"' in index_src
        and "trustReviewState.reasoningRuntime" in dashboard_src
        and "trust-center-reasoning-summary" in dashboard_src
    )
    settings_surface_present = (
        'id="settings-reasoning-summary"' in index_src
        and 'id="settings-reasoning-grid"' in index_src
        and "settings-reasoning-summary" in dashboard_src
    )
    settings_control_surface_present = (
        'id="settings-permission-summary"' in index_src
        and 'id="settings-permission-grid"' in index_src
        and "requestSettingsRuntimeRefresh(force = false)" in dashboard_src
        and "setRuntimePermission(permission, enabled)" in dashboard_src
    )
    runtime_support_present = (
        "_build_second_opinion_review_text" in brain_src
        and "reasoning_runtime" in brain_src
        and "build_settings_router" in brain_src
        and '"/api/settings/runtime"' in settings_api_src
    )

    if (
        BUILD_PHASE >= 7
        and capability_enabled
        and executor_present
        and safety_wrapper_present
        and gateway_mediated
        and governor_wired
        and mediator_wired
        and trust_surface_present
        and settings_surface_present
        and settings_control_surface_present
        and runtime_support_present
    ):
        return "COMPLETE"
    if capability_enabled and executor_present and gateway_mediated and governor_wired:
        return "ACTIVE"
    if capability_enabled or executor_present:
        return "PARTIAL"
    return "DESIGN"


def _phase_45_status() -> str:
    """Derive coarse runtime status for Phase 4.5 UX surface."""
    dashboard_src = _safe_read(STATIC_DASHBOARD_PATH)
    index_src = _safe_read(STATIC_INDEX_PATH)
    has_morning_panel = "Morning Dashboard" in index_src or "morning-widget" in index_src
    has_morning_state = "morningState" in dashboard_src
    trust_panel_present = "trust panel" in dashboard_src.lower() or "trust-panel" in index_src.lower()
    failure_ladder_present = (
        "failure_ladder" in _safe_read(BRAIN_SERVER_PATH).lower()
        or "failurestate" in dashboard_src.lower()
        or "offline-safe mode" in dashboard_src.lower()
    )
    calendar_present = _calendar_integration_present()
    all_surfaces_live = (
        has_morning_panel
        and has_morning_state
        and trust_panel_present
        and failure_ladder_present
        and calendar_present
    )

    if all_surfaces_live and BUILD_PHASE >= 5:
        return "COMPLETE"
    if all_surfaces_live:
        return "ACTIVE"
    if has_morning_panel and has_morning_state:
        return "PARTIAL"
    return "DESIGN ONLY"


def _known_runtime_gaps() -> list[str]:
    trust_panel_present = (
        "trust panel" in _safe_read(STATIC_DASHBOARD_PATH).lower()
        or "trust-panel" in _safe_read(STATIC_INDEX_PATH).lower()
    )
    failure_ladder_present = (
        "failure_ladder" in _safe_read(BRAIN_SERVER_PATH).lower()
        or "failurestate" in _safe_read(STATIC_DASHBOARD_PATH).lower()
        or "offline-safe mode" in _safe_read(STATIC_DASHBOARD_PATH).lower()
    )
    checks: list[tuple[str, bool]] = [
        (
            "Orthogonal Agent Stack (Phase 4.2)",
            (PROJECT_ROOT / "nova_backend" / "src" / "agents").exists()
            and (PROJECT_ROOT / "nova_backend" / "src" / "personality").exists(),
        ),
        ("Personality Validator Pipeline", (PROJECT_ROOT / "nova_backend" / "src" / "validation").exists()),
        ("Compile-time phase gating for 4.2 modules", "PHASE_4_2_ENABLED" in _safe_read(BUILD_PHASE_PATH)),
        ("Trust Panel system", trust_panel_present),
        ("Failure Mode Ladder", failure_ladder_present),
        ("Calendar integration", _calendar_integration_present()),
    ]
    if _openclaw_home_agent_foundation_present():
        checks.extend(
            [
                ("OpenClaw proactive scheduling (Phase 8.5)", (OPENCLAW_DIR / "agent_scheduler.py").exists()),
                (
                    "OpenClaw scheduler quiet-hours suppression",
                    "Held by quiet hours" in _safe_read(OPENCLAW_AGENT_RUNTIME_STORE_PATH)
                    and "delivery_policy_decision"
                    in _safe_read(PROJECT_ROOT / "nova_backend" / "src" / "tasks" / "notification_schedule_store.py"),
                ),
                (
                    "OpenClaw scheduler rate limiting",
                    "Held by rate limit" in _safe_read(OPENCLAW_AGENT_RUNTIME_STORE_PATH)
                    and "deliveries_last_hour_override" in _safe_read(OPENCLAW_AGENT_SCHEDULER_PATH),
                ),
                (
                    "Full Phase-8 governed envelope execution",
                    False,
                ),
            ]
        )
    return [label for label, implemented in checks if not implemented]


def _design_runtime_divergences(registry: dict[str, Any]) -> list[str]:
    divergences: list[str] = []

    if _phase_42_status() not in {"ACTIVE", "COMPLETE"}:
        divergences.append(
            "Phase 4.2 orthogonal cognition stack is still design-only or not fully wired at runtime."
        )

    if "PHASE_4_2_ENABLED" not in _safe_read(BUILD_PHASE_PATH):
        divergences.append(
            "Phase 4.2 compile-time gating contract is documented, but explicit BUILD_PHASE exclusion is not present."
        )

    trust_panel_present = (
        "trust panel" in _safe_read(STATIC_DASHBOARD_PATH).lower()
        or "trust-panel" in _safe_read(STATIC_INDEX_PATH).lower()
    )
    if not trust_panel_present:
        divergences.append(
            "Phase 4.5 Trust Panel requirement is not explicitly represented in dashboard runtime text."
        )
    if not _calendar_integration_present():
        divergences.append(
            "Phase 4.5 calendar integration requirement is not represented in runtime UI + skill surfaces."
        )

    phase_8_status = _phase_8_status()
    if phase_8_status == "FOUNDATION":
        divergences.append(
            "Phase 8 canonical governed automation remains only partially realized at runtime: "
            "manual OpenClaw home-agent foundations are live, but the narrow scheduler and full "
            "envelope-governed execution are still deferred."
        )

    return divergences


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
        "| id | name | enabled | status | phase_introduced | risk_level | data_exfiltration | authority_class | confirmation_required | reversible | external_effect | network_access | execution_surface | execution_gate | single_action_queue | ledger_allowlist | dns_rebinding_guard | timeout_guard |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {id} | {name} | {enabled} | {status} | {phase_introduced} | {risk_level} | {data_exfiltration} | {authority_class} | {confirmation_required} | {reversible} | {external_effect} | {network_access} | {execution_surface} | {execution_gate} | {single_action_queue} | {ledger_allowlist} | {dns_rebinding_guard} | {timeout_guard} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Derivation notes",
            "",
            "- authority_class / confirmation_required / reversible / external_effect use explicit registry governance metadata when present; older stub inputs fall back to legacy heuristics.",
            "- network_access is derived from explicit `read_only_network` authority or from Governor execution branches that pass `self.network` to an executor.",
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
            "- Legacy sealed skill shims that are not registered in `src/skill_registry.py` are intentionally omitted from this live runtime map.",
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
        f"- runtime_surface_hash: {fp['runtime_surface_hash']}",
        f"- enabled_capability_ids_hash: {fp['enabled_capability_ids_hash']}",
        f"- runtime_fingerprint_hash: {fp['runtime_fingerprint_hash']}",
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
    for rel_path in ("src/conversation/deepseek_bridge.py", "src/skills/general_chat.py", "src/openclaw/agent_runner.py"):
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
            f"  C{row['id']} --> C{row['id']}A[authority={row['authority_class']}, risk={row['risk_level']}, confirm={row['confirmation_required']}, reversible={row['reversible']}, external={row['external_effect']}, network={row['network_access']}, surface={row['execution_surface']}]"
        )
    lines.append("  Runtime --> Routes[Skill Routes]")
    for route in skill_routes:
        lines.append(f"  Routes --> R{route['capability_id']}_{route['name']}[{route['name']} -> capability {route['capability_id']}]")
    lines.append("  Runtime --> LLM[Conversation/Model Surfaces]")
    for module in llm_gateway_users:
        key = module.replace("/", "_").replace(".", "_")
        lines.append(f"  LLM --> {key}[{module} uses llm_gateway.generate_chat]")
    lines.extend(["```", "", "```text", "Runtime", f"|- Enabled IDs: {enabled}", f"|- Disabled IDs: {disabled}", "|- Governor Guards"])
    lines.extend(
        [
            f"|  |- execution_gate: {enforcement['execution_gate_enabled']}",
            f"|  |- single_action_queue: {enforcement['single_action_queue_enforced']}",
            "|  |- ledger_allowlist: True",
            f"|  |- dns_rebinding_guard: {enforcement['dns_rebinding_protection_active']}",
            f"|  |- timeout_guard: {enforcement['execution_timeout_guard_active']}",
            "|- Capabilities",
        ]
    )
    for row in rows:
        lines.append(
            f"|  |- {row['id']} {row['name']} (authority={row['authority_class']}, risk={row['risk_level']}, network={row['network_access']}, exfil={row['data_exfiltration']}, confirm={row['confirmation_required']}, surface={row['execution_surface']})"
        )
    lines.append("|- Skill -> capability routes")
    for route in skill_routes:
        lines.append(f"|  |- {route['name']} -> {route['capability_id']}")
    lines.append("|- Conversation/model surfaces")
    for module in llm_gateway_users:
        lines.append(f"   |- {module} -> llm_gateway.generate_chat")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def render_current_runtime_state_markdown(report: dict[str, Any], registry: dict[str, Any]) -> str:
    capabilities = registry.get("capabilities", [])
    enabled_ids = sorted(int(item["id"]) for item in capabilities if item.get("enabled") is True)
    disabled_ids = sorted(int(item["id"]) for item in capabilities if item.get("enabled") is not True)
    governance_rows = _derive_capability_governance_rows(registry)
    enforcement = _governor_enforcement_summary()
    bridge_surface_present = _governed_remote_bridge_present()
    openclaw_home_agent_present = _openclaw_home_agent_foundation_present()
    connector_package_summary = _connector_package_foundation_summary()
    fingerprint = _runtime_fingerprint(enabled_ids)
    known_gaps = _known_runtime_gaps()
    design_divergences = _design_runtime_divergences(registry)
    profile_context = _runtime_profile_context(registry)
    phase_4_status = _phase_4_status(registry)
    phase_42_status = _phase_42_status()
    phase_45_status = _phase_45_status()
    phase_5_status = _phase_5_status(registry)
    phase_6_status = _phase_6_status()
    phase_7_status = _phase_7_status(registry)
    phase_8_status = _phase_8_status()

    if phase_4_status == "COMPLETE":
        phase_4_note = "Governed execution spine, mediation, queueing, ledger, and boundary controls are complete and sealed"
    elif phase_4_status == "ACTIVE":
        phase_4_note = "Governed execution runtime"
    elif phase_4_status == "PARTIAL":
        phase_4_note = "Governed execution foundations present but not fully sealed"
    else:
        phase_4_note = "Governed execution remains design-only"
    phase_42_note = (
        "Orthogonal cognition stack, deep-mode arming, and report surfaces are complete and sealed"
        if phase_42_status == "COMPLETE"
        else "Orthogonal cognition stack enabled via explicit invocation path"
        if phase_42_status == "ACTIVE"
        else "Orthogonal cognition stack not enabled in runtime"
    )
    if phase_45_status == "COMPLETE":
        phase_45_note = "UX, trust, failure ladder, and calendar surfaces complete and sealed"
    elif phase_45_status == "ACTIVE":
        phase_45_note = "UX trust, failure ladder, and calendar surfaces implemented"
    elif phase_45_status == "PARTIAL":
        phase_45_note = "UX elements present but incomplete"
    else:
        phase_45_note = "Experience layer remains design-only"
    if phase_5_status == "COMPLETE":
        phase_5_note = (
            "Governed memory, continuity, tone, scheduling, and pattern-review "
            "surfaces are complete and sealed"
        )
    elif phase_5_status == "ACTIVE":
        phase_5_note = (
            "Governed memory, continuity, tone, scheduling, and pattern-review "
            "surfaces active; closure state tracked in Phase-5 proof packet"
        )
    elif phase_5_status == "PARTIAL":
        phase_5_note = "Build phase promoted with partial memory/continuity runtime activation"
    else:
        phase_5_note = "Memory continuity planned"
    if phase_6_status == "COMPLETE":
        phase_6_note = (
            "Trust loop, policy review, capability authority map, and manual policy executor gate "
            "are complete; delegated trigger runtime remains disabled by design"
        )
    elif phase_6_status == "ACTIVE":
        phase_6_note = (
            "Atomic policy draft foundation, executor-gate simulation, capability topology, "
            "and Policy Review Center active; trigger runtime remains disabled"
        )
    elif phase_6_status == "PARTIAL":
        phase_6_note = "Phase-6 policy foundation is in code, but the full review surface is incomplete"
    elif phase_6_status == "FOUNDATION":
        phase_6_note = "Phase-6 policy substrate exists in code, but no user-facing review surface is active"
    else:
        phase_6_note = "Delegated policy layer remains design-only"
    if phase_7_status == "COMPLETE":
        phase_7_note = (
            "Governed external reasoning is complete: answer-first research surfaces, explicit second-opinion capability, "
            "provider transparency, actionable Settings controls, and advisory-only trust explanation are active"
        )
    elif phase_7_status == "ACTIVE":
        phase_7_note = "Governed external reasoning is active, but not all user-facing transparency surfaces are complete"
    elif phase_7_status == "PARTIAL":
        phase_7_note = "Phase-7 reasoning substrate exists, but the full routed user-facing slice is incomplete"
    else:
        phase_7_note = "Governed external reasoning remains design-only"
    if phase_8_status == "ACTIVE":
        phase_8_note = (
            "Manual strict preflight is active. Scheduled home-agent runtime is available behind explicit settings control, "
            "with quiet-hours suppression, rate limiting, explicit envelope preview, measured narrow-lane run usage visibility, "
            "local-first metered OpenAI fallback for narrow task reports, and bounded assistive noticing live; "
            "broader envelope-governed execution still remains deferred"
        )
    elif phase_8_status == "FOUNDATION":
        preflight_note = "Manual strict preflight is active. " if OPENCLAW_STRICT_PREFLIGHT_PATH.exists() else ""
        phase_8_note = (
            preflight_note
            + "Manual OpenClaw home-agent briefing templates, delivery controls, operator surface, and local-first metered OpenAI fallback are live; "
            "scheduled automation and full Phase-8 execution enforcement remain deferred"
        )
    else:
        phase_8_note = "Phase-8 home-agent and governed external execution remain design-only"

    governor_modules = [
        "src/governor/governor.py",
        "src/governor/governor_mediator.py",
        "src/governor/capability_registry.py",
        "src/governor/execute_boundary/execute_boundary.py",
        "src/governor/network_mediator.py",
        "src/ledger/writer.py",
    ]

    executor_count = len([p for p in EXECUTORS_DIR.glob("*.py") if p.name != "__init__.py"])
    skill_count = len([row for row in _skill_surface_rows() if row.get("surface_type") == "skill"])
    fingerprint_payload = {
        "enabled_capability_ids": enabled_ids,
        "governor_modules": governor_modules,
        "executor_count": executor_count,
        "skill_count": skill_count,
        "runtime_surface_hash": fingerprint["runtime_surface_hash"],
        "phase_marker": fingerprint["phase_marker"],
    }
    runtime_hash = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    lines = [
        "# NOVA - CURRENT RUNTIME STATE",
        "",
        f"Runtime Fingerprint: {runtime_hash}",
        "Generated By: scripts/generate_runtime_docs.py",
        "",
        "Authoritative Source: Runtime codebase",
        "Manual edits: NOT PERMITTED",
        "",
        "## Phase Activation Matrix",
        "",
        "| Phase | Status | Notes |",
        "| --- | --- | --- |",
        "| Phase 3.5 | COMPLETE | Governance baseline sealed |",
        f"| Phase 4 | {phase_4_status} | {phase_4_note} |",
        f"| Phase 4.2 | {phase_42_status} | {phase_42_note} |",
        f"| Phase 4.5 | {phase_45_status} | {phase_45_note} |",
        f"| Phase 5 | {phase_5_status} | {phase_5_note} |",
        f"| Phase 6 | {phase_6_status} | {phase_6_note} |",
        f"| Phase 7 | {phase_7_status} | {phase_7_note} |",
        f"| Phase 8 | {phase_8_status} | {phase_8_note} |",
        "",
        "## Runtime Governance Spine",
        "",
        "Execution Authority Model:",
        "User -> GovernorMediator -> Governor -> CapabilityRegistry -> SingleActionQueue -> LedgerWriter -> ExecuteBoundary -> Executor",
        "",
        "Components:",
        "",
        "GovernorMediator",
        "Role: Invocation router and policy enforcement",
        "Location: src/governor/governor_mediator.py",
        "",
        "CapabilityRegistry",
        "Role: Capability enablement control",
        "Location: src/governor/capability_registry.py",
        "",
        "ExecuteBoundary",
        "Role: Final execution permission gate",
        "Location: src/governor/execute_boundary/execute_boundary.py",
        "",
        "NetworkMediator",
        "Role: Enforced outbound HTTP control",
        "Location: src/governor/network_mediator.py",
        "",
        "LedgerWriter",
        "Role: Append-only audit logging",
        "Location: src/ledger/writer.py",
        "",
        "## Runtime Profile",
        "",
        f"- Active profile: {profile_context['profile']}",
        f"- Enabled groups: {profile_context['groups']}",
        "",
        "## Active Capabilities",
        "",
        "| ID | Name | Description |",
        "| --- | --- | --- |",
    ]

    for row in governance_rows:
        if row["enabled"]:
            description = str(row.get("description") or "").strip() or "Governed runtime capability"
            lines.append(f"| {row['id']} | {row['name']} | {description} |")

    lines.extend(
        [
            "",
        "| ID | Capability | Registry Status | Runtime Enabled | Runtime State |",
        "| --- | --- | --- | --- | --- |",
        ]
    )

    for row in governance_rows:
        runtime_state = "ACTIVE" if row["enabled"] and row["status"] == "active" else "INACTIVE"
        lines.append(
            f"| {row['id']} | {row['name']} | {row['status'].upper()} | {str(row['enabled'])} | {runtime_state} |"
        )

    lines.extend(
        [
            "",
            "## Runtime Systems",
            "",
            "Conversation Router",
            "Location: src/conversation",
            "Status: Active",
            "",
            "Deep Analysis Bridge",
            "Location: src/conversation/deepseek_bridge.py",
            "Status: Contained analysis-only",
            "",
            *(
                [
                    "Governed Remote Bridge",
                    "Location: src/api/bridge_api.py (/api/openclaw/bridge/*)",
                    "Status: Token-gated read/reasoning ingress active",
                    "",
                ]
                if bridge_surface_present
                else []
            ),
            *(
                [
                    "OpenClaw Home Agent Foundation",
                    "Location: src/openclaw + src/api/openclaw_agent_api.py",
                    "Status: Manual briefing templates, delivery controls, and operator surface active",
                    "",
                ]
                if openclaw_home_agent_present
                else []
            ),
            *(
                [
                    "Metered OpenAI Task-Report Lane",
                    "Location: src/providers/openai_responses_lane.py",
                    "Status: Local-first narrow fallback for OpenClaw task reports only",
                    "",
                ]
                if OPENAI_RESPONSES_LANE_PATH.exists()
                else []
            ),
            *(
                [
                    "Governed Connector Package Foundation",
                    "Location: src/connectors/package_registry.py + src/config/connector_packages.json",
                    "Status: "
                    + f"{connector_package_summary['active_count']} active package manifests "
                    + f"({', '.join(connector_package_summary['package_ids'])}) present as a governed connector rollout foundation",
                    "",
                ]
                if connector_package_summary["present"]
                else []
            ),
            *(
                [
                    "Assistive Noticing",
                    "Location: src/working_context/assistive_noticing.py",
                    "Status: Bounded suggestion-only notices with handled state and Trust review active",
                    "",
                ]
                if ASSISTIVE_NOTICING_PATH.exists()
                else []
            ),
            "Voice System",
            "Location: src/voice",
            "Status: Active",
            "",
            "WebSocket Interface",
            "Location: src/websocket/session_handler.py + src/brain_server.py",
            "Status: Active",
            "",
            "Dashboard UI",
            "Location: static/",
            "Status: Active",
            "",
            "## Known Runtime Gaps",
            "",
            "Not Implemented Yet",
            "",
        ]
    )

    if known_gaps:
        lines.extend(f"- {gap}" for gap in known_gaps)
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "Operational / QA Follow-Through",
            "",
            "- Live-device spoken-output validation remains recommended for the local TTS path",
        ]
    )

    lines.extend(
        [
            "",
            "## Runtime Invariants",
            "",
            "- No broad autonomy",
            "- No hidden background execution outside the explicit OpenClaw scheduler carve-out",
            "- All actions must pass GovernorMediator",
            "- All outbound HTTP must pass NetworkMediator",
            "- All execution logged to ledger",
            "",
            "## Runtime Fingerprint",
            "",
            f"- Capabilities enabled: {enabled_ids}",
            f"- Capabilities disabled: {disabled_ids}",
            f"- Capability Count: {len(enabled_ids)}",
            f"- Governor Modules: {len(governor_modules)}",
            f"- Executors: {executor_count}",
            f"- Skills: {skill_count}",
            f"- Runtime Surface Hash: {fingerprint['runtime_surface_hash']}",
            "",
            f"- Hash: {runtime_hash}",
            "",
            "## Runtime Truth Discrepancies",
            "",
        ]
    )

    discrepancies = report.get("discrepancies", [])
    if discrepancies:
        for item in discrepancies:
            lines.append(
                f"- [{item.get('severity', 'unknown')}] {item.get('code', 'UNKNOWN')}: {item.get('message', '')}"
            )
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Design Runtime Divergences",
            "",
        ]
    )
    if design_divergences:
        lines.extend(f"- {item}" for item in design_divergences)
    else:
        lines.append("- None")

    lines.append("")
    return "\n".join(lines)


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
