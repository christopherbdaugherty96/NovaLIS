from __future__ import annotations

import os
import shlex
import subprocess
import sys
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


def test_plan_allows_only_filter_guard_and_four_fixed_read_operations(
    tmp_path: Path,
) -> None:
    plan = build_git_identity_plan(tmp_path.resolve())

    assert [operation for operation, _command in plan.commands] == list(
        GitIdentityOperation
    )
    assert len(plan.commands) == 5
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
    assert environment["GIT_ATTR_NOSYSTEM"] == "1"
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


def test_admitted_plan_runs_guard_and_four_reads_with_one_isolated_environment(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-cross-boundary")
    monkeypatch.setenv("GIT_EXTERNAL_DIFF", "must-not-run")
    calls: list[tuple[list[str], dict[str, object]]] = []

    def _run(command, **kwargs):
        calls.append((command, kwargs))
        stdout = "a" * 40 + "\n" if "rev-parse" in command else ""
        returncode = 1 if "--get-regexp" in command else 0
        return _completed(command, returncode=returncode, stdout=stdout)

    sink = _Sink()
    results = run_git_identity_plan(
        tmp_path.resolve(),
        evidence_sink=sink,
        runner=_run,
    )

    assert set(results) == set(GitIdentityOperation)
    assert len(calls) == 5
    assert len(sink.records) == 6  # one admission plus five outcome records
    environments = [kwargs["env"] for _command, kwargs in calls]
    assert all(environment == environments[0] for environment in environments)
    assert all("OPENAI_API_KEY" not in environment for environment in environments)
    assert all("GIT_EXTERNAL_DIFF" not in environment for environment in environments)
    assert all(kwargs["shell"] is False for _command, kwargs in calls)
    assert all("--no-ext-diff" in command for command, _kwargs in calls if "diff" in command)
    assert all("--no-textconv" in command for command, _kwargs in calls if "diff" in command)


def test_configured_clean_filter_is_rejected_without_auxiliary_launch(
    tmp_path: Path,
) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    subprocess.run(["git", "-C", str(repository), "init", "-q"], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(repository), "config", "user.name", "Nova test"],
        check=True,
    )
    payload = repository / "payload.txt"
    payload.write_text("before\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "add", "payload.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "commit", "-q", "-m", "baseline"],
        check=True,
    )

    marker = tmp_path / "filter-launched"
    filter_script = tmp_path / "filter.py"
    filter_script.write_text(
        "from pathlib import Path\n"
        "import sys\n"
        "Path(sys.argv[1]).write_text('launched', encoding='utf-8')\n"
        "sys.stdout.buffer.write(sys.stdin.buffer.read())\n",
        encoding="utf-8",
    )
    arguments = [
        value.replace("\\", "/")
        for value in (sys.executable, str(filter_script), str(marker))
    ]
    filter_command = shlex.join(arguments)
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "config",
            "filter.escape.clean",
            filter_command,
        ],
        check=True,
    )
    (repository / ".gitattributes").write_text(
        "*.txt filter=escape\n", encoding="utf-8"
    )
    payload.write_text("after\n", encoding="utf-8")

    # Prove the original admitted diff shape would execute this repository filter.
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "diff",
            "--quiet",
            "--no-ext-diff",
            "--no-textconv",
            "--ignore-submodules=all",
            "--",
        ],
        check=False,
    )
    assert marker.exists()
    marker.unlink()

    sink = _Sink()
    with pytest.raises(GitChildAdmissionError, match="filters are not admitted"):
        run_git_identity_plan(repository.resolve(), evidence_sink=sink)

    assert not marker.exists()
    assert len(sink.records) == 2  # admission plus filter-guard outcome
    assert sink.records[-1].outcome == "filter_configuration_present"


def test_timeout_records_observed_outcome_before_failure(tmp_path: Path) -> None:
    sink = _Sink()

    def _run(command, **_kwargs):
        if "--get-regexp" in command:
            return _completed(command, returncode=1)
        raise subprocess.TimeoutExpired(command, timeout=2)

    with pytest.raises(GitChildAdmissionError, match="timed out"):
        run_git_identity_plan(tmp_path.resolve(), evidence_sink=sink, runner=_run)

    assert sink.records[-1].outcome == "timeout"
    assert sink.records[-1].transport_observed is True
    assert sink.records[-1].exit_code is None


def test_execution_uncertainty_records_observed_outcome(tmp_path: Path) -> None:
    sink = _Sink()

    def _run(command, **_kwargs):
        if "--get-regexp" in command:
            return _completed(command, returncode=1)
        raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid")

    with pytest.raises(GitChildAdmissionError, match="uncertain outcome"):
        run_git_identity_plan(tmp_path.resolve(), evidence_sink=sink, runner=_run)

    assert sink.records[-1].outcome == "execution_unknown"
    assert sink.records[-1].transport_observed is True


def test_pre_spawn_failure_records_unobserved_outcome(tmp_path: Path) -> None:
    sink = _Sink()

    def _run(command, **_kwargs):
        if "--get-regexp" in command:
            return _completed(command, returncode=1)
        raise FileNotFoundError("git unavailable")

    with pytest.raises(GitChildAdmissionError, match="could not start"):
        run_git_identity_plan(tmp_path.resolve(), evidence_sink=sink, runner=_run)

    assert sink.records[-1].outcome == "spawn_failed"
    assert sink.records[-1].transport_observed is False


@pytest.mark.parametrize(
    "failed_operation",
    [GitIdentityOperation.COMMIT, GitIdentityOperation.UNTRACKED],
)
def test_commit_and_untracked_failures_are_terminal(
    tmp_path: Path,
    failed_operation: GitIdentityOperation,
) -> None:
    plan = build_git_identity_plan(tmp_path.resolve())
    command_operations = {command: operation for operation, command in plan.commands}

    def _run(command, **_kwargs):
        operation = command_operations[tuple(command)]
        if operation is GitIdentityOperation.FILTER_GUARD:
            return _completed(command, returncode=1)
        returncode = 2 if operation is failed_operation else 0
        stdout = "a" * 40 + "\n" if operation is GitIdentityOperation.COMMIT else ""
        return _completed(command, returncode=returncode, stdout=stdout)

    with pytest.raises(GitChildAdmissionError, match=f"{failed_operation.value} failed"):
        run_git_identity_plan(tmp_path.resolve(), evidence_sink=_Sink(), runner=_run)
