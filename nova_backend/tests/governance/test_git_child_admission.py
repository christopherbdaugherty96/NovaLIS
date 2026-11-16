from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from src.governor.disclosure_policy import DisclosurePolicy
from src.governor.git_child_admission import (
    GitChildAdmissionError,
    GitIdentityOperation,
    build_git_identity_plan,
    minimal_git_environment,
    run_git_identity_plan,
)


class _Sink:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.records: list[object] = []

    def append(self, record: object) -> None:
        if self.fail:
            raise OSError("evidence unavailable")
        self.records.append(record)


def _completed(command, *, returncode: int = 0, stdout: str = ""):
    return subprocess.CompletedProcess(command, returncode, stdout, "")


def test_plan_allows_only_four_fixed_read_operations(tmp_path: Path) -> None:
    plan = build_git_identity_plan(tmp_path.resolve())

    assert [operation for operation, _command in plan.commands] == list(
        GitIdentityOperation
    )
    assert len(plan.commands) == 4
    for _operation, command in plan.commands:
        joined = " ".join(command)
        assert command[0] == "git"
        assert "protocol.allow=never" in command
        assert "credential.helper=" in command
        assert "core.fsmonitor=false" in command
        assert not any(
            forbidden in command
            for forbidden in ("fetch", "pull", "push", "clone", "remote", "commit")
        )
        assert "http://" not in joined and "https://" not in joined


def test_minimal_environment_excludes_credentials_and_ambient_git_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    hostile = {
        "OPENAI_API_KEY": "secret-openai",
        "BRAVE_API_KEY": "secret-brave",
        "HTTPS_PROXY": "http://proxy.invalid",
        "NETRC": "remote-netrc",
        "REQUESTS_CA_BUNDLE": "remote-ca",
        "SSLKEYLOGFILE": "remote-keylog",
        "GIT_EXTERNAL_DIFF": "malicious-diff",
        "GIT_SSH_COMMAND": "malicious-ssh",
        "GIT_ASKPASS": "malicious-askpass",
        "GIT_CONFIG_SYSTEM": "malicious-system-config",
    }
    for key, value in hostile.items():
        monkeypatch.setenv(key, value)

    environment = minimal_git_environment()

    assert not (set(hostile) & set(environment))
    assert environment["GIT_CONFIG_NOSYSTEM"] == "1"
    assert environment["GIT_CONFIG_GLOBAL"] == os.devnull
    assert environment["GIT_TERMINAL_PROMPT"] == "0"
    assert environment["GIT_NO_LAZY_FETCH"] == "1"
    assert environment["GIT_PROTOCOL_FROM_USER"] == "0"
    assert environment["GIT_ALLOW_PROTOCOL"] == ""


@pytest.mark.parametrize(
    ("policy", "sink"),
    [
        (DisclosurePolicy(version="deny", grants=()), _Sink()),
        (None, _Sink()),
    ],
)
def test_denial_or_missing_policy_spawns_nothing(
    tmp_path: Path,
    policy,
    sink,
) -> None:
    spawned: list[object] = []

    with pytest.raises(GitChildAdmissionError):
        run_git_identity_plan(
            tmp_path.resolve(),
            policy=policy,
            evidence_sink=sink,
            runner=lambda *args, **kwargs: spawned.append((args, kwargs)),
        )

    assert spawned == []


@pytest.mark.parametrize("sink", [None, _Sink(fail=True)])
def test_missing_or_failed_evidence_spawns_nothing(
    tmp_path: Path,
    sink,
) -> None:
    spawned: list[object] = []

    with pytest.raises(GitChildAdmissionError):
        run_git_identity_plan(
            tmp_path.resolve(),
            evidence_sink=sink,
            runner=lambda *args, **kwargs: spawned.append((args, kwargs)),
        )

    assert spawned == []


def test_admitted_plan_runs_all_four_with_one_isolated_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-cross-boundary")
    monkeypatch.setenv("GIT_EXTERNAL_DIFF", "must-not-run")
    calls: list[tuple[list[str], dict[str, object]]] = []

    def _run(command, **kwargs):
        calls.append((command, kwargs))
        stdout = "a" * 40 + "\n" if "rev-parse" in command else ""
        return _completed(command, stdout=stdout)

    sink = _Sink()
    results = run_git_identity_plan(
        tmp_path.resolve(),
        evidence_sink=sink,
        runner=_run,
    )

    assert set(results) == set(GitIdentityOperation)
    assert len(calls) == 4
    assert len(sink.records) == 5  # one admission plus four outcome records
    environments = [kwargs["env"] for _command, kwargs in calls]
    assert all(environment == environments[0] for environment in environments)
    assert all("OPENAI_API_KEY" not in environment for environment in environments)
    assert all("GIT_EXTERNAL_DIFF" not in environment for environment in environments)
    assert all(kwargs["shell"] is False for _command, kwargs in calls)
    assert all("--no-ext-diff" in command for command, _kwargs in calls if "diff" in command)
    assert all("--no-textconv" in command for command, _kwargs in calls if "diff" in command)
