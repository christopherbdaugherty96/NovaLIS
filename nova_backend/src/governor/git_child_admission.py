"""Bounded custody for the read-only Git build-identity children.

This boundary removes ambient credentials and Git configuration from the
children used by ``/phase-status``.  Git executable discovery still depends on
``PATH`` and is explicitly not treated as trusted executable identity; that is
the unresolved F09 boundary.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Callable

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
from src.llm.local_ollama_bootstrap import _verified_evidence_target

_POLICY_VERSION = "runtime-git-child-admission-v1"
_CALLER = "audit_api_runtime_build_identity"
_PURPOSE = "read_local_runtime_build_identity"
_ROUTE = "path_resolution_unverified_f09"
_DEFAULT = object()


class GitChildAdmissionError(RuntimeError):
    """The bounded Git identity plan was not admitted or completed safely."""


class GitIdentityOperation(str, Enum):
    FILTER_GUARD = "filter_guard"
    COMMIT = "commit"
    UNSTAGED = "unstaged"
    STAGED = "staged"
    UNTRACKED = "untracked"


@dataclass(frozen=True)
class GitIdentityPlan:
    source_root: Path
    commands: tuple[tuple[GitIdentityOperation, tuple[str, ...]], ...]
    plan_fingerprint: str


@dataclass(frozen=True)
class GitChildOutcomeRecord:
    operation: GitIdentityOperation
    plan_fingerprint: str
    outcome: str
    exit_code: int | None
    transport_observed: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "record_kind": "delegated_process_outcome",
            "transport_observed": self.transport_observed,
            "operation": self.operation.value,
            "plan_fingerprint": self.plan_fingerprint,
            "outcome": self.outcome,
            "exit_code": self.exit_code,
            "executable_identity": _ROUTE,
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        }


def _fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _git_prefix(source_root: Path) -> tuple[str, ...]:
    # Command-line config has higher precedence than repository configuration.
    # These reads need no protocol, credential helper, hook, pager, or fsmonitor.
    return (
        "git",
        "-c",
        "protocol.allow=never",
        "-c",
        "credential.helper=",
        "-c",
        f"core.hooksPath={os.devnull}",
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.pager=",
        "-c",
        "maintenance.auto=false",
        "-C",
        str(source_root),
    )


def build_git_identity_plan(source_root: Path) -> GitIdentityPlan:
    """Build the one immutable read-only command plan accepted by this boundary."""

    if not isinstance(source_root, Path) or not source_root.is_absolute():
        raise GitChildAdmissionError("An absolute source root is required.")
    prefix = _git_prefix(source_root)
    commands = (
        (
            GitIdentityOperation.FILTER_GUARD,
            (
                *prefix,
                "config",
                "--includes",
                "--get-regexp",
                r"^filter\..*\.(clean|process)$",
            ),
        ),
        (GitIdentityOperation.COMMIT, (*prefix, "rev-parse", "--verify", "HEAD")),
        (
            GitIdentityOperation.UNSTAGED,
            (
                *prefix,
                "diff",
                "--quiet",
                "--no-ext-diff",
                "--no-textconv",
                "--ignore-submodules=all",
                "--",
            ),
        ),
        (
            GitIdentityOperation.STAGED,
            (
                *prefix,
                "diff",
                "--cached",
                "--quiet",
                "--no-ext-diff",
                "--no-textconv",
                "--ignore-submodules=all",
                "--",
            ),
        ),
        (
            GitIdentityOperation.UNTRACKED,
            (*prefix, "ls-files", "--others", "--exclude-standard"),
        ),
    )
    serialized = "\n".join(
        operation.value + "\0" + "\0".join(command)
        for operation, command in commands
    )
    return GitIdentityPlan(
        source_root=source_root,
        commands=commands,
        plan_fingerprint=_fingerprint(serialized),
    )


def minimal_git_environment() -> dict[str, str]:
    """Return an explicit environment that excludes credentials and ambient Git controls."""

    permitted_parent_keys = (
        "PATH",  # F09 executable identity remains unresolved and recorded.
        "PATHEXT",
        "SystemRoot",
        "WINDIR",
        "COMSPEC",
        "TEMP",
        "TMP",
        "TMPDIR",
    )
    environment = {
        key: os.environ[key]
        for key in permitted_parent_keys
        if isinstance(os.environ.get(key), str) and os.environ.get(key)
    }
    environment.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_ATTR_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_PROTOCOL_FROM_USER": "0",
            "GIT_ALLOW_PROTOCOL": "",
            "GIT_PAGER": "",
            "LC_ALL": "C",
            "LANG": "C",
        }
    )
    return environment


def _evidence_sink() -> JsonlDisclosureEvidenceSink:
    return JsonlDisclosureEvidenceSink(_verified_evidence_target())


def _default_policy(plan: GitIdentityPlan) -> DisclosurePolicy:
    destination = f"local-git-read:{plan.plan_fingerprint}"
    return DisclosurePolicy(
        version=_POLICY_VERSION,
        grants=(
            DisclosureGrant(
                provider="local_git",
                provider_class=ProviderClass.LOCAL_OS,
                destination_class=DestinationClass.LOCAL_OS,
                destinations=frozenset({destination}),
                effective_routes=frozenset({_ROUTE}),
                transports=frozenset({TransportClass.PROCESS_HANDOFF}),
                data_categories=frozenset({DataCategory.STRUCTURAL_METADATA}),
                purposes=frozenset({_PURPOSE}),
                callers=frozenset({_CALLER}),
                capability_ids=frozenset({None}),
                initiations=frozenset({InitiationClass.AUTOMATIC}),
            ),
        ),
    )


def _record_admission(plan: GitIdentityPlan, policy: DisclosurePolicy, sink) -> None:
    destination = f"local-git-read:{plan.plan_fingerprint}"
    request = DisclosureRequest(
        caller=_CALLER,
        purpose=_PURPOSE,
        transport=TransportClass.PROCESS_HANDOFF,
        destination_class=DestinationClass.LOCAL_OS,
        provider_class=ProviderClass.LOCAL_OS,
        derived_destination=destination,
        declared_destination=destination,
        policy_version=_POLICY_VERSION,
        data_categories=frozenset({DataCategory.STRUCTURAL_METADATA}),
        action_id=plan.plan_fingerprint,
        declared_provider="local_git",
        derived_provider="local_git",
        effective_route=_ROUTE,
        initiation=InitiationClass.AUTOMATIC,
    )
    decision = DisclosurePolicyEvaluator().evaluate_and_record(request, policy, sink)
    if not decision.may_proceed:
        raise GitChildAdmissionError(
            f"Git child admission failed ({decision.reason})."
        )


def _record_outcome(
    sink,
    *,
    operation: GitIdentityOperation,
    plan: GitIdentityPlan,
    outcome: str,
    exit_code: int | None,
    transport_observed: bool,
) -> None:
    try:
        sink.append(
            GitChildOutcomeRecord(
                operation=operation,
                plan_fingerprint=plan.plan_fingerprint,
                outcome=outcome,
                exit_code=exit_code,
                transport_observed=transport_observed,
            )
        )
    except Exception as error:
        raise GitChildAdmissionError("Git child outcome evidence failed.") from error


def _validate_result(
    operation: GitIdentityOperation,
    completed: subprocess.CompletedProcess[str],
) -> None:
    if operation is GitIdentityOperation.FILTER_GUARD:
        if completed.returncode == 0:
            raise GitChildAdmissionError(
                "Repository Git filters are not admitted for build-identity reads."
            )
        if completed.returncode != 1:
            raise GitChildAdmissionError("Git filter configuration was unavailable.")
        return
    if operation in {GitIdentityOperation.COMMIT, GitIdentityOperation.UNTRACKED}:
        if completed.returncode != 0:
            raise GitChildAdmissionError(
                f"Git identity operation {operation.value} failed."
            )
        return
    if completed.returncode not in {0, 1}:
        raise GitChildAdmissionError(
            f"Git identity operation {operation.value} failed."
        )


def run_git_identity_plan(
    source_root: Path,
    *,
    policy: DisclosurePolicy | object = _DEFAULT,
    evidence_sink: object = _DEFAULT,
    runner: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    timeout: float = 2.0,
) -> dict[GitIdentityOperation, subprocess.CompletedProcess[str]]:
    """Admit the fixed plan before spawning, then execute its guard and four reads."""

    plan = build_git_identity_plan(source_root)
    selected_policy = _default_policy(plan) if policy is _DEFAULT else policy
    try:
        sink = _evidence_sink() if evidence_sink is _DEFAULT else evidence_sink
    except Exception as error:
        raise GitChildAdmissionError("Trusted Git evidence is unavailable.") from error
    if not isinstance(selected_policy, DisclosurePolicy):
        raise GitChildAdmissionError("Git child policy is unavailable.")
    _record_admission(plan, selected_policy, sink)

    environment = minimal_git_environment()
    results: dict[GitIdentityOperation, subprocess.CompletedProcess[str]] = {}
    for operation, command in plan.commands:
        try:
            arguments = {
                "check": False,
                "capture_output": True,
                "text": True,
                "timeout": timeout,
                "env": dict(environment),
                "shell": False,
            }
            try:
                if runner is None:
                    completed = subprocess.run(list(command), **arguments)
                else:
                    completed = runner(list(command), **arguments)
            except subprocess.TimeoutExpired as error:
                _record_outcome(
                    sink,
                    operation=operation,
                    plan=plan,
                    outcome="timeout",
                    exit_code=None,
                    transport_observed=True,
                )
                raise GitChildAdmissionError(
                    f"Git identity operation {operation.value} timed out."
                ) from error
            except OSError as error:
                _record_outcome(
                    sink,
                    operation=operation,
                    plan=plan,
                    outcome="spawn_failed",
                    exit_code=None,
                    transport_observed=False,
                )
                raise GitChildAdmissionError(
                    f"Git identity operation {operation.value} could not start."
                ) from error
            except Exception as error:
                _record_outcome(
                    sink,
                    operation=operation,
                    plan=plan,
                    outcome="execution_unknown",
                    exit_code=None,
                    transport_observed=True,
                )
                raise GitChildAdmissionError(
                    f"Git identity operation {operation.value} had an uncertain outcome."
                ) from error
        except GitChildAdmissionError:
            raise
        except Exception as error:
            raise GitChildAdmissionError(
                f"Git identity operation {operation.value} was unavailable."
            ) from error
        results[operation] = completed
        if operation is GitIdentityOperation.FILTER_GUARD:
            outcome = (
                "filter_configuration_absent"
                if completed.returncode == 1
                else "filter_configuration_present"
                if completed.returncode == 0
                else "exit_failure"
            )
        else:
            outcome = "exit_success" if completed.returncode == 0 else "exit_failure"
        _record_outcome(
            sink,
            operation=operation,
            plan=plan,
            outcome=outcome,
            exit_code=int(completed.returncode),
            transport_observed=True,
        )
        _validate_result(operation, completed)
    return results
