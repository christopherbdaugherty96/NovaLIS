"""Fail-closed admission for the installer's bounded Ollama commands.

This module authorizes only ``ollama list`` and an explicitly consented pull
of Nova's single approved installation model.  It records durable admission
evidence before spawning the process and a separate, content-free outcome
afterward.  Ollama's registry traffic remains delegated traffic; this module
does not claim to mediate it.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from src.governor.disclosure_policy import (
    DataCategory,
    DestinationClass,
    DisclosureGrant,
    DisclosurePolicy,
    DisclosurePolicyEvaluator,
    DisclosureRequest,
    InitiationClass,
    JsonlDisclosureEvidenceSink,
    ProviderClass,
    TransportClass,
)
from src.llm.local_ollama_bootstrap import (
    _attest_ollama_listener,
    _ollama_authenticode_is_valid,
    _verified_evidence_target,
)

APPROVED_INSTALL_MODEL = "gemma4:e4b"
_POLICY_VERSION = "installer-ollama-command-admission-v1"


class OllamaSetupAdmissionError(RuntimeError):
    """The installer command did not satisfy the exact admission contract."""


class OllamaSetupOperation(str, Enum):
    LIST = "list"
    PULL = "pull"


@dataclass(frozen=True)
class OllamaCommandAdmission:
    executable: Path
    operation: OllamaSetupOperation
    model: str
    command: tuple[str, ...]
    command_fingerprint: str
    executable_fingerprint: str
    correlation_id: str
    online_consent: bool


@dataclass(frozen=True)
class DelegatedProcessOutcomeRecord:
    operation: OllamaSetupOperation
    command_fingerprint: str
    executable_fingerprint: str
    correlation_id: str
    outcome: str
    exit_code: int | None

    def as_dict(self) -> dict[str, object]:
        return {
            "record_kind": "delegated_process_outcome",
            "transport_observed": True,
            "operation": self.operation.value,
            "command_fingerprint": self.command_fingerprint,
            "executable_fingerprint": self.executable_fingerprint,
            "correlation_id": _fingerprint(self.correlation_id),
            "outcome": self.outcome,
            "exit_code": self.exit_code,
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        }


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _trusted_ollama_executable() -> Path:
    if os.name != "nt":
        raise OllamaSetupAdmissionError("Ollama setup admission requires Windows.")
    local_appdata = os.environ.get("LOCALAPPDATA")
    if not local_appdata:
        raise OllamaSetupAdmissionError("Ollama installation root is unavailable.")
    expected = (Path(local_appdata) / "Programs" / "Ollama" / "ollama.exe").resolve()
    if not expected.is_file() or expected.is_symlink():
        raise OllamaSetupAdmissionError("Trusted Ollama executable was not found.")
    return expected


def _process_evidence_sink() -> JsonlDisclosureEvidenceSink:
    return JsonlDisclosureEvidenceSink(_verified_evidence_target())


def _minimal_child_environment() -> dict[str, str]:
    allowed = ("SystemRoot", "WINDIR", "LOCALAPPDATA", "USERPROFILE", "TEMP", "TMP")
    environment = {key: os.environ[key] for key in allowed if os.environ.get(key)}
    environment["OLLAMA_HOST"] = "http://127.0.0.1:11434"
    return environment


def _command_for(
    executable: Path, operation: OllamaSetupOperation, model: str
) -> tuple[str, ...]:
    if operation is OllamaSetupOperation.LIST:
        return (str(executable), "list")
    return (str(executable), "pull", model)


def build_ollama_admission(
    *,
    operation: OllamaSetupOperation,
    model: str,
    correlation_id: str,
    online_consent: bool,
) -> OllamaCommandAdmission:
    if not isinstance(operation, OllamaSetupOperation):
        raise OllamaSetupAdmissionError("Unsupported Ollama setup operation.")
    if not correlation_id or len(correlation_id) > 160:
        raise OllamaSetupAdmissionError("A bounded installation correlation ID is required.")
    if model != APPROVED_INSTALL_MODEL:
        raise OllamaSetupAdmissionError("The requested model is not installation-authorized.")
    if operation is OllamaSetupOperation.PULL and not online_consent:
        raise OllamaSetupAdmissionError("Ollama pull requires explicit online consent.")

    executable = _trusted_ollama_executable().resolve(strict=True)
    if not _ollama_authenticode_is_valid(executable):
        raise OllamaSetupAdmissionError("Ollama executable publisher is untrusted.")
    _attest_ollama_listener()
    executable_fingerprint = _file_fingerprint(executable)
    command = _command_for(executable, operation, model)
    command_fingerprint = _fingerprint("\0".join(command))
    return OllamaCommandAdmission(
        executable=executable,
        operation=operation,
        model=model,
        command=command,
        command_fingerprint=command_fingerprint,
        executable_fingerprint=executable_fingerprint,
        correlation_id=correlation_id,
        online_consent=online_consent,
    )


def _record_admission(admission: OllamaCommandAdmission, sink) -> None:
    purpose = (
        "authorized_model_acquisition"
        if admission.operation is OllamaSetupOperation.PULL
        else "local_model_inventory"
    )
    initiation = (
        InitiationClass.APPROVED
        if admission.operation is OllamaSetupOperation.PULL
        else InitiationClass.AUTOMATIC
    )
    # The non-URL destination is an exact, immutable operation identity.  It
    # deliberately records fingerprints rather than arguments or user data.
    destination = (
        f"ollama-command:{admission.operation.value}:"
        f"{admission.command_fingerprint}:{admission.executable_fingerprint}"
    )
    request = DisclosureRequest(
        caller="windows_installer_ollama_setup",
        purpose=purpose,
        transport=TransportClass.PROCESS_HANDOFF,
        destination_class=DestinationClass.DELEGATED_APPLICATION,
        provider_class=ProviderClass.LOCAL_MODEL,
        derived_destination=destination,
        declared_destination=destination,
        policy_version=_POLICY_VERSION,
        data_categories=frozenset({DataCategory.STRUCTURAL_METADATA}),
        request_id=admission.correlation_id,
        action_id=admission.command_fingerprint,
        declared_provider="ollama_local",
        derived_provider="ollama_local",
        effective_route="verified_local_process",
        initiation=initiation,
    )
    grant = DisclosureGrant(
        provider="ollama_local",
        provider_class=ProviderClass.LOCAL_MODEL,
        destination_class=DestinationClass.DELEGATED_APPLICATION,
        destinations=frozenset({destination}),
        effective_routes=frozenset({"verified_local_process"}),
        transports=frozenset({TransportClass.PROCESS_HANDOFF}),
        data_categories=frozenset({DataCategory.STRUCTURAL_METADATA}),
        purposes=frozenset({purpose}),
        callers=frozenset({"windows_installer_ollama_setup"}),
        capability_ids=frozenset({None}),
        initiations=frozenset({initiation}),
    )
    decision = DisclosurePolicyEvaluator().evaluate_and_record(
        request,
        DisclosurePolicy(version=_POLICY_VERSION, grants=(grant,)),
        sink,
    )
    if not decision.may_proceed:
        raise OllamaSetupAdmissionError(
            f"Ollama command admission evidence failed ({decision.reason})."
        )


def _revalidate(admission: OllamaCommandAdmission) -> None:
    executable = _trusted_ollama_executable().resolve(strict=True)
    if (
        executable != admission.executable
        or _file_fingerprint(executable) != admission.executable_fingerprint
        or not _ollama_authenticode_is_valid(executable)
    ):
        raise OllamaSetupAdmissionError("Ollama executable identity changed before delegation.")
    _attest_ollama_listener()


def run_ollama_command(
    *,
    operation: OllamaSetupOperation,
    model: str,
    correlation_id: str,
    online_consent: bool,
    timeout: float = 1800.0,
) -> subprocess.CompletedProcess[str]:
    """Admit, evidence, revalidate and run one exact Ollama setup command."""
    admission = build_ollama_admission(
        operation=operation,
        model=model,
        correlation_id=correlation_id,
        online_consent=online_consent,
    )
    try:
        sink = _process_evidence_sink()
        _record_admission(admission, sink)
    except OllamaSetupAdmissionError:
        raise
    except Exception as error:
        raise OllamaSetupAdmissionError("Ollama command evidence is unavailable.") from error
    _revalidate(admission)

    outcome = "exception"
    exit_code: int | None = None
    try:
        result = subprocess.run(
            list(admission.command),
            capture_output=True,
            check=False,
            encoding="utf-8",
            env=_minimal_child_environment(),
            errors="strict",
            timeout=timeout,
        )
        exit_code = result.returncode
        outcome = "exit_success" if result.returncode == 0 else "exit_failure"
        return result
    except subprocess.TimeoutExpired:
        outcome = "timeout"
        raise
    finally:
        try:
            sink.append(
                DelegatedProcessOutcomeRecord(
                    operation=admission.operation,
                    command_fingerprint=admission.command_fingerprint,
                    executable_fingerprint=admission.executable_fingerprint,
                    correlation_id=admission.correlation_id,
                    outcome=outcome,
                    exit_code=exit_code,
                )
            )
        except Exception as error:
            raise OllamaSetupAdmissionError(
                "Ollama command outcome evidence could not be recorded."
            ) from error
