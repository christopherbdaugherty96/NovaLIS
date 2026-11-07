from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest
from src.llm import ollama_setup_admission as admission

ROOT = Path(__file__).resolve().parents[3]


def _load_fetch_models():
    path = ROOT / "scripts" / "fetch_models.py"
    spec = importlib.util.spec_from_file_location("nova_fetch_models", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_process_is_not_spawned_when_admission_evidence_fails(monkeypatch, tmp_path):
    executable = tmp_path / "ollama.exe"
    executable.write_bytes(b"signed ollama")
    spawned = []

    monkeypatch.setattr(admission, "_trusted_ollama_executable", lambda: executable)
    monkeypatch.setattr(
        admission,
        "_process_evidence_sink",
        lambda: (_ for _ in ()).throw(OSError("evidence unavailable")),
    )
    monkeypatch.setattr(admission.subprocess, "run", lambda *a, **k: spawned.append((a, k)))

    with pytest.raises(admission.OllamaSetupAdmissionError, match="evidence"):
        admission.run_ollama_command(
            operation=admission.OllamaSetupOperation.LIST,
            model=admission.APPROVED_INSTALL_MODEL,
            correlation_id="install-attempt-1",
            online_consent=False,
        )

    assert spawned == []


def test_pull_requires_exact_model_and_explicit_online_consent(monkeypatch):
    monkeypatch.setattr(
        admission,
        "_trusted_ollama_executable",
        lambda: Path(r"C:\Users\Nova\AppData\Local\Programs\Ollama\ollama.exe"),
    )
    monkeypatch.setattr(admission, "_ollama_authenticode_is_valid", lambda _path: True)
    monkeypatch.setattr(admission, "_attest_ollama_listener", lambda: None)

    for model, consent in (("other:model", True), (admission.APPROVED_INSTALL_MODEL, False)):
        with pytest.raises(admission.OllamaSetupAdmissionError):
            admission.build_ollama_admission(
                operation=admission.OllamaSetupOperation.PULL,
                model=model,
                correlation_id="install-attempt-2",
                online_consent=consent,
            )


def test_exact_command_and_minimal_environment_are_bound_before_spawn(
    monkeypatch, tmp_path
):
    executable = tmp_path / "ollama.exe"
    executable.write_bytes(b"signed ollama")
    recorded = []
    spawned = []

    class Sink:
        def append(self, record):
            recorded.append(record.as_dict())

    monkeypatch.setattr(admission, "_trusted_ollama_executable", lambda: executable)
    monkeypatch.setattr(admission, "_attest_ollama_listener", lambda: None)
    monkeypatch.setattr(admission, "_ollama_authenticode_is_valid", lambda _path: True)
    monkeypatch.setattr(admission, "_process_evidence_sink", lambda: Sink())

    def fake_run(command, **kwargs):
        spawned.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0, "NAME ID SIZE\ngemma4:e4b abc 1 GB\n", "")

    monkeypatch.setattr(admission.subprocess, "run", fake_run)
    result = admission.run_ollama_command(
        operation=admission.OllamaSetupOperation.LIST,
        model=admission.APPROVED_INSTALL_MODEL,
        correlation_id="install-attempt-3",
        online_consent=False,
    )

    assert result.returncode == 0
    assert spawned[0][0] == [str(executable.resolve()), "list"]
    assert spawned[0][1]["env"] == admission._minimal_child_environment()
    assert [item["record_kind"] for item in recorded] == [
        "verification_process_admission",
        "disclosure_policy_evaluation",
        "delegated_process_outcome",
    ]
    assert recorded[2]["outcome"] == "exit_success"


def test_fetch_models_rejects_silent_or_arbitrary_pull(monkeypatch):
    fetch_models = _load_fetch_models()
    calls = []
    monkeypatch.setattr(fetch_models, "run_ollama_command", lambda **kwargs: calls.append(kwargs))

    assert fetch_models.main([]) == 3
    assert fetch_models.main(["--allow-online-pull", "--model", "other:model"]) == 3
    assert calls == []


def test_fetch_models_verifies_exact_model_after_pull(monkeypatch):
    fetch_models = _load_fetch_models()
    results = iter(
        [
            subprocess.CompletedProcess([], 0, "NAME ID SIZE\n", ""),
            subprocess.CompletedProcess([], 0, "download complete\n", ""),
            subprocess.CompletedProcess(
                [], 0, f"NAME ID SIZE\n{fetch_models.DEFAULT_MODEL} abc 1 GB\n", ""
            ),
        ]
    )
    calls = []

    def run(**kwargs):
        calls.append(kwargs)
        return next(results)

    monkeypatch.setattr(fetch_models, "run_ollama_command", run)
    rc = fetch_models.main(
        [
            "--allow-online-pull",
            "--model",
            fetch_models.DEFAULT_MODEL,
            "--correlation-id",
            "install-attempt-4",
        ]
    )

    assert rc == 0
    assert [item["operation"] for item in calls] == [
        admission.OllamaSetupOperation.LIST,
        admission.OllamaSetupOperation.PULL,
        admission.OllamaSetupOperation.LIST,
    ]


def test_installer_silent_mode_never_grants_model_pull():
    bootstrap = (ROOT / "installer" / "windows" / "nova_bootstrap.ps1").read_text(
        encoding="utf-8"
    )
    inno = (ROOT / "installer" / "windows" / "nova_setup.iss").read_text(
        encoding="utf-8"
    )

    assert "AllowOnlineModelSetup" in bootstrap
    model_step = bootstrap.split("# Step 5: Pull model", 1)[1]
    assert "Silent mode cannot authorize an online model pull" in model_step
    assert "Read-Host" in model_step
    assert "--allow-online-pull" in bootstrap
    assert "-AllowOnlineModelSetup" not in inno
    assert "-SkipModel" in inno


def test_outcome_record_never_contains_process_output():
    record = admission.DelegatedProcessOutcomeRecord(
        operation=admission.OllamaSetupOperation.PULL,
        command_fingerprint="abc",
        executable_fingerprint="def",
        correlation_id="install-attempt-5",
        outcome="exit_failure",
        exit_code=9,
        transport_observed=True,
    ).as_dict()

    serialized = json.dumps(record)
    assert "stdout" not in serialized
    assert "stderr" not in serialized


def test_identity_verifier_runs_only_after_evidence_is_durable(monkeypatch, tmp_path):
    executable = tmp_path / "ollama.exe"
    executable.write_bytes(b"signed ollama")
    order = []

    class Sink:
        def append(self, record):
            order.append(record.as_dict()["record_kind"])

    monkeypatch.setattr(admission, "_trusted_ollama_executable", lambda: executable)
    monkeypatch.setattr(
        admission,
        "_ollama_authenticode_is_valid",
        lambda _path: order.append("authenticode_verifier") or True,
    )
    monkeypatch.setattr(admission, "_attest_ollama_listener", lambda: None)
    monkeypatch.setattr(admission, "_process_evidence_sink", lambda: Sink())
    monkeypatch.setattr(
        admission.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, "NAME\n", ""),
    )

    admission.run_ollama_command(
        operation=admission.OllamaSetupOperation.LIST,
        model=admission.APPROVED_INSTALL_MODEL,
        correlation_id="install-attempt-order",
        online_consent=False,
    )

    assert order.index("verification_process_admission") < order.index(
        "authenticode_verifier"
    )


def test_spawn_failure_is_recorded_as_unobserved(monkeypatch, tmp_path):
    executable = tmp_path / "ollama.exe"
    executable.write_bytes(b"signed ollama")
    records = []

    class Sink:
        def append(self, record):
            records.append(record.as_dict())

    monkeypatch.setattr(admission, "_trusted_ollama_executable", lambda: executable)
    monkeypatch.setattr(admission, "_attest_ollama_listener", lambda: None)
    monkeypatch.setattr(admission, "_ollama_authenticode_is_valid", lambda _path: True)
    monkeypatch.setattr(admission, "_process_evidence_sink", lambda: Sink())

    def fail_spawn(*args, **kwargs):
        raise OSError("process was not created")

    monkeypatch.setattr(admission.subprocess, "run", fail_spawn)
    with pytest.raises(OSError):
        admission.run_ollama_command(
            operation=admission.OllamaSetupOperation.LIST,
            model=admission.APPROVED_INSTALL_MODEL,
            correlation_id="install-attempt-spawn-failure",
            online_consent=False,
        )

    assert records[-1]["outcome"] == "spawn_failure"
    assert records[-1]["transport_observed"] is False


@pytest.mark.parametrize(
    ("result", "expected"),
    [
        (subprocess.CompletedProcess([], 8, "", "failure detail"), "exit_failure"),
        (subprocess.CompletedProcess([], 0, "not a model inventory", ""), "exit_success"),
    ],
)
def test_command_outcomes_are_recorded_without_process_content(
    monkeypatch, tmp_path, result, expected
):
    executable = tmp_path / "ollama.exe"
    executable.write_bytes(b"signed ollama")
    records = []

    class Sink:
        def append(self, record):
            records.append(record.as_dict())

    monkeypatch.setattr(admission, "_trusted_ollama_executable", lambda: executable)
    monkeypatch.setattr(admission, "_attest_ollama_listener", lambda: None)
    monkeypatch.setattr(admission, "_ollama_authenticode_is_valid", lambda _path: True)
    monkeypatch.setattr(admission, "_process_evidence_sink", lambda: Sink())
    monkeypatch.setattr(admission.subprocess, "run", lambda *a, **k: result)

    completed = admission.run_ollama_command(
        operation=admission.OllamaSetupOperation.LIST,
        model=admission.APPROVED_INSTALL_MODEL,
        correlation_id="install-attempt-outcome",
        online_consent=False,
    )

    assert completed.returncode == result.returncode
    assert records[-1]["outcome"] == expected
    assert "failure detail" not in json.dumps(records)
    assert "not a model inventory" not in json.dumps(records)


def test_timeout_records_outcome(monkeypatch, tmp_path):
    executable = tmp_path / "ollama.exe"
    executable.write_bytes(b"signed ollama")
    records = []

    class Sink:
        def append(self, record):
            records.append(record.as_dict())

    monkeypatch.setattr(admission, "_trusted_ollama_executable", lambda: executable)
    monkeypatch.setattr(admission, "_attest_ollama_listener", lambda: None)
    monkeypatch.setattr(admission, "_ollama_authenticode_is_valid", lambda _path: True)
    monkeypatch.setattr(admission, "_process_evidence_sink", lambda: Sink())

    def time_out(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(admission.subprocess, "run", time_out)
    with pytest.raises(subprocess.TimeoutExpired):
        admission.run_ollama_command(
            operation=admission.OllamaSetupOperation.PULL,
            model=admission.APPROVED_INSTALL_MODEL,
            correlation_id="install-attempt-timeout",
            online_consent=True,
            timeout=1,
        )
    assert records[-1]["outcome"] == "timeout"


def test_executable_change_after_evidence_prevents_spawn(monkeypatch, tmp_path):
    executable = tmp_path / "ollama.exe"
    executable.write_bytes(b"first")
    records = []
    spawned = []

    class Sink:
        def append(self, record):
            records.append(record.as_dict())
            if record.as_dict()["record_kind"] == "disclosure_policy_evaluation":
                executable.write_bytes(b"replacement")

    monkeypatch.setattr(admission, "_trusted_ollama_executable", lambda: executable)
    monkeypatch.setattr(admission, "_attest_ollama_listener", lambda: None)
    monkeypatch.setattr(admission, "_ollama_authenticode_is_valid", lambda _path: True)
    monkeypatch.setattr(admission, "_process_evidence_sink", lambda: Sink())
    monkeypatch.setattr(admission.subprocess, "run", lambda *a, **k: spawned.append((a, k)))

    with pytest.raises(admission.OllamaSetupAdmissionError, match="changed"):
        admission.run_ollama_command(
            operation=admission.OllamaSetupOperation.LIST,
            model=admission.APPROVED_INSTALL_MODEL,
            correlation_id="install-attempt-replaced",
            online_consent=False,
        )
    assert spawned == []


def test_successful_pull_does_not_claim_model_ready_when_inventory_is_malformed(
    monkeypatch,
):
    fetch_models = _load_fetch_models()
    results = iter(
        [
            subprocess.CompletedProcess([], 0, "NAME ID SIZE\n", ""),
            subprocess.CompletedProcess([], 0, "download complete\n", ""),
            subprocess.CompletedProcess([], 0, "unexpected output\n", ""),
        ]
    )
    monkeypatch.setattr(fetch_models, "run_ollama_command", lambda **kwargs: next(results))

    assert (
        fetch_models.main(
            [
                "--allow-online-pull",
                "--model",
                fetch_models.DEFAULT_MODEL,
                "--correlation-id",
                "install-attempt-malformed",
            ]
        )
        == 2
    )
