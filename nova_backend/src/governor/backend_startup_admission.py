"""Exact, evidence-backed admission for the Windows Nova backend child.

This boundary governs only creation of the fixed local uvicorn command used by
``scripts/start_daemon.py``.  It does not claim to certify every executable the
backend may later delegate to; those remain F05/F09 scope decisions.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.governor.disclosure_policy import (
    CredentialCategory,
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
from src.llm.local_ollama_bootstrap import _verified_evidence_target

_POLICY_VERSION = "windows-backend-startup-admission-v1"
_CALLER = "windows_start_daemon"
_PURPOSE = "start_local_nova_backend"
_ROUTE = "current_python_exact_uvicorn"
_PROVIDER_ENVIRONMENT_KEYS = frozenset(
    {
        "OPENAI_API_KEY",
        "BRAVE_API_KEY",
        "NEWS_API_KEY",
        "WEATHER_API_KEY",
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_MODEL",
        "SHOPIFY_ACCESS_TOKEN",
        "SHOPIFY_STORE",
    }
)
_OS_ENVIRONMENT_KEYS = frozenset(
    {
        "SystemRoot",
        "WINDIR",
        "COMSPEC",
        "LOCALAPPDATA",
        "APPDATA",
        "PROGRAMDATA",
        "USERPROFILE",
        "TEMP",
        "TMP",
        "TMPDIR",
        "LANG",
        "LC_ALL",
    }
)
_NORMALIZED_OS_ENVIRONMENT_KEYS = frozenset(key.upper() for key in _OS_ENVIRONMENT_KEYS)


class BackendStartupAdmissionError(RuntimeError):
    """The fixed Nova backend child was not safely admitted or evidenced."""


@dataclass(frozen=True)
class BackendStartupPlan:
    executable: Path
    executable_identity: Path
    backend_dir: Path
    command: tuple[str, ...]
    executable_fingerprint: str
    command_fingerprint: str
    environment: tuple[tuple[str, str], ...]
    environment_fingerprint: str
    plan_fingerprint: str
    credential_categories: frozenset[CredentialCategory]
    initiation: InitiationClass


@dataclass(frozen=True)
class BackendStartupLaunch:
    plan: BackendStartupPlan
    process: subprocess.Popen


@dataclass(frozen=True)
class BackendStartupOutcomeRecord:
    command_fingerprint: str
    executable_fingerprint: str
    environment_fingerprint: str
    plan_fingerprint: str
    outcome: str
    process_observed: bool
    exit_code: int | None = None
    listener_pid: int | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "record_kind": "delegated_process_outcome",
            "transport_observed": self.process_observed,
            "operation": "nova_backend_startup",
            "command_fingerprint": self.command_fingerprint,
            "executable_fingerprint": self.executable_fingerprint,
            "environment_fingerprint": self.environment_fingerprint,
            "plan_fingerprint": self.plan_fingerprint,
            "outcome": self.outcome,
            "exit_code": self.exit_code,
            "listener_pid": self.listener_pid,
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


def _evidence_sink() -> JsonlDisclosureEvidenceSink:
    return JsonlDisclosureEvidenceSink(_verified_evidence_target())


def _minimal_backend_environment(executable: Path) -> dict[str, str]:
    environment = {
        key: value
        for key, value in os.environ.items()
        if value
        and (
            key.upper() in _NORMALIZED_OS_ENVIRONMENT_KEYS
            or key.upper() in _PROVIDER_ENVIRONMENT_KEYS
            or key.upper().startswith("NOVA_")
            or key.upper().startswith("OLLAMA_")
        )
    }
    # Do not inherit proxy configuration or an ambient executable search path.
    # The bounded backend command uses the exact current Python executable.
    normalized_environment = {key.upper(): value for key, value in environment.items()}
    system_root = normalized_environment.get("SYSTEMROOT") or normalized_environment.get("WINDIR")
    path_entries: list[str] = []
    if system_root:
        system_root_path = Path(system_root)
        powershell_dir = system_root_path / "System32" / "WindowsPowerShell" / "v1.0"
        # Brightness and Windows audio still use the supported system PowerShell
        # entry point. Keep only its canonical Windows location discoverable;
        # broader executable identity remains the separately tracked F09 work.
        if (powershell_dir / "powershell.exe").is_file():
            path_entries.append(str(powershell_dir))
        path_entries.append(str(system_root_path / "System32"))
    path_entries.append(str(executable.parent))
    environment["PATH"] = os.pathsep.join(path_entries)
    environment["PYTHONNOUSERSITE"] = "1"
    return environment


def build_backend_startup_plan(
    *,
    executable: Path,
    backend_dir: Path,
    host: str,
    port: int,
    initiation: InitiationClass = InitiationClass.USER_INITIATED,
) -> BackendStartupPlan:
    if host not in {"127.0.0.1", "::1"}:
        raise BackendStartupAdmissionError("Backend startup requires a literal loopback bind.")
    if not isinstance(port, int) or not 1 <= port <= 65535:
        raise BackendStartupAdmissionError("Backend startup port is invalid.")
    if initiation not in {InitiationClass.USER_INITIATED, InitiationClass.AUTOMATIC}:
        raise BackendStartupAdmissionError("Backend startup initiation is invalid.")
    try:
        invocation_executable = Path(os.path.abspath(executable))
        resolved_executable = invocation_executable.resolve(strict=True)
        resolved_backend = backend_dir.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise BackendStartupAdmissionError("Backend startup identity is unavailable.") from error
    if (
        not invocation_executable.is_file()
        or not resolved_executable.is_file()
        or not resolved_backend.is_dir()
    ):
        raise BackendStartupAdmissionError("Backend startup identity is invalid.")
    command = (
        str(invocation_executable),
        "-m",
        "uvicorn",
        "src.brain_server:app",
        "--host",
        host,
        "--port",
        str(port),
        "--app-dir",
        str(resolved_backend),
    )
    executable_fingerprint = _file_fingerprint(resolved_executable)
    command_fingerprint = _fingerprint("\0".join(command))
    environment = tuple(sorted(_minimal_backend_environment(invocation_executable).items()))
    environment_fingerprint = _fingerprint(
        "\0".join(f"{key}\0{value}" for key, value in environment)
    )
    environment_keys = {key for key, _value in environment}
    credential_categories: set[CredentialCategory] = set()
    if environment_keys & {
        "OPENAI_API_KEY",
        "BRAVE_API_KEY",
        "NEWS_API_KEY",
        "WEATHER_API_KEY",
        "DEEPSEEK_API_KEY",
    }:
        credential_categories.add(CredentialCategory.API_KEY)
    if "SHOPIFY_ACCESS_TOKEN" in environment_keys:
        credential_categories.add(CredentialCategory.ORIGIN_CREDENTIAL)
    plan_fingerprint = _fingerprint(
        "\0".join(
            (
                executable_fingerprint,
                command_fingerprint,
                environment_fingerprint,
                initiation.value,
            )
        )
    )
    return BackendStartupPlan(
        executable=invocation_executable,
        executable_identity=resolved_executable,
        backend_dir=resolved_backend,
        command=command,
        executable_fingerprint=executable_fingerprint,
        command_fingerprint=command_fingerprint,
        environment=environment,
        environment_fingerprint=environment_fingerprint,
        plan_fingerprint=plan_fingerprint,
        credential_categories=frozenset(credential_categories),
        initiation=initiation,
    )


def _record_admission(plan: BackendStartupPlan, sink) -> None:
    destination = f"nova-backend-command:{plan.plan_fingerprint}"
    request = DisclosureRequest(
        caller=_CALLER,
        purpose=_PURPOSE,
        transport=TransportClass.PROCESS_HANDOFF,
        destination_class=DestinationClass.LOCAL_OS,
        provider_class=ProviderClass.LOCAL_OS,
        derived_destination=destination,
        declared_destination=destination,
        policy_version=_POLICY_VERSION,
        data_categories=frozenset({DataCategory.RUNTIME_STATE}),
        credential_categories=plan.credential_categories,
        action_id=plan.plan_fingerprint,
        declared_provider="nova_local_backend",
        derived_provider="nova_local_backend",
        effective_route=_ROUTE,
        initiation=plan.initiation,
    )
    grant = DisclosureGrant(
        provider="nova_local_backend",
        provider_class=ProviderClass.LOCAL_OS,
        destination_class=DestinationClass.LOCAL_OS,
        destinations=frozenset({destination}),
        effective_routes=frozenset({_ROUTE}),
        transports=frozenset({TransportClass.PROCESS_HANDOFF}),
        data_categories=frozenset({DataCategory.RUNTIME_STATE}),
        credential_categories=plan.credential_categories,
        purposes=frozenset({_PURPOSE}),
        callers=frozenset({_CALLER}),
        capability_ids=frozenset({None}),
        initiations=frozenset({plan.initiation}),
    )
    decision = DisclosurePolicyEvaluator().evaluate_and_record(
        request,
        DisclosurePolicy(version=_POLICY_VERSION, grants=(grant,)),
        sink,
    )
    if not decision.may_proceed:
        raise BackendStartupAdmissionError(f"Backend startup admission failed ({decision.reason}).")


@contextmanager
def _locked_executable_identity(executable: Path):
    """On Windows, deny executable write/delete through process creation."""
    if os.name != "nt":
        yield
        return
    import ctypes
    from ctypes import wintypes

    create_file = ctypes.WinDLL("kernel32", use_last_error=True).CreateFileW
    create_file.argtypes = (
        wintypes.LPCWSTR,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.LPVOID,
        wintypes.DWORD,
        wintypes.DWORD,
        wintypes.HANDLE,
    )
    create_file.restype = wintypes.HANDLE
    close_handle = ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle
    close_handle.argtypes = (wintypes.HANDLE,)
    close_handle.restype = wintypes.BOOL
    handle = create_file(str(executable), 0x80000000, 0x00000001, None, 3, 0x80, None)
    if handle == wintypes.HANDLE(-1).value:
        raise BackendStartupAdmissionError("Backend executable identity could not be locked.")
    try:
        yield
    finally:
        close_handle(handle)


def _revalidate(plan: BackendStartupPlan) -> None:
    try:
        current = plan.executable.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise BackendStartupAdmissionError("Backend executable identity changed.") from error
    if (
        current != plan.executable_identity
        or _file_fingerprint(current) != plan.executable_fingerprint
    ):
        raise BackendStartupAdmissionError("Backend executable identity changed before spawn.")


def _record_outcome(
    sink,
    plan: BackendStartupPlan,
    *,
    outcome: str,
    process_observed: bool,
    exit_code: int | None = None,
    listener_pid: int | None = None,
) -> None:
    try:
        sink.append(
            BackendStartupOutcomeRecord(
                command_fingerprint=plan.command_fingerprint,
                executable_fingerprint=plan.executable_fingerprint,
                environment_fingerprint=plan.environment_fingerprint,
                plan_fingerprint=plan.plan_fingerprint,
                outcome=outcome,
                process_observed=process_observed,
                exit_code=exit_code,
                listener_pid=listener_pid,
            )
        )
    except Exception as error:
        raise BackendStartupAdmissionError("Backend startup outcome evidence failed.") from error


def spawn_admitted_backend(
    *,
    executable: Path,
    backend_dir: Path,
    host: str,
    port: int,
    evidence_sink=None,
    stdout=None,
    stderr=None,
    initiation: InitiationClass = InitiationClass.USER_INITIATED,
) -> BackendStartupLaunch:
    """Evidence, revalidate, and spawn the one fixed local backend command."""
    plan = build_backend_startup_plan(
        executable=executable,
        backend_dir=backend_dir,
        host=host,
        port=port,
        initiation=initiation,
    )
    try:
        sink = _evidence_sink() if evidence_sink is None else evidence_sink
        with _locked_executable_identity(plan.executable_identity):
            _record_admission(plan, sink)
            _revalidate(plan)
            try:
                process = subprocess.Popen(
                    list(plan.command),
                    stdout=stdout,
                    stderr=stderr,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                    env=dict(plan.environment),
                    cwd=str(plan.backend_dir.parent),
                    shell=False,
                )
            except OSError as error:
                _record_outcome(sink, plan, outcome="spawn_failure", process_observed=False)
                raise BackendStartupAdmissionError(
                    "Backend process could not be created."
                ) from error
    except BackendStartupAdmissionError:
        raise
    except Exception as error:
        raise BackendStartupAdmissionError("Backend startup evidence is unavailable.") from error
    try:
        _record_outcome(sink, plan, outcome="spawn_observed_not_ready", process_observed=True)
    except BackendStartupAdmissionError:
        try:
            process.terminate()
        except Exception:
            pass
        raise
    return BackendStartupLaunch(plan=plan, process=process)


def record_backend_outcome(
    launch: BackendStartupLaunch,
    *,
    outcome: str,
    evidence_sink=None,
    exit_code: int | None = None,
    listener_pid: int | None = None,
) -> None:
    if outcome not in {"ready", "exited_before_ready", "readiness_timeout"}:
        raise BackendStartupAdmissionError("Backend startup outcome is invalid.")
    try:
        sink = _evidence_sink() if evidence_sink is None else evidence_sink
    except Exception as error:
        raise BackendStartupAdmissionError("Backend startup evidence is unavailable.") from error
    _record_outcome(
        sink,
        launch.plan,
        outcome=outcome,
        process_observed=True,
        exit_code=exit_code,
        listener_pid=listener_pid,
    )
