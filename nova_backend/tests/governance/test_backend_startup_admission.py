from __future__ import annotations

import json
import os
import subprocess
from contextlib import nullcontext
from pathlib import Path

import pytest
from src.governor import backend_startup_admission as admission
from src.governor.disclosure_policy import InitiationClass


class Sink:
    def __init__(self, *, fail: bool = False) -> None:
        self.records: list[dict[str, object]] = []
        self.fail = fail

    def append(self, record) -> None:
        if self.fail:
            raise OSError("evidence unavailable")
        self.records.append(record.as_dict())


def _python(tmp_path: Path) -> Path:
    executable = tmp_path / "python.exe"
    executable.write_bytes(b"trusted-python")
    return executable


def test_denied_or_missing_evidence_makes_zero_process_attempts(tmp_path, monkeypatch):
    attempts: list[object] = []
    monkeypatch.setattr(admission.subprocess, "Popen", lambda *a, **k: attempts.append((a, k)))

    with pytest.raises(admission.BackendStartupAdmissionError, match="evidence"):
        admission.spawn_admitted_backend(
            executable=_python(tmp_path),
            backend_dir=tmp_path,
            host="127.0.0.1",
            port=8000,
            evidence_sink=Sink(fail=True),
        )

    assert attempts == []


def test_spawn_binds_exact_command_and_constrained_environment(tmp_path, monkeypatch):
    executable = _python(tmp_path)
    captured: dict[str, object] = {}
    process = type("Process", (), {"pid": 41, "poll": lambda self: None})()

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured.update(kwargs)
        return process

    monkeypatch.setattr(admission.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(admission, "_locked_executable_identity", lambda _path: nullcontext())
    monkeypatch.setenv("OPENAI_API_KEY", "approved-provider-secret")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "deepseek-provider-secret")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-reasoner")
    monkeypatch.setenv("NOVA_SHOPIFY_ACCESS_TOKEN", "shopify-provider-secret")
    monkeypatch.setenv("NOVA_GOOGLE_OAUTH_CLIENT_SECRET", "google-client-secret")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "unrelated-secret")
    monkeypatch.setenv("HTTP_PROXY", "http://proxy.invalid")
    sink = Sink()

    launch = admission.spawn_admitted_backend(
        executable=executable,
        backend_dir=tmp_path,
        host="127.0.0.1",
        port=8000,
        evidence_sink=sink,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    assert launch.process is process
    assert captured["command"] == [
        str(executable.resolve()),
        "-m",
        "uvicorn",
        "src.brain_server:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--app-dir",
        str(tmp_path.resolve()),
    ]
    environment = captured["env"]
    assert environment["OPENAI_API_KEY"] == "approved-provider-secret"
    assert environment["DEEPSEEK_API_KEY"] == "deepseek-provider-secret"
    assert environment["DEEPSEEK_MODEL"] == "deepseek-reasoner"
    assert environment["NOVA_SHOPIFY_ACCESS_TOKEN"] == "shopify-provider-secret"
    assert environment["NOVA_GOOGLE_OAUTH_CLIENT_SECRET"] == "google-client-secret"
    assert "AWS_SECRET_ACCESS_KEY" not in environment
    assert "HTTP_PROXY" not in environment
    assert "HTTPS_PROXY" not in environment
    assert captured["shell"] is False
    assert sink.records[0]["record_kind"] == "disclosure_policy_evaluation"
    assert sink.records[1]["outcome"] == "spawn_observed_not_ready"
    assert "approved-provider-secret" not in json.dumps(sink.records)
    assert "deepseek-provider-secret" not in json.dumps(sink.records)
    assert "shopify-provider-secret" not in json.dumps(sink.records)
    assert "google-client-secret" not in json.dumps(sink.records)
    assert sink.records[0]["credential_categories"] == ["api_key", "origin_credential"]


def test_minimal_environment_preserves_only_canonical_windows_powershell(tmp_path, monkeypatch):
    executable = _python(tmp_path)
    windows_root = tmp_path / "Windows"
    powershell_dir = windows_root / "System32" / "WindowsPowerShell" / "v1.0"
    powershell_dir.mkdir(parents=True)
    (powershell_dir / "powershell.exe").write_bytes(b"system-powershell")
    monkeypatch.setenv("SystemRoot", str(windows_root))
    monkeypatch.setenv("ProgramFiles", str(tmp_path / "NoGit"))
    monkeypatch.setenv("ProgramFiles(x86)", str(tmp_path / "NoGitX86"))
    monkeypatch.setenv("PATH", str(tmp_path / "ambient-bin"))

    environment = admission._minimal_backend_environment(executable)

    path_entries = environment["PATH"].split(os.pathsep)
    assert path_entries[:2] == [
        str(powershell_dir),
        str(windows_root / "System32"),
    ]
    assert path_entries[-1] == str(executable.parent)
    assert str(tmp_path / "ambient-bin") not in path_entries


def test_minimal_environment_binds_external_ffmpeg_without_inheriting_path(
    tmp_path, monkeypatch
):
    executable = _python(tmp_path)
    external_bin = tmp_path / "external-bin"
    external_bin.mkdir()
    ffmpeg_name = "ffmpeg.exe" if os.name == "nt" else "ffmpeg"
    ffmpeg = external_bin / ffmpeg_name
    ffmpeg.write_bytes(b"local-ffmpeg")
    monkeypatch.setenv("PATH", str(external_bin))

    environment = admission._minimal_backend_environment(executable)

    assert environment["NOVA_FFMPEG_PATH"] == str(ffmpeg.resolve())
    assert str(external_bin) not in environment["PATH"].split(os.pathsep)


@pytest.mark.skipif(os.name != "nt", reason="Windows canonical Git path contract")
def test_minimal_environment_preserves_only_canonical_windows_git(tmp_path, monkeypatch):
    executable = _python(tmp_path)
    program_files = tmp_path / "Program Files"
    git_dir = program_files / "Git" / "cmd"
    git_dir.mkdir(parents=True)
    (git_dir / "git.exe").write_bytes(b"canonical-git")
    monkeypatch.setenv("ProgramFiles", str(program_files))
    monkeypatch.setenv("ProgramFiles(x86)", str(tmp_path / "NoGitX86"))
    monkeypatch.setenv("PATH", str(tmp_path / "ambient-git"))

    environment = admission._minimal_backend_environment(executable)

    path_entries = environment["PATH"].split(os.pathsep)
    assert str(git_dir) in path_entries
    assert str(tmp_path / "ambient-git") not in path_entries


def test_relative_runtime_dir_is_bound_to_launcher_location(tmp_path, monkeypatch):
    executable = _python(tmp_path)
    launcher_dir = tmp_path / "launcher"
    launcher_dir.mkdir()
    monkeypatch.chdir(launcher_dir)
    monkeypatch.setenv("NOVA_RUNTIME_DIR", "relative-state")

    environment = admission._minimal_backend_environment(executable)

    assert environment["NOVA_RUNTIME_DIR"] == str(launcher_dir / "relative-state")


def test_relative_calendar_path_is_bound_to_launcher_location(tmp_path, monkeypatch):
    executable = _python(tmp_path)
    launcher_dir = tmp_path / "launcher"
    launcher_dir.mkdir()
    monkeypatch.chdir(launcher_dir)
    monkeypatch.setenv("NOVA_CALENDAR_ICS_PATH", "calendar.ics")

    environment = admission._minimal_backend_environment(executable)

    assert environment["NOVA_CALENDAR_ICS_PATH"] == str(launcher_dir / "calendar.ics")


def test_relative_piper_model_path_is_bound_to_launcher_location(tmp_path, monkeypatch):
    executable = _python(tmp_path)
    launcher_dir = tmp_path / "launcher"
    launcher_dir.mkdir()
    monkeypatch.chdir(launcher_dir)
    monkeypatch.setenv("NOVA_PIPER_MODEL_PATH", "voice.onnx")

    environment = admission._minimal_backend_environment(executable)

    assert environment["NOVA_PIPER_MODEL_PATH"] == str(launcher_dir / "voice.onnx")


@pytest.mark.skipif(os.name == "nt", reason="POSIX virtualenv symlink contract")
def test_symlinked_virtualenv_interpreter_is_preserved_for_invocation(tmp_path):
    base_dir = tmp_path / "base"
    base_dir.mkdir()
    base_python = base_dir / "python"
    base_python.write_bytes(b"base-python")
    virtualenv_bin = tmp_path / "venv" / "bin"
    virtualenv_bin.mkdir(parents=True)
    virtualenv_python = virtualenv_bin / "python"
    virtualenv_python.symlink_to(base_python)

    plan = admission.build_backend_startup_plan(
        executable=virtualenv_python,
        backend_dir=tmp_path,
        host="127.0.0.1",
        port=8000,
    )

    assert plan.executable == virtualenv_python.absolute()
    assert plan.executable_identity == base_python.resolve()
    assert plan.command[0] == str(virtualenv_python.absolute())
    assert str(virtualenv_bin) in dict(plan.environment)["PATH"].split(os.pathsep)


def test_changed_executable_is_denied_before_spawn(tmp_path, monkeypatch):
    executable = _python(tmp_path)
    attempts: list[object] = []
    original_record = admission._record_admission

    def mutate_after_record(plan, sink):
        original_record(plan, sink)
        executable.write_bytes(b"replacement")

    monkeypatch.setattr(admission, "_record_admission", mutate_after_record)
    monkeypatch.setattr(admission.subprocess, "Popen", lambda *a, **k: attempts.append((a, k)))
    monkeypatch.setattr(admission, "_locked_executable_identity", lambda _path: nullcontext())

    with pytest.raises(admission.BackendStartupAdmissionError, match="changed"):
        admission.spawn_admitted_backend(
            executable=executable,
            backend_dir=tmp_path,
            host="127.0.0.1",
            port=8000,
            evidence_sink=Sink(),
        )

    assert attempts == []


def test_readiness_outcome_is_distinct_from_spawn(tmp_path, monkeypatch):
    executable = _python(tmp_path)
    process = type("Process", (), {"pid": 41, "poll": lambda self: None})()
    monkeypatch.setattr(admission.subprocess, "Popen", lambda *a, **k: process)
    monkeypatch.setattr(admission, "_locked_executable_identity", lambda _path: nullcontext())
    sink = Sink()
    launch = admission.spawn_admitted_backend(
        executable=executable,
        backend_dir=tmp_path,
        host="127.0.0.1",
        port=8000,
        evidence_sink=sink,
    )

    admission.record_backend_outcome(launch, outcome="ready", evidence_sink=sink)

    assert [record.get("outcome") for record in sink.records] == [
        None,
        "spawn_observed_not_ready",
        "ready",
    ]


@pytest.mark.parametrize("host", ["localhost", "0.0.0.0", "192.168.1.2"])
def test_noncanonical_backend_bind_is_denied(tmp_path, host):
    with pytest.raises(admission.BackendStartupAdmissionError):
        admission.build_backend_startup_plan(
            executable=_python(tmp_path),
            backend_dir=tmp_path,
            host=host,
            port=8000,
        )


def test_automatic_startup_is_bound_to_automatic_initiation(tmp_path, monkeypatch):
    executable = _python(tmp_path)
    process = type("Process", (), {"pid": 41, "poll": lambda self: None})()
    monkeypatch.setattr(admission.subprocess, "Popen", lambda *a, **k: process)
    monkeypatch.setattr(admission, "_locked_executable_identity", lambda _path: nullcontext())
    sink = Sink()

    admission.spawn_admitted_backend(
        executable=executable,
        backend_dir=tmp_path,
        host="127.0.0.1",
        port=8000,
        initiation=InitiationClass.AUTOMATIC,
        evidence_sink=sink,
    )

    assert sink.records[0]["initiation"] == InitiationClass.AUTOMATIC.value


@pytest.mark.skipif(os.name != "nt", reason="Windows executable lock contract")
def test_windows_executable_identity_lock_blocks_replacement(tmp_path):
    executable = _python(tmp_path)

    with admission._locked_executable_identity(executable):
        with pytest.raises(PermissionError):
            executable.write_bytes(b"replacement")


def test_failed_post_spawn_evidence_terminates_child(tmp_path, monkeypatch):
    executable = _python(tmp_path)

    class Process:
        pid = 41
        terminated = False

        def terminate(self):
            self.terminated = True

    process = Process()
    sink = Sink()
    original_append = sink.append

    def fail_after_admission(record):
        if getattr(record, "outcome", "") == "spawn_observed_not_ready":
            raise OSError("outcome evidence unavailable")
        original_append(record)

    sink.append = fail_after_admission
    monkeypatch.setattr(admission.subprocess, "Popen", lambda *a, **k: process)
    monkeypatch.setattr(admission, "_locked_executable_identity", lambda _path: nullcontext())

    with pytest.raises(admission.BackendStartupAdmissionError, match="outcome evidence"):
        admission.spawn_admitted_backend(
            executable=executable,
            backend_dir=tmp_path,
            host="127.0.0.1",
            port=8000,
            evidence_sink=sink,
        )

    assert process.terminated is True
