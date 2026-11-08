from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from src.llm import ollama_serve_admission as admission


class Sink:
    def __init__(self, events: list[object]):
        self.events = events

    def append(self, event: object) -> None:
        self.events.append(event)


def _trusted_setup(monkeypatch, tmp_path: Path, events: list[object]) -> Path:
    executable = tmp_path / "ollama.exe"
    executable.write_bytes(b"trusted-ollama")
    monkeypatch.setattr(admission, "_trusted_ollama_executable", lambda: executable)
    monkeypatch.setattr(admission, "_ollama_authenticode_is_valid", lambda _path: True)
    monkeypatch.setattr(admission, "_process_evidence_sink", lambda: Sink(events))
    return executable


def test_evidence_failure_prevents_all_process_attempts(monkeypatch, tmp_path):
    executable = tmp_path / "ollama.exe"
    executable.write_bytes(b"trusted-ollama")
    monkeypatch.setattr(admission, "_trusted_ollama_executable", lambda: executable)
    monkeypatch.setattr(admission, "_ollama_authenticode_is_valid", lambda _path: True)

    class FailingSink:
        def append(self, _event):
            raise OSError("read only")

    monkeypatch.setattr(admission, "_process_evidence_sink", lambda: FailingSink())
    spawned = []
    monkeypatch.setattr(
        admission.subprocess,
        "Popen",
        lambda *args, **kwargs: spawned.append((args, kwargs)),
    )

    with pytest.raises(admission.OllamaServeAdmissionError, match="evidence"):
        admission.spawn_verified_ollama_server(correlation_id="startup-test")

    assert spawned == []


def test_allowed_spawn_uses_exact_command_and_minimal_environment(monkeypatch, tmp_path):
    events: list[object] = []
    executable = _trusted_setup(monkeypatch, tmp_path, events)
    spawned = []
    process = object()

    def fake_popen(command, **kwargs):
        spawned.append((command, kwargs))
        return process

    monkeypatch.setattr(admission.subprocess, "Popen", fake_popen)
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-leak")
    monkeypatch.setenv("HTTPS_PROXY", "must-not-leak")
    monkeypatch.setenv("SystemRoot", r"C:\\Windows")

    result = admission.spawn_verified_ollama_server(correlation_id="startup-test")

    assert result is process
    assert spawned[0][0] == [str(executable.resolve()), "serve"]
    environment = spawned[0][1]["env"]
    assert environment["OLLAMA_HOST"] == "http://127.0.0.1:11434"
    assert environment["SystemRoot"] == r"C:\\Windows"
    assert "OPENAI_API_KEY" not in environment
    assert "HTTPS_PROXY" not in environment
    assert spawned[0][1]["stdout"] is subprocess.DEVNULL
    assert spawned[0][1]["stderr"] is subprocess.DEVNULL
    assert len(events) == 3


def test_changed_executable_identity_prevents_spawn(monkeypatch, tmp_path):
    events: list[object] = []
    executable = _trusted_setup(monkeypatch, tmp_path, events)
    spawned = []

    original_record = admission._record_admission

    def mutate_after_record(item, sink):
        original_record(item, sink)
        executable.write_bytes(b"replacement")

    monkeypatch.setattr(admission, "_record_admission", mutate_after_record)
    monkeypatch.setattr(
        admission.subprocess,
        "Popen",
        lambda *args, **kwargs: spawned.append((args, kwargs)),
    )

    with pytest.raises(admission.OllamaServeAdmissionError, match="changed"):
        admission.spawn_verified_ollama_server(correlation_id="startup-test")

    assert spawned == []


def test_outcome_evidence_failure_terminates_spawned_process(monkeypatch, tmp_path):
    executable = tmp_path / "ollama.exe"
    executable.write_bytes(b"trusted-ollama")
    monkeypatch.setattr(admission, "_trusted_ollama_executable", lambda: executable)
    monkeypatch.setattr(admission, "_ollama_authenticode_is_valid", lambda _path: True)

    class FailThirdAppend:
        def __init__(self):
            self.count = 0

        def append(self, _event):
            self.count += 1
            if self.count == 3:
                raise OSError("outcome unavailable")

    class Process:
        terminated = False

        def terminate(self):
            self.terminated = True

    process = Process()
    monkeypatch.setattr(admission, "_process_evidence_sink", FailThirdAppend)
    monkeypatch.setattr(admission.subprocess, "Popen", lambda *_a, **_k: process)

    with pytest.raises(admission.OllamaServeAdmissionError, match="outcome evidence"):
        admission.spawn_verified_ollama_server(correlation_id="startup-test")

    assert process.terminated is True


def test_non_windows_or_untrusted_identity_fails_closed(monkeypatch):
    monkeypatch.setattr(
        admission,
        "_trusted_ollama_executable",
        lambda: (_ for _ in ()).throw(
            admission.OllamaServeAdmissionError("requires Windows")
        ),
    )
    spawned = []
    monkeypatch.setattr(
        admission.subprocess,
        "Popen",
        lambda *args, **kwargs: spawned.append((args, kwargs)),
    )

    # Depending on the host, the trusted evidence target can reject the
    # operation before executable identity reaches its Windows-only check.
    with pytest.raises(admission.OllamaServeAdmissionError, match="evidence|Windows"):
        admission.spawn_verified_ollama_server(correlation_id="startup-test")

    assert spawned == []


@pytest.mark.parametrize("correlation_id", ["", "x" * 161])
def test_unbounded_correlation_identity_is_denied_before_spawn(
    monkeypatch, tmp_path, correlation_id
):
    events: list[object] = []
    _trusted_setup(monkeypatch, tmp_path, events)
    spawned = []
    monkeypatch.setattr(
        admission.subprocess,
        "Popen",
        lambda *args, **kwargs: spawned.append((args, kwargs)),
    )

    with pytest.raises(admission.OllamaServeAdmissionError, match="correlation"):
        admission.spawn_verified_ollama_server(correlation_id=correlation_id)

    assert spawned == []


def test_untrusted_publisher_is_denied_before_spawn(monkeypatch, tmp_path):
    events: list[object] = []
    executable = _trusted_setup(monkeypatch, tmp_path, events)
    monkeypatch.setattr(admission, "_ollama_authenticode_is_valid", lambda _path: False)
    spawned = []
    monkeypatch.setattr(
        admission.subprocess,
        "Popen",
        lambda *args, **kwargs: spawned.append((args, kwargs)),
    )

    with pytest.raises(admission.OllamaServeAdmissionError, match="publisher"):
        admission.spawn_verified_ollama_server(correlation_id="startup-test")

    assert executable.is_file()
    assert spawned == []
