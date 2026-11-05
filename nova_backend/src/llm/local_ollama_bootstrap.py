"""Narrow, fail-closed Windows loopback-Ollama Data-Out composition.

This is not a general LOCAL_PRIVATE_MODEL exemption. Other callers retain the
default deny-only ModelNetworkMediator. No remote or LAN provider is admitted.
"""
from __future__ import annotations

import ctypes
import json
import logging
import os
import subprocess
import threading
from pathlib import Path
from urllib.parse import urlsplit

import psutil
from src.governor.disclosure_policy import (
    DataCategory,
    DestinationClass,
    DisclosureGrant,
    DisclosurePolicy,
    DisclosurePolicyEvaluator,
    InitiationClass,
    JsonlDisclosureEvidenceSink,
    ProviderClass,
    TransportClass,
    VerifiedLocalEvidenceTarget,
)
from src.governor.disclosure_transport import (
    HttpDisclosureContext,
    authorize_http_disclosure,
    disclosure_facts,
)
from src.llm.model_network_mediator import (
    ModelNetworkMediator,
    ModelNetworkMediatorError,
    localhost_resolves_exclusively_to_loopback,
)
from src.utils.persistent_state import runtime_root

_LOG = logging.getLogger(__name__)
_PORT = 11434
_PATHS = {("POST", "/api/show"), ("GET", "/api/tags"), ("POST", "/api/chat")}
_OPTIONS = {"temperature", "num_predict", "num_ctx", "top_k", "repeat_penalty", "stop"}
_ATTESTATION_LOCK = threading.Lock()
_ATTESTED_PROCESS: tuple[str, int, float] | None = None


def _is_windows() -> bool:
    return os.name == "nt"


def _ollama_authenticode_is_valid(executable: Path) -> bool:
    """Verify that Windows trusts the binary and attributes it to Ollama Inc."""
    system_root = Path(os.environ.get("SystemRoot") or r"C:\Windows").resolve()
    powershell = (
        system_root
        / "System32"
        / "WindowsPowerShell"
        / "v1.0"
        / "powershell.exe"
    ).resolve()
    if not powershell.is_file():
        return False
    command = (
        "$signature = Get-AuthenticodeSignature -LiteralPath "
        "$env:NOVA_OLLAMA_ATTEST_PATH; "
        "$subject = if ($signature.SignerCertificate) "
        "{ [string]$signature.SignerCertificate.Subject } else { '' }; "
        "[pscustomobject]@{Status=[string]$signature.Status;Subject=$subject} "
        "| ConvertTo-Json -Compress"
    )
    environment = {
        "NOVA_OLLAMA_ATTEST_PATH": str(executable),
        "SystemRoot": str(system_root),
        "WINDIR": str(system_root),
    }
    try:
        completed = subprocess.run(
            [
                str(powershell),
                "-NoLogo",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                command,
            ],
            capture_output=True,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            encoding="utf-8",
            env=environment,
            errors="strict",
            timeout=15,
        )
        if completed.returncode != 0:
            return False
        result = json.loads(completed.stdout)
    except (OSError, subprocess.SubprocessError, UnicodeError, ValueError):
        return False
    subject = str(result.get("Subject") or "")
    return result.get("Status") == "Valid" and any(
        component.strip() in {"CN=Ollama Inc.", "O=Ollama Inc."}
        for component in subject.split(",")
    )


def _verified_evidence_target() -> VerifiedLocalEvidenceTarget:
    """Verify local Windows fixed-volume storage before claiming evidence locality."""
    if not _is_windows():
        raise ModelNetworkMediatorError("Local Ollama evidence bootstrap requires Windows.")
    root = runtime_root(__file__).resolve(strict=True)
    if not root.is_absolute() or str(root).startswith("\\\\"):
        raise ModelNetworkMediatorError("Untrusted model evidence root.")
    # On Windows, GetDriveTypeW=3 is a fixed local drive; reject network,
    # removable, unknown and UNC targets instead of asserting false locality.
    drive = Path(root.anchor)
    if ctypes.windll.kernel32.GetDriveTypeW(str(drive)) != 3:
        raise ModelNetworkMediatorError("Model evidence must reside on a local fixed drive.")
    target = root / "data" / "nova_state" / "ollama_disclosure_evidence.jsonl"
    cursor = target.parent
    while cursor != root.parent:
        if cursor.is_symlink():
            raise ModelNetworkMediatorError("Model evidence path contains a symlink.")
        if cursor == root:
            break
        cursor = cursor.parent
    if target.is_symlink():
        raise ModelNetworkMediatorError("Model evidence file is a symlink.")
    return VerifiedLocalEvidenceTarget(path=target, locality_verified=True)


def _attest_ollama_listener() -> None:
    """Require the user-installed Ollama executable to own the exact loopback listener."""
    global _ATTESTED_PROCESS
    if not _is_windows():
        raise ModelNetworkMediatorError("No verified Windows Ollama listener.")
    local_appdata = os.environ.get("LOCALAPPDATA")
    if not local_appdata:
        raise ModelNetworkMediatorError("Ollama installation root unavailable.")
    expected = (Path(local_appdata) / "Programs" / "Ollama" / "ollama.exe").resolve()
    if not expected.is_file():
        raise ModelNetworkMediatorError("Trusted Ollama executable not found.")
    try:
        listeners = [
            c for c in psutil.net_connections(kind="tcp")
            if c.status == psutil.CONN_LISTEN
            and c.laddr and c.laddr.port == _PORT
        ]
        if not listeners or any(
            c.laddr.ip != "127.0.0.1" or not c.pid for c in listeners
        ):
            raise ModelNetworkMediatorError("Ollama is not exclusively bound to IPv4 loopback.")
        pids = {c.pid for c in listeners}
        if len(pids) != 1:
            raise ModelNetworkMediatorError("Ambiguous Ollama listener owner.")
        process = psutil.Process(pids.pop())
        executable = Path(process.exe()).resolve()
        commands = process.cmdline()
        if (
            str(executable).casefold() != str(expected).casefold()
            or not commands
            or "serve" not in commands[1:]
        ):
            raise ModelNetworkMediatorError("Unexpected process owns the Ollama listener.")
        identity = (str(executable).casefold(), process.pid, process.create_time())
        with _ATTESTATION_LOCK:
            if _ATTESTED_PROCESS != identity:
                if not _ollama_authenticode_is_valid(executable):
                    raise ModelNetworkMediatorError(
                        "Ollama listener publisher could not be verified."
                    )
                _ATTESTED_PROCESS = identity
    except ModelNetworkMediatorError:
        raise
    except (OSError, psutil.Error, ValueError) as error:
        raise ModelNetworkMediatorError("Unable to attest Ollama listener.") from error


class VerifiedLoopbackOllamaMediator(ModelNetworkMediator):
    """Bounded policy for a specifically attested, loopback-only Ollama service."""

    def __init__(self, *, model: str, evidence_sink) -> None:
        super().__init__(disclosure_evidence_sink=evidence_sink)
        self._expected_model = model

    @staticmethod
    def _strict_url(url: str, method: str) -> str:
        try:
            parsed = urlsplit(url)
            if (
                parsed.scheme != "http"
                or parsed.hostname not in {"localhost", "127.0.0.1"}
                or parsed.port != _PORT
                or parsed.username is not None
                or parsed.password is not None
                or parsed.query or parsed.fragment
                or (method.upper(), parsed.path) not in _PATHS
                or not parsed.netloc
            ):
                raise ModelNetworkMediatorError("Unsupported local Ollama destination.")
            if parsed.hostname == "localhost":
                if not localhost_resolves_exclusively_to_loopback():
                    raise ModelNetworkMediatorError("localhost did not resolve exclusively to loopback.")
            return f"http://127.0.0.1:{_PORT}{parsed.path}"
        except ModelNetworkMediatorError:
            raise
        except (OSError, ValueError, TypeError) as error:
            raise ModelNetworkMediatorError("Invalid local Ollama destination.") from error

    def _validate_payload(self, method: str, url: str, payload: dict | None) -> frozenset[DataCategory]:
        parsed = urlsplit(url)
        if (method.upper(), parsed.path) == ("GET", "/api/tags"):
            if payload is not None:
                raise ModelNetworkMediatorError("Ollama tags must have no request body.")
            return frozenset({DataCategory.STRUCTURAL_METADATA})
        if not isinstance(payload, dict) or payload.get("model") != self._expected_model:
            raise ModelNetworkMediatorError("Ollama model identity mismatch.")
        if (method.upper(), parsed.path) == ("POST", "/api/show"):
            if set(payload) != {"model"}:
                raise ModelNetworkMediatorError("Unsupported Ollama identity request.")
            return frozenset({DataCategory.STRUCTURAL_METADATA})
        if set(payload) != {"model", "messages", "stream", "options"}:
            raise ModelNetworkMediatorError("Unsupported Ollama inference request.")
        if not isinstance(payload["stream"], bool):
            raise ModelNetworkMediatorError("Unsupported Ollama stream mode.")
        messages, options = payload["messages"], payload["options"]
        if (
            not isinstance(messages, list) or not messages
            or not all(
                isinstance(item, dict)
                and set(item) == {"role", "content"}
                and item["role"] in {"system", "user", "assistant"}
                and isinstance(item["content"], str)
                for item in messages
            )
            or not isinstance(options, dict) or not set(options).issubset(_OPTIONS)
            or not all(isinstance(k, str) for k in options)
        ):
            raise ModelNetworkMediatorError("Unsupported Ollama inference structure.")
        return frozenset({DataCategory.PROMPT, DataCategory.CONVERSATION_CONTEXT})

    def _authorize_disclosure(
        self, *, method: str, url: str, json_payload: dict | None,
        has_body: bool, request_id: str | None, session_id: str | None,
    ) -> None:
        pinned_url = self._strict_url(url, method)
        categories = self._validate_payload(method, pinned_url, json_payload)
        _attest_ollama_listener()
        facts = disclosure_facts(
            transport=TransportClass.LOCAL_PRIVATE_MODEL,
            method=method,
            url=pinned_url,
            json_payload=json_payload,
            capability_id=None,
        )
        if not facts.shape_supported or facts.credential_categories:
            raise ModelNetworkMediatorError("Unclassified Ollama disclosure shape.")
        context = HttpDisclosureContext(
            caller="verified_local_ollama",
            purpose="local_model_runtime",
            provider="ollama_local",
            provider_class=ProviderClass.LOCAL_MODEL,
            data_categories=categories,
            initiation=InitiationClass.AUTOMATIC,
        )
        # The schema validator above is closed over three known operations.
        # A per-operation grant binds the exact prepared request shape; no
        # general private-network or open-ended endpoint grant is created.
        grant = DisclosureGrant(
            provider="ollama_local",
            provider_class=ProviderClass.LOCAL_MODEL,
            destination_class=DestinationClass.LOCAL_LOOPBACK,
            destinations=frozenset({facts.destination}),
            effective_routes=frozenset({"direct"}),
            transports=frozenset({TransportClass.LOCAL_PRIVATE_MODEL}),
            data_categories=categories,
            http_methods=frozenset({method.upper()}),
            request_shapes=frozenset({facts.request_shape}),
            credential_categories=frozenset(),
            purposes=frozenset({"local_model_runtime"}),
            callers=frozenset({"verified_local_ollama"}),
            capability_ids=frozenset({None}),
            initiations=frozenset({InitiationClass.AUTOMATIC}),
        )
        policy = DisclosurePolicy(version="ollama-loopback-bootstrap-v1", grants=(grant,))
        decision = authorize_http_disclosure(
            evaluator=DisclosurePolicyEvaluator(),
            policy=policy,
            evidence_sink=self._disclosure_evidence_sink,
            context=context,
            facts=facts,
            has_body=has_body,
            capability_id=None,
            request_id=request_id or "",
            session_id=session_id or "",
        )
        if not decision.may_proceed:
            raise ModelNetworkMediatorError(f"Data-Out denied ({decision.reason}).")

    def _validate_url(self, url: str) -> str:
        pinned = self._strict_url(url, "GET" if urlsplit(url).path == "/api/tags" else "POST")
        _attest_ollama_listener()
        return pinned

    def _request_session(self):
        session = super()._request_session()
        if getattr(session, "trust_env", True) or getattr(session, "proxies", {}):
            raise ModelNetworkMediatorError("Untrusted Ollama request session.")
        return session


def build_local_ollama_mediator(base_url: str, model: str) -> ModelNetworkMediator:
    """Create only the trusted Windows Ollama composition, otherwise fail closed."""
    try:
        VerifiedLoopbackOllamaMediator._strict_url(
            base_url.rstrip("/") + "/api/tags", "GET"
        )
        _attest_ollama_listener()
        sink = JsonlDisclosureEvidenceSink(_verified_evidence_target())
        return VerifiedLoopbackOllamaMediator(model=model, evidence_sink=sink)
    except Exception as error:
        _LOG.warning("Local Ollama trust bootstrap unavailable: %s", type(error).__name__)
        return ModelNetworkMediator()
