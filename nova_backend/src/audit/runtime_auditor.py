from __future__ import annotations

"""Wave B1 runtime-truth instrumentation facade.

The pre-B1 auditor is preserved in ``runtime_auditor_core``.  This module is the
stable import path used by Nova runtime/tests and adds only the instrumentation
repairs required by Wave B1:

- direct-network findings participate in discrepancy state;
- known NetworkMediator exceptions are explicit and classified;
- Phase 9 status uses import/symbol evidence instead of retired placeholder files;
- runtime fingerprints cover behaviorally active source families;
- generated runtime invariants are scoped to what the auditor actually proves.

Keeping the existing implementation intact behind this facade makes the B1 diff
reviewable while avoiding a risky rewrite of the mature generator.
"""

import hashlib
import importlib
import json
from pathlib import Path
from typing import Any

from . import runtime_auditor_core as _core


# ---------------------------------------------------------------------------
# Stable core export / compatibility
# ---------------------------------------------------------------------------

# Re-export the pre-B1 auditor surface, including underscore helpers used by
# existing tests and internal tooling. Targeted names are replaced below.
for _name in dir(_core):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_core, _name)


KNOWN_NETWORK_MEDIATOR_EXCEPTIONS: dict[str, dict[str, str]] = {
    "nova_backend/src/api/connections_api.py": {
        "classification": "local_administrative_health_probe",
        "disposition": "pending_explicit_runtime_governance_disposition",
        "reason": (
            "Provider-health requests are local administrative connection checks, "
            "not registered governed capability execution. The direct network path "
            "remains visible and does not become implicitly approved."
        ),
    }
}

FINGERPRINT_SCOPE_VERSION = "behaviorally_active_v2"
_FINGERPRINT_EXTRA_SOURCE_DIRS = (
    "audit",
    "brain",
    "connections",
    "governor",
    "identity",
    "memory",
    "patterns",
    "policies",
    "routers",
    "trust",
    "utils",
    "validation",
    "voice",
)

_PHASE9_REQUIRED_SYMBOLS = (
    ("src.openclaw.thinking_loop", "ThinkingLoop"),
    ("src.openclaw.tool_registry", "ToolRegistry"),
    ("src.openclaw.execution_memory", "ExecutionMemory"),
    ("src.openclaw.agent_personality_bridge", "OpenClawAgentPersonalityBridge"),
    ("src.identity.nova_self_awareness", "build_self_awareness_block"),
)


# ---------------------------------------------------------------------------
# Core-global synchronization
# ---------------------------------------------------------------------------

_SYNCABLE_CORE_GLOBALS = (
    "PROJECT_ROOT",
    "RUNTIME_DOC_DIR",
    "RUNTIME_DOC_PATH",
    "CANONICAL_RUNTIME_DOC_PATH",
    "GOVERNANCE_MATRIX_PATH",
    "SKILL_SURFACE_MAP_PATH",
    "BYPASS_SURFACES_PATH",
    "RUNTIME_FINGERPRINT_PATH",
    "GOVERNANCE_MATRIX_TREE_PATH",
    "ROUTE_PROTECTION_COVERAGE_PATH",
    "ALLOWED_READ_PATHS",
    "BUILD_PHASE",
    "GOVERNED_ACTIONS_ENABLED",
    "OPENCLAW_DIR",
    "OPENCLAW_AGENT_API_PATH",
    "OPENCLAW_AGENT_RUNTIME_STORE_PATH",
    "OPENCLAW_AGENT_RUNNER_PATH",
    "OPENCLAW_AGENT_PERSONALITY_BRIDGE_PATH",
    "OPENCLAW_AGENT_SCHEDULER_PATH",
    "STATIC_DASHBOARD_PATH",
    "STATIC_DASHBOARD_MODULAR_PATHS",
    "STATIC_INDEX_PATH",
    "BRAIN_SERVER_PATH",
    "SESSION_HANDLER_PATH",
    "BRIDGE_API_PATH",
    "SETTINGS_API_PATH",
    "GOVERNOR_PATH",
    "GOVERNOR_MEDIATOR_PATH",
    "NETWORK_MEDIATOR_PATH",
    "LEDGER_WRITER_PATH",
    "SKILL_REGISTRY_PATH",
    "STT_ROUTER_PATH",
    "ATOMIC_POLICY_STORE_PATH",
    "POLICY_VALIDATOR_PATH",
    "POLICY_EXECUTOR_GATE_PATH",
    "CAPABILITY_TOPOLOGY_PATH",
    "EXTERNAL_REASONING_EXECUTOR_PATH",
    "DEEPSEEK_SAFETY_WRAPPER_PATH",
    "DEEPSEEK_BRIDGE_PATH",
    "DEEPSEEK_PROVIDER_PATH",
)


def _sync_core_globals() -> None:
    """Propagate facade monkeypatches/constants into the preserved core module."""

    for name in _SYNCABLE_CORE_GLOBALS:
        if name in globals():
            setattr(_core, name, globals()[name])

    # These helpers are frequently monkeypatched by tests. Propagate the
    # facade's current value on every call so monkeypatch teardown restores the
    # preserved core as well.
    for helper_name in (
        "_safe_read",
        "_load_registry",
        "_openclaw_home_agent_foundation_present",
        "_connector_package_foundation_summary",
        "_phase_5_status",
        "_phase_6_status",
        "_phase_7_status",
        "_phase_8_status",
    ):
        helper = globals().get(helper_name)
        if helper is None:
            continue
        wrapper = _B1_WRAPPERS.get(helper_name)
        if wrapper is not None and helper is wrapper:
            setattr(_core, helper_name, _ORIGINAL_EXPORTS[helper_name])
        else:
            setattr(_core, helper_name, helper)


_ORIGINAL_EXPORTS = {
    name: globals().get(name)
    for name in (
        "_safe_read",
        "_load_registry",
        "_openclaw_home_agent_foundation_present",
        "_connector_package_foundation_summary",
        "_phase_5_status",
        "_phase_6_status",
        "_phase_7_status",
        "_phase_8_status",
    )
}
_B1_WRAPPERS: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Direct-network discrepancy truth
# ---------------------------------------------------------------------------

_ORIGINAL_BUILD_DISCREPANCIES = _core._build_discrepancies
_ORIGINAL_RENDER_BYPASS = _core.render_bypass_surfaces_markdown
_ORIGINAL_RUN_AUDIT = _core.run_runtime_truth_audit


def _classify_direct_network_paths(paths: list[str] | None = None) -> dict[str, Any]:
    _sync_core_globals()
    offenders = sorted(set(paths if paths is not None else _core._find_requests_usage_outside_network_mediator()))
    known: list[dict[str, str]] = []
    unclassified: list[str] = []

    for path in offenders:
        metadata = KNOWN_NETWORK_MEDIATOR_EXCEPTIONS.get(path)
        if metadata is None:
            unclassified.append(path)
            continue
        known.append({"path": path, **metadata})

    return {
        "detected_paths": offenders,
        "known_exceptions": known,
        "unclassified_paths": unclassified,
    }


def _build_discrepancies(
    runtime_doc_enabled_ids: list[int],
    registry_enabled_ids: list[int],
    mediator_mapped_ids: list[int],
    model_path_signals: dict[str, Any],
    execution_gate_enabled: bool,
) -> list[Discrepancy]:
    _sync_core_globals()
    discrepancies = list(
        _ORIGINAL_BUILD_DISCREPANCIES(
            runtime_doc_enabled_ids=runtime_doc_enabled_ids,
            registry_enabled_ids=registry_enabled_ids,
            mediator_mapped_ids=mediator_mapped_ids,
            model_path_signals=model_path_signals,
            execution_gate_enabled=execution_gate_enabled,
        )
    )

    network = _classify_direct_network_paths()
    known = network["known_exceptions"]
    unknown = network["unclassified_paths"]

    if known:
        discrepancies.append(
            Discrepancy(
                severity="warning",
                code="KNOWN_DIRECT_NETWORK_EXCEPTION",
                message=(
                    "Known direct-network path(s) exist outside NetworkMediator and "
                    "remain explicitly classified pending disposition."
                ),
                details={"exceptions": known},
            )
        )

    if unknown:
        discrepancies.append(
            Discrepancy(
                severity="hard_fail",
                code="UNCLASSIFIED_DIRECT_NETWORK_PATH",
                message=(
                    "Direct requests/network usage was detected outside NetworkMediator "
                    "without an explicit exception classification."
                ),
                details={"paths": unknown},
            )
        )

    return discrepancies


_core._build_discrepancies = _build_discrepancies


def render_bypass_surfaces_markdown() -> str:
    _sync_core_globals()
    base = _ORIGINAL_RENDER_BYPASS().rstrip()
    classification = _classify_direct_network_paths()

    lines = [
        base,
        "",
        "## Direct-network classification",
        "",
        "Detected direct-network paths are not silently treated as mediated. Known exceptions remain visible until explicitly disposed.",
        "",
    ]

    if classification["known_exceptions"]:
        for item in classification["known_exceptions"]:
            lines.extend(
                [
                    f"- `{item['path']}`",
                    f"  - classification: `{item['classification']}`",
                    f"  - disposition: `{item['disposition']}`",
                    f"  - reason: {item['reason']}",
                ]
            )
    else:
        lines.append("- Known exceptions: None detected.")

    if classification["unclassified_paths"]:
        lines.append("")
        lines.append("Unclassified direct-network paths:")
        lines.extend(f"- `{path}`" for path in classification["unclassified_paths"])
    else:
        lines.extend(["", "- Unclassified direct-network paths: None detected."])

    lines.append("")
    return "\n".join(lines)


_core.render_bypass_surfaces_markdown = render_bypass_surfaces_markdown


# ---------------------------------------------------------------------------
# Phase 9 live implementation evidence
# ---------------------------------------------------------------------------


def _phase_9_live_evidence() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for module_name, symbol_name in _PHASE9_REQUIRED_SYMBOLS:
        entry: dict[str, Any] = {
            "module": module_name,
            "symbol": symbol_name,
            "imported": False,
            "symbol_present": False,
        }
        try:
            module = importlib.import_module(module_name)
            entry["imported"] = True
            symbol = getattr(module, symbol_name, None)
            entry["symbol_present"] = symbol is not None and (
                isinstance(symbol, type) or callable(symbol)
            )
        except Exception as exc:  # report truth; do not hide import failures
            entry["error"] = f"{type(exc).__name__}: {exc}"
        checks.append(entry)

    return {
        "checks": checks,
        "all_required_symbols_live": all(
            item["imported"] and item["symbol_present"] for item in checks
        ),
    }


def _phase_9_status(registry: dict[str, Any]) -> str:
    evidence = _phase_9_live_evidence()
    enabled_ids = set(_core._enabled_registry_ids(registry))
    cap63 = 63 in enabled_ids

    if evidence["all_required_symbols_live"] and cap63:
        return "ACTIVE"
    if evidence["all_required_symbols_live"] or cap63:
        return "PARTIAL"
    return "DESIGN"


_core._phase_9_status = _phase_9_status


# ---------------------------------------------------------------------------
# Behaviorally active fingerprint scope
# ---------------------------------------------------------------------------


def _behaviorally_active_fingerprint_paths() -> frozenset[Path]:
    _sync_core_globals()
    paths = set(_core.ALLOWED_READ_PATHS)
    source_root = Path(_core.PROJECT_ROOT) / "nova_backend" / "src"

    # The existing allowlist remains the audit read boundary. Fingerprint
    # coverage is intentionally broader because generated runtime claims depend
    # on behavior in these active source families too.
    for directory_name in _FINGERPRINT_EXTRA_SOURCE_DIRS:
        directory = source_root / directory_name
        if directory.exists():
            paths.update(directory.rglob("*.py"))

    paths.add(Path(__file__).resolve())
    core_path = Path(getattr(_core, "__file__", "")).resolve()
    if core_path.exists():
        paths.add(core_path)

    return frozenset(path.resolve() for path in paths)


def _runtime_surface_hash() -> str:
    digest = hashlib.sha256()
    runtime_doc_root = Path(_core.RUNTIME_DOC_DIR).resolve()

    for path in sorted(_behaviorally_active_fingerprint_paths()):
        resolved = path.resolve()
        if resolved.is_relative_to(runtime_doc_root):
            continue
        try:
            rel = resolved.relative_to(_core.PROJECT_ROOT).as_posix()
        except ValueError:
            rel = resolved.as_posix()
        digest.update(rel.encode("utf-8"))
        digest.update(b"\n")
        if resolved.exists():
            digest.update(_core._stable_hash_bytes(resolved))
        digest.update(b"\n")

    return digest.hexdigest()


def _runtime_fingerprint(registry_enabled_ids: list[int]) -> dict[str, Any]:
    runtime_surface_hash = _runtime_surface_hash()
    enabled_hash = hashlib.sha256(
        json.dumps(registry_enabled_ids, sort_keys=True).encode("utf-8")
    ).hexdigest()
    paths = _behaviorally_active_fingerprint_paths()
    payload = {
        "enabled_capability_ids": registry_enabled_ids,
        "runtime_surface_hash": runtime_surface_hash,
        "phase_marker": f"Build phase {_core.BUILD_PHASE}",
        "scope_version": FINGERPRINT_SCOPE_VERSION,
    }
    runtime_fingerprint_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "runtime_surface_hash": runtime_surface_hash,
        "enabled_capability_ids_hash": enabled_hash,
        "runtime_fingerprint_hash": runtime_fingerprint_hash,
        "phase_marker": f"Build phase {_core.BUILD_PHASE}",
        "scope_version": FINGERPRINT_SCOPE_VERSION,
        "runtime_surface_file_count": len(paths),
    }


_core._runtime_surface_hash = _runtime_surface_hash
_core._runtime_fingerprint = _runtime_fingerprint


def render_runtime_fingerprint_markdown(registry_enabled_ids: list[int]) -> str:
    fp = _runtime_fingerprint(registry_enabled_ids)
    return "\n".join(
        [
            "# RUNTIME_FINGERPRINT",
            "",
            f"- runtime_surface_hash: {fp['runtime_surface_hash']}",
            f"- enabled_capability_ids_hash: {fp['enabled_capability_ids_hash']}",
            f"- runtime_fingerprint_hash: {fp['runtime_fingerprint_hash']}",
            f"- phase_marker: {fp['phase_marker']}",
            f"- scope_version: {fp['scope_version']}",
            f"- runtime_surface_file_count: {fp['runtime_surface_file_count']}",
            "",
        ]
    )


_core.render_runtime_fingerprint_markdown = render_runtime_fingerprint_markdown


# ---------------------------------------------------------------------------
# Report/current-state rendering with scoped claims
# ---------------------------------------------------------------------------


def run_runtime_truth_audit() -> dict[str, Any]:
    _sync_core_globals()
    report = _ORIGINAL_RUN_AUDIT()
    checks = report.setdefault("checks", {})
    checks["direct_network_paths"] = _classify_direct_network_paths()
    checks["phase_9_live_evidence"] = _phase_9_live_evidence()
    checks["fingerprint_scope"] = {
        "scope_version": FINGERPRINT_SCOPE_VERSION,
        "runtime_surface_file_count": len(_behaviorally_active_fingerprint_paths()),
    }
    return report


_core.run_runtime_truth_audit = run_runtime_truth_audit

_ORIGINAL_RENDER_CURRENT_STATE = _core.render_current_runtime_state_markdown


def _phase_9_note(registry: dict[str, Any]) -> str:
    evidence = _phase_9_live_evidence()
    live = [
        f"{item['module']}.{item['symbol']}"
        for item in evidence["checks"]
        if item["imported"] and item["symbol_present"]
    ]
    cap63 = 63 in set(_core._enabled_registry_ids(registry))
    return (
        "Import/symbol evidence: "
        + (", ".join(live) if live else "no required Phase 9 symbols confirmed")
        + f"; capability 63 enabled={cap63}."
    )


def render_current_runtime_state_markdown(report: dict[str, Any], registry: dict[str, Any]) -> str:
    _sync_core_globals()
    markdown = _ORIGINAL_RENDER_CURRENT_STATE(report, registry)

    # Replace the Phase 9 row with evidence the generator actually measured.
    phase9_status = _phase_9_status(registry)
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        if line.startswith("| Phase 9 |"):
            lines[index] = f"| Phase 9 | {phase9_status} | {_phase_9_note(registry)} |"
            break

    # Qualify generated governance language.  The generated artifact describes
    # the governed capability plane and detected exceptions; it does not prove a
    # whole-repository absolute.
    replacements = {
        "Role: Enforced outbound HTTP control": (
            "Role: Primary outbound HTTP control for mediated paths; detected exceptions are reported separately"
        ),
        "- All actions must pass GovernorMediator": (
            "- Registered governed capability execution inspected here routes through GovernorMediator"
        ),
        "- All outbound HTTP must pass NetworkMediator": (
            "- Outbound network paths are mediated where wired; detected direct-network exceptions are reported separately"
        ),
        "- All execution logged to ledger": (
            "- Governed execution paths inspected by this auditor include ledger evidence; this is not a whole-repository persistence claim"
        ),
    }
    lines = [replacements.get(line, line) for line in lines]

    # Make fingerprint scope visible beside the generated hash.
    fp = _runtime_fingerprint(_core._enabled_registry_ids(registry))
    for index, line in enumerate(lines):
        if line.startswith("- Runtime Surface Hash:"):
            lines.insert(index + 1, f"- Runtime Surface Scope: {fp['scope_version']} ({fp['runtime_surface_file_count']} files)")
            break

    # Add an explicit scope statement before the invariant block.
    try:
        invariant_index = lines.index("## Runtime Invariants")
    except ValueError:
        invariant_index = -1
    if invariant_index >= 0:
        scope_block = [
            "## Generated Evidence Scope",
            "",
            "- This artifact reports only properties mechanically inspected by the runtime auditor.",
            "- File/symbol presence is not treated as behavioral proof unless the corresponding check explicitly imports or exercises that surface.",
            "- Known direct-network exceptions remain discrepancies/warnings until explicitly dispositioned; they are not hidden by global invariants.",
            "",
        ]
        lines[invariant_index:invariant_index] = scope_block

    return "\n".join(lines).rstrip() + "\n"


_core.render_current_runtime_state_markdown = render_current_runtime_state_markdown


# ---------------------------------------------------------------------------
# Compatibility wrappers for existing monkeypatch-heavy tests/callers
# ---------------------------------------------------------------------------


def _derive_capability_governance_rows(registry: dict[str, Any]) -> list[dict[str, Any]]:
    _sync_core_globals()
    return _core._derive_capability_governance_rows(registry)


def _calendar_integration_present() -> bool:
    _sync_core_globals()
    return _core._calendar_integration_present()


def _phase_5_status(registry: dict[str, Any]) -> str:
    _sync_core_globals()
    return _core._phase_5_status(registry)


def _phase_6_status() -> str:
    _sync_core_globals()
    return _core._phase_6_status()


def _phase_7_status(registry: dict[str, Any]) -> str:
    _sync_core_globals()
    return _core._phase_7_status(registry)


def _phase_8_status() -> str:
    _sync_core_globals()
    return _core._phase_8_status()


def _find_requests_usage_outside_network_mediator() -> list[str]:
    _sync_core_globals()
    return _core._find_requests_usage_outside_network_mediator()


def render_route_protection_coverage_markdown() -> str:
    _sync_core_globals()
    return _core.render_route_protection_coverage_markdown()


def render_governance_matrix_tree_markdown(registry: dict[str, Any]) -> str:
    _sync_core_globals()
    return _core.render_governance_matrix_tree_markdown(registry)


def write_runtime_governance_docs(
    output_dir: Path | None = None,
    registry: dict[str, Any] | None = None,
) -> dict[str, Path]:
    _sync_core_globals()
    registry = registry or globals()["_load_registry"]()
    output_dir = output_dir or globals()["RUNTIME_DOC_DIR"]
    enabled_ids = _core._enabled_registry_ids(registry)

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "governance_matrix": output_dir / "GOVERNANCE_MATRIX.md",
        "skill_surface_map": output_dir / "SKILL_SURFACE_MAP.md",
        "bypass_surfaces": output_dir / "BYPASS_SURFACES.md",
        "runtime_fingerprint": output_dir / "RUNTIME_FINGERPRINT.md",
        "governance_matrix_tree": output_dir / "GOVERNANCE_MATRIX_TREE.md",
        "route_protection_coverage": output_dir / "ROUTE_PROTECTION_COVERAGE.md",
    }

    paths["governance_matrix"].write_text(_core.render_governance_matrix_markdown(registry), encoding="utf-8")
    paths["skill_surface_map"].write_text(_core.render_skill_surface_map_markdown(), encoding="utf-8")
    paths["bypass_surfaces"].write_text(render_bypass_surfaces_markdown(), encoding="utf-8")
    paths["runtime_fingerprint"].write_text(render_runtime_fingerprint_markdown(enabled_ids), encoding="utf-8")
    paths["governance_matrix_tree"].write_text(render_governance_matrix_tree_markdown(registry), encoding="utf-8")
    paths["route_protection_coverage"].write_text(render_route_protection_coverage_markdown(), encoding="utf-8")

    return {name: path.resolve() for name, path in paths.items()}


def write_current_runtime_state_snapshot(path: Path | None = None) -> Path:
    if path is None:
        path = globals()["RUNTIME_DOC_PATH"]
    report = globals()["run_runtime_truth_audit"]()
    registry = globals()["_load_registry"]()
    markdown = globals()["render_current_runtime_state_markdown"](report, registry)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(markdown, encoding="utf-8")
    globals()["write_runtime_governance_docs"](output_dir=path.parent, registry=registry)
    return path.resolve()


_B1_WRAPPERS.update(
    {
        "_phase_5_status": _phase_5_status,
        "_phase_6_status": _phase_6_status,
        "_phase_7_status": _phase_7_status,
        "_phase_8_status": _phase_8_status,
    }
)


# Install public replacements into the preserved core so calls made internally
# by core renderers use B1 semantics too.
_core._runtime_surface_hash = _runtime_surface_hash
_core._runtime_fingerprint = _runtime_fingerprint
_core.render_runtime_fingerprint_markdown = render_runtime_fingerprint_markdown
_core.render_bypass_surfaces_markdown = render_bypass_surfaces_markdown
_core.run_runtime_truth_audit = run_runtime_truth_audit
_core.render_current_runtime_state_markdown = render_current_runtime_state_markdown
_core._phase_9_status = _phase_9_status
_core._build_discrepancies = _build_discrepancies
