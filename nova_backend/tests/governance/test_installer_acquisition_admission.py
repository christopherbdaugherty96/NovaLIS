from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
BOOTSTRAP = ROOT / "installer" / "windows" / "nova_bootstrap.ps1"
ADMISSION = ROOT / "installer" / "windows" / "installer_acquisition_admission.ps1"
SETUP = ROOT / "installer" / "windows" / "nova_setup.iss"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_bootstrap_has_no_direct_winget_or_pip_acquisition() -> None:
    source = _text(BOOTSTRAP)

    assert not re.search(r"(?im)^\s*winget\s+install\b", source)
    assert not re.search(r"(?im)&\s*\$VenvPython\s+-m\s+pip\s+install\b", source)
    assert "Invoke-NovaInstallerAcquisition" in source


def test_noninteractive_mode_never_manufactures_online_consent() -> None:
    source = _text(BOOTSTRAP)

    assert 'if ($NonInteractive) { $install = "Y" }' not in source
    assert "Silent mode cannot authorize" in source
    assert "AllowOnlinePythonInstall" in source
    assert "AllowOnlineOllamaInstall" in source
    assert "AllowOnlinePipSetup" in source


def test_all_four_acquisitions_use_exact_admission_operations() -> None:
    source = _text(BOOTSTRAP)

    for operation in ("winget_python", "winget_ollama", "pip_install_nova"):
        assert f'-Operation "{operation}"' in source
    # The fourth historical acquisition is removed rather than admitted.
    assert '-Operation "pip_upgrade"' not in source
    assert "-m pip install --upgrade pip" not in source


def test_admission_binds_exact_sources_and_disables_ambient_configuration() -> None:
    source = _text(ADMISSION)

    assert '"Python.Python.3.12"' in source
    assert '"Ollama.Ollama"' in source
    assert '"--source", "winget"' in source
    assert '"--exact"' in source
    assert '"--isolated"' in source
    assert '"--index-url", "https://pypi.org/simple"' in source
    assert 'SetEnvironmentVariable("PIP_CONFIG_FILE", "NUL", "Process")' in source
    assert "GetTempFileName" not in source
    for forbidden in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
        "PIP_INDEX_URL",
        "PIP_EXTRA_INDEX_URL",
        "PIP_TRUSTED_HOST",
    ):
        assert forbidden in source


def test_evidence_is_written_before_process_start_and_outcome_is_separate() -> None:
    source = _text(ADMISSION)

    evidence = source.index("Write-NovaAcquisitionEvidence -Record $admissionRecord")
    process = source.index("& $executable @arguments")
    outcome = source.index("Write-NovaAcquisitionEvidence -Record $outcomeRecord")
    assert evidence < process < outcome
    assert 'record_kind = "installer_acquisition_admission"' in source
    assert 'record_kind = "delegated_process_outcome"' in source
    assert '$ErrorActionPreference = "Continue"' in source
    assert "$ErrorActionPreference = $savedErrorActionPreference" in source


def test_installer_does_not_silently_enable_online_acquisition() -> None:
    source = _text(SETUP)

    for task in ("onlinepip", "onlinepython", "onlineollama"):
        assert f"Name: \"{task}\"" in source
        assert "Flags: unchecked" in next(
            line for line in source.splitlines() if f'Name: "{task}"' in line
        )
    assert "WizardIsTaskSelected('onlinepip')" in source
    assert "WizardIsTaskSelected('onlinepython')" in source
    assert "WizardIsTaskSelected('onlineollama')" in source


@pytest.mark.skipif(os.name != "nt", reason="Windows installer execution proof")
def test_denial_makes_zero_process_attempts(tmp_path: Path) -> None:
    powershell = shutil.which("powershell")
    assert powershell
    sentinel = tmp_path / "spawned.txt"
    executable = tmp_path / "fake-acquisition.cmd"
    executable.write_text(f'@echo off\r\necho spawned>"{sentinel}"\r\n', encoding="utf-8")
    evidence = tmp_path / "evidence.jsonl"
    command = (
        f". '{ADMISSION}'; "
        "try { "
        f"Invoke-NovaInstallerAcquisition -Operation 'pip_install_nova' -ExecutablePath '{executable}' "
        f"-InstallDir '{ROOT}' -EvidencePath '{evidence}' -CorrelationId 'denied-test' -ExplicitConsent $false; "
        "exit 91 } catch { exit 0 }"
    )

    completed = subprocess.run([powershell, "-NoProfile", "-Command", command], check=False)

    assert completed.returncode == 0
    assert not sentinel.exists()
    assert not evidence.exists()


@pytest.mark.skipif(os.name != "nt", reason="Windows installer execution proof")
def test_admission_is_durable_before_minimal_environment_delegation(tmp_path: Path) -> None:
    powershell = shutil.which("powershell")
    assert powershell
    evidence = tmp_path / "evidence.jsonl"
    sentinel = tmp_path / "child.txt"
    executable = tmp_path / "fake-acquisition.cmd"
    executable.write_text(
        "@echo off\r\n"
        f'if not exist "{evidence}" exit /b 92\r\n'
        "echo delegated diagnostic output\r\n"
        "echo delegated warning output 1>&2\r\n"
        f'>"{sentinel}" echo proxy=%HTTPS_PROXY%\r\n'
        f'>>"{sentinel}" echo pip_config=%PIP_CONFIG_FILE%\r\n'
        "exit /b 0\r\n",
        encoding="utf-8",
    )
    command = (
        "$ErrorActionPreference = 'Stop'; "
        f". '{ADMISSION}'; "
        f"$code = Invoke-NovaInstallerAcquisition -Operation 'pip_install_nova' -ExecutablePath '{executable}' "
        f"-InstallDir '{ROOT}' -EvidencePath '{evidence}' -CorrelationId 'allow-test' -ExplicitConsent $true; "
        "if ($code -isnot [int]) { exit 93 }; "
        "exit $code"
    )
    child_env = dict(os.environ)
    child_env["HTTPS_PROXY"] = "https://secret-proxy.invalid"

    completed = subprocess.run(
        [powershell, "-NoProfile", "-Command", command], env=child_env, check=False
    )

    assert completed.returncode == 0
    child_text = sentinel.read_text(encoding="utf-8")
    assert "secret-proxy" not in child_text
    assert "pip_config=" in child_text
    records = [json.loads(line) for line in evidence.read_text(encoding="utf-8").splitlines()]
    assert [record["record_kind"] for record in records] == [
        "installer_acquisition_admission",
        "delegated_process_outcome",
    ]
    assert records[1]["exit_code"] == 0
    assert records[1]["installation_verified"] is False

