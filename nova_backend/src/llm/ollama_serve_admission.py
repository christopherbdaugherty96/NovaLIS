"""Fail-closed admission for the launcher's bounded ``ollama serve`` process.

This module governs only creation of the verified local Ollama daemon. It does
not claim to mediate sockets later opened by Ollama or authorize model pulls.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
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
    _ollama_authenticode_is_valid,
    _verified_evidence_target,
)
from src.llm.ollama_setup_admission import _trusted_ollama_executable

_POLICY_VERSION = "launcher-ollama-serve-admission-v1"
_CORRELATION_LIMIT = 160


class OllamaServeAdmissionError(RuntimeError):
    """The daemon launch did not satisfy its exact admission contract."""


@dataclass(frozen=True)
class OllamaServeAdmission:
    executable: Path
    command: tuple[str, str]
    command_fingerprint: str
    executable_fingerprint: str
    correlation_id: str


@dataclass(frozen=True)
class VerificationProcessAdmissionRecord:
    correlation_id: str

    def as_dict(self) -> dict[str, object]:
        return {
            "record_kind": "verification_process_admission",
            "transport_observed": False,
            "purpose": "verify_ollama_serve_executable_identity",
            "correlation_id": _fingerprint(self.correlation_id),
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        }


@dataclass(frozen=True)
class DelegatedServeOutcomeRecord:
    command_fingerprint: str
    executable_fingerprint: str
    correlation_id: str
    outcome: str
    process_observed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "record_kind": "delegated_process_outcome",
            "transport_observed": self.process_observed,
            "operation": "serve",
            "command_fingerprint": self.command_fingerprint,
            "executable_fingerprint": self.executable_fingerprint,
            "correlation_id": _fingerprint(self.correlation_id),
            "outcome": self.outcome,
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


def _process_evidence_sink() -> JsonlDisclosureEvidenceSink:
    return JsonlDisclosureEvidenceSink(_verified_evidence_target())


def _minimal_child_environment() -> dict[str, str]:
    allowed = ("SystemRoot", "WINDIR", "LOCALAPPDATA", "USERPROFILE", "TEMP", "TMP")
    environment = {key: os.environ[key] for key in allowed if os.environ.get(key)}
    environment["OLLAMA_HOST"] = "http://127.0.0.1:11434"
    return environment


def _build_admission(*, correlation_id: str) -> OllamaServeAdmission:
    if not correlation_id or len(correlation_id) > _CORRELATION_LIMIT:
        raise OllamaServeAdmissionError("A bounded startup correlation ID is required.")
    executable = _trusted_ollama_executable().resolve(strict=True)
    if not _ollama_authenticode_is_valid(executable):
        raise OllamaServeAdmissionError("Ollama executable publisher is untrusted.")
    executable_fingerprint = _file_fingerprint(executable)
    command = (str(executable), "serve")
    return OllamaServeAdmission(
        executable=executable,
        command=command,
        command_fingerprint=_fingerprint("\0".join(command)),
        executable_fingerprint=executable_fingerprint,
        correlation_id=correlation_id,
    )


def _record_admission(admission: OllamaServeAdmission, sink) -> None:
    destination = (
        "ollama-command:serve:"
        f"{admission.command_fingerprint}:{admission.executable_fingerprint}"
    )
    request = DisclosureRequest(
        caller="windows_launcher_ollama_startup",
        purpose="local_model_daemon_startup",
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
        initiation=InitiationClass.AUTOMATIC,
    )
    grant = DisclosureGrant(
        provider="ollama_local",
        provider_class=ProviderClass.LOCAL_MODEL,
        destination_class=DestinationClass.DELEGATED_APPLICATION,
        destinations=frozenset({destination}),
        effective_routes=frozenset({"verified_local_process"}),
        transports=frozenset({TransportClass.PROCESS_HANDOFF}),
        data_categories=frozenset({DataCategory.STRUCTURAL_METADATA}),
        purposes=frozenset({"local_model_daemon_startup"}),
        callers=frozenset({"windows_launcher_ollama_startup"}),
        capability_ids=frozenset({None}),
        initiations=frozenset({InitiationClass.AUTOMATIC}),
    )
    decision = DisclosurePolicyEvaluator().evaluate_and_record(
        request,
        DisclosurePolicy(version=_POLICY_VERSION, grants=(grant,)),
        sink,
    )
    if not decision.may_proceed:
        raise OllamaServeAdmissionError(
            f"Ollama serve admission evidence failed ({decision.reason})."
        )


def _revalidate(admission: OllamaServeAdmission) -> None:
    executable = _trusted_ollama_executable().resolve(strict=True)
    if (
        executable != admission.executable
        or _file_fingerprint(executable) != admission.executable_fingerprint
        or not _ollama_authenticode_is_valid(executable)
    ):
        raise OllamaServeAdmissionError("Ollama executable identity changed before delegation.")


def spawn_verified_ollama_server(*, correlation_id: str) -> subprocess.Popen[bytes]:
    """Admit, evidence, revalidate, and spawn the exact local Ollama daemon."""
    try:
        sink = _process_evidence_sink()
        # Establish durable evidence before Authenticode verification or any
        # Ollama process creation. No PATH search is used by this module.
        sink.append(VerificationProcessAdmissionRecord(correlation_id=correlation_id))
        admission = _build_admission(correlation_id=correlation_id)
        _record_admission(admission, sink)
        _revalidate(admission)
    except OllamaServeAdmissionError:
        raise
    except Exception as error:
        raise OllamaServeAdmissionError("Ollama serve evidence is unavailable.") from error

    creation_flags = 0
    if os.name == "nt":
        creation_flags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
    try:
        process = subprocess.Popen(
            list(admission.command),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
            env=_minimal_child_environment(),
        )
    except OSError as error:
        try:
            sink.append(
                DelegatedServeOutcomeRecord(
                    command_fingerprint=admission.command_fingerprint,
                    executable_fingerprint=admission.executable_fingerprint,
                    correlation_id=admission.correlation_id,
                    outcome="spawn_failure",
                    process_observed=False,
                )
            )
        except Exception as evidence_error:
            raise OllamaServeAdmissionError(
                "Ollama serve outcome evidence could not be recorded."
            ) from evidence_error
        raise OllamaServeAdmissionError("Ollama serve process could not be created.") from error

    try:
        sink.append(
            DelegatedServeOutcomeRecord(
                command_fingerprint=admission.command_fingerprint,
                executable_fingerprint=admission.executable_fingerprint,
                correlation_id=admission.correlation_id,
                outcome="spawn_observed_not_ready",
                process_observed=True,
            )
        )
    except Exception as error:
        try:
            process.terminate()
        except Exception:
            pass
        raise OllamaServeAdmissionError(
            "Ollama serve outcome evidence could not be recorded."
        ) from error
    return process
