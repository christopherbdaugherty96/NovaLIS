from __future__ import annotations

"""Wave B1 instrumentation installed onto Nova's existing runtime auditor.

The existing ``src.audit.runtime_auditor`` remains the authoritative generator.
This module installs narrow measurement repairs without duplicating or rewriting
that mature implementation:

- direct-network findings participate in discrepancy state;
- known NetworkMediator exceptions are explicit and classified;
- Phase 9 status uses import/symbol evidence instead of retired placeholder files;
- runtime fingerprints cover behaviorally active source families;
- generated runtime invariants are scoped to what the auditor actually proves.
"""

import hashlib
import importlib
import json
from pathlib import Path
from types import ModuleType
from typing import Any


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


def install_runtime_truth_instrumentation(auditor: ModuleType) -> None:
    """Install B1 truth instrumentation onto ``runtime_auditor`` exactly once."""

    if getattr(auditor, "_B1_RUNTIME_TRUTH_INSTRUMENTATION_INSTALLED", False):
        return

    original_build_discrepancies = auditor._build_discrepancies
    original_render_bypass = auditor.render_bypass_surfaces_markdown
    original_run_audit = auditor.run_runtime_truth_audit
    original_render_current_state = auditor.render_current_runtime_state_markdown

    def classify_direct_network_paths(paths: list[str] | None = None) -> dict[str, Any]:
        offenders = sorted(
            set(
                paths
                if paths is not None
                else auditor._find_requests_usage_outside_network_mediator()
            )
        )
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

    def build_discrepancies(
        runtime_doc_enabled_ids: list[int],
        registry_enabled_ids: list[int],
        mediator_mapped_ids: list[int],
        model_path_signals: dict[str, Any],
        execution_gate_enabled: bool,
    ) -> list[Any]:
        discrepancies = list(
            original_build_discrepancies(
                runtime_doc_enabled_ids=runtime_doc_enabled_ids,
                registry_enabled_ids=registry_enabled_ids,
                mediator_mapped_ids=mediator_mapped_ids,
                model_path_signals=model_path_signals,
                execution_gate_enabled=execution_gate_enabled,
            )
        )

        network = auditor._classify_direct_network_paths()
        known = network["known_exceptions"]
        unknown = network["unclassified_paths"]

        if known:
            discrepancies.append(
                auditor.Discrepancy(
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
                auditor.Discrepancy(
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

    def render_bypass_surfaces_markdown() -> str:
        base = original_render_bypass().rstrip()
        classification = auditor._classify_direct_network_paths()

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
            lines.extend(
                f"- `{path}`" for path in classification["unclassified_paths"]
            )
        else:
            lines.extend(["", "- Unclassified direct-network paths: None detected."])

        lines.append("")
        return "\n".join(lines)

    def phase_9_live_evidence() -> dict[str, Any]:
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
            except Exception as exc:
                entry["error"] = f"{type(exc).__name__}: {exc}"
            checks.append(entry)

        return {
            "checks": checks,
            "all_required_symbols_live": all(
                item["imported"] and item["symbol_present"] for item in checks
            ),
        }

    def phase_9_status(registry: dict[str, Any]) -> str:
        evidence = auditor._phase_9_live_evidence()
        enabled_ids = set(auditor._enabled_registry_ids(registry))
        cap63 = 63 in enabled_ids

        if evidence["all_required_symbols_live"] and cap63:
            return "ACTIVE"
        if evidence["all_required_symbols_live"] or cap63:
            return "PARTIAL"
        return "DESIGN"

    def behaviorally_active_fingerprint_paths() -> frozenset[Path]:
        paths = set(auditor.ALLOWED_READ_PATHS)
        source_root = Path(auditor.PROJECT_ROOT) / "nova_backend" / "src"

        # Fingerprint scope is deliberately broader than the auditor's scan
        # allowlist: generated phase/runtime claims depend on these active source
        # families even when a specific scanner does not inspect each file.
        for directory_name in _FINGERPRINT_EXTRA_SOURCE_DIRS:
            directory = source_root / directory_name
            if directory.exists():
                paths.update(directory.rglob("*.py"))

        paths.add(Path(auditor.__file__).resolve())
        paths.add(Path(__file__).resolve())
        return frozenset(path.resolve() for path in paths)

    def runtime_surface_hash() -> str:
        digest = hashlib.sha256()
        runtime_doc_root = Path(auditor.RUNTIME_DOC_DIR).resolve()

        for path in sorted(auditor._behaviorally_active_fingerprint_paths()):
            resolved = path.resolve()
            if resolved.is_relative_to(runtime_doc_root):
                continue
            try:
                rel = resolved.relative_to(auditor.PROJECT_ROOT).as_posix()
            except ValueError:
                rel = resolved.as_posix()
            digest.update(rel.encode("utf-8"))
            digest.update(b"\n")
            if resolved.exists():
                digest.update(auditor._stable_hash_bytes(resolved))
            digest.update(b"\n")

        return digest.hexdigest()

    def runtime_fingerprint(registry_enabled_ids: list[int]) -> dict[str, Any]:
        runtime_surface_hash = auditor._runtime_surface_hash()
        enabled_hash = hashlib.sha256(
            json.dumps(registry_enabled_ids, sort_keys=True).encode("utf-8")
        ).hexdigest()
        paths = auditor._behaviorally_active_fingerprint_paths()
        payload = {
            "enabled_capability_ids": registry_enabled_ids,
            "runtime_surface_hash": runtime_surface_hash,
            "phase_marker": f"Build phase {auditor.BUILD_PHASE}",
            "scope_version": FINGERPRINT_SCOPE_VERSION,
        }
        runtime_fingerprint_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        return {
            "runtime_surface_hash": runtime_surface_hash,
            "enabled_capability_ids_hash": enabled_hash,
            "runtime_fingerprint_hash": runtime_fingerprint_hash,
            "phase_marker": f"Build phase {auditor.BUILD_PHASE}",
            "scope_version": FINGERPRINT_SCOPE_VERSION,
            "runtime_surface_file_count": len(paths),
        }

    def render_runtime_fingerprint_markdown(registry_enabled_ids: list[int]) -> str:
        fp = auditor._runtime_fingerprint(registry_enabled_ids)
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

    def run_runtime_truth_audit() -> dict[str, Any]:
        report = original_run_audit()
        checks = report.setdefault("checks", {})
        checks["direct_network_paths"] = auditor._classify_direct_network_paths()
        checks["phase_9_live_evidence"] = auditor._phase_9_live_evidence()
        checks["fingerprint_scope"] = {
            "scope_version": FINGERPRINT_SCOPE_VERSION,
            "runtime_surface_file_count": len(
                auditor._behaviorally_active_fingerprint_paths()
            ),
        }
        return report

    def phase_9_note(registry: dict[str, Any]) -> str:
        evidence = auditor._phase_9_live_evidence()
        live = [
            f"{item['module']}.{item['symbol']}"
            for item in evidence["checks"]
            if item["imported"] and item["symbol_present"]
        ]
        cap63 = 63 in set(auditor._enabled_registry_ids(registry))
        return (
            "Import/symbol evidence: "
            + (", ".join(live) if live else "no required Phase 9 symbols confirmed")
            + f"; capability 63 enabled={cap63}."
        )

    def render_current_runtime_state_markdown(
        report: dict[str, Any], registry: dict[str, Any]
    ) -> str:
        markdown = original_render_current_state(report, registry)
        lines = markdown.splitlines()

        phase9_status = auditor._phase_9_status(registry)
        for index, line in enumerate(lines):
            if line.startswith("| Phase 9 |"):
                lines[index] = (
                    f"| Phase 9 | {phase9_status} | "
                    f"{auditor._phase_9_evidence_note(registry)} |"
                )
                break

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

        fp = auditor._runtime_fingerprint(auditor._enabled_registry_ids(registry))
        for index, line in enumerate(lines):
            if line.startswith("- Runtime Surface Hash:"):
                lines.insert(
                    index + 1,
                    f"- Runtime Surface Scope: {fp['scope_version']} ({fp['runtime_surface_file_count']} files)",
                )
                break

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

    auditor._classify_direct_network_paths = classify_direct_network_paths
    auditor._build_discrepancies = build_discrepancies
    auditor.render_bypass_surfaces_markdown = render_bypass_surfaces_markdown
    auditor._phase_9_live_evidence = phase_9_live_evidence
    auditor._phase_9_status = phase_9_status
    auditor._behaviorally_active_fingerprint_paths = behaviorally_active_fingerprint_paths
    auditor._runtime_surface_hash = runtime_surface_hash
    auditor._runtime_fingerprint = runtime_fingerprint
    auditor.render_runtime_fingerprint_markdown = render_runtime_fingerprint_markdown
    auditor._phase_9_evidence_note = phase_9_note
    auditor.run_runtime_truth_audit = run_runtime_truth_audit
    auditor.render_current_runtime_state_markdown = render_current_runtime_state_markdown
    auditor.KNOWN_NETWORK_MEDIATOR_EXCEPTIONS = KNOWN_NETWORK_MEDIATOR_EXCEPTIONS
    auditor.FINGERPRINT_SCOPE_VERSION = FINGERPRINT_SCOPE_VERSION
    auditor._B1_RUNTIME_TRUTH_INSTRUMENTATION_INSTALLED = True
