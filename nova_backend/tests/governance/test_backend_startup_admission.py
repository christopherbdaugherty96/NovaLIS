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
    assert "AWS_SECRET_ACCESS_KEY" not in environment
    assert "HTTP_PROXY" not in environment
    assert "HTTPS_PROXY" not in environment
    assert captured["shell"] is False
    assert sink.records[0]["record_kind"] == "disclosure_policy_evaluation"
    assert sink.records[1]["outcome"] == "spawn_observed_not_ready"
    assert "approved-provider-secret" not in json.dumps(sink.records)
    assert sink.records[0]["credential_categories"] == ["api_key"]


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
