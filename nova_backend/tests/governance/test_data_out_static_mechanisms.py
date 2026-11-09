from __future__ import annotations

from pathlib import Path

from src.audit.data_out_static_mechanisms import (
    ClosureFamily,
    DispositionRegistry,
    MechanismDisposition,
    MechanismStatus,
    scan_python_file,
    scan_text_file,
    validate_repository_dispositions,
)


def test_alias_call_is_detected_at_exact_site(tmp_path: Path) -> None:
    source = tmp_path / "worker.py"
    source.write_text(
        "from subprocess import Popen as launch\nlaunch(['tool'])\n",
        encoding="utf-8",
    )

    findings = scan_python_file(source, repository_root=tmp_path)

    assert [(finding.symbol, finding.line, finding.column) for finding in findings] == [
        ("subprocess.Popen", 2, 0)
    ]


def test_registration_is_per_call_site_not_per_module(tmp_path: Path) -> None:
    source = tmp_path / "worker.py"
    source.write_text(
        "import subprocess\n"
        "subprocess.run(['first'])\n"
        "subprocess.run(['second'])\n",
        encoding="utf-8",
    )
    findings = scan_python_file(source, repository_root=tmp_path)
    registry = DispositionRegistry(
        dispositions=(
            MechanismDisposition(
                site=findings[0].site,
                mechanism=findings[0].mechanism,
                symbol=findings[0].symbol,
                status=MechanismStatus.UNRESOLVED,
                closure_family=ClosureFamily.NON_OLLAMA_DELEGATION,
                reason="Known first delegated-process call.",
            ),
        )
    )

    report = registry.compare(findings)

    assert report.registered == (findings[0],)
    assert report.unregistered == (findings[1],)


def test_removed_exact_site_becomes_stale(tmp_path: Path) -> None:
    source = tmp_path / "worker.py"
    source.write_text("import subprocess\nsubprocess.run(['first'])\n", encoding="utf-8")
    finding = scan_python_file(source, repository_root=tmp_path)[0]
    registry = DispositionRegistry(
        dispositions=(
            MechanismDisposition(
                site=finding.site,
                mechanism=finding.mechanism,
                symbol=finding.symbol,
                status=MechanismStatus.UNRESOLVED,
                closure_family=ClosureFamily.NON_OLLAMA_DELEGATION,
                reason="Known delegated-process call.",
            ),
        )
    )

    report = registry.compare(())

    assert report.stale == registry.dispositions


def test_powershell_help_text_is_not_detected_as_an_operation(tmp_path: Path) -> None:
    source = tmp_path / "setup.ps1"
    source.write_text(
        "<#\nOffers winget install and pip install help.\n#>\n"
        "winget install Example.Package\n",
        encoding="utf-8",
    )

    findings = scan_text_file(source, repository_root=tmp_path)

    assert [(item.symbol, item.line) for item in findings] == [("winget install", 4)]


def test_repository_registry_has_no_unregistered_supported_mechanisms() -> None:
    report = validate_repository_dispositions()

    assert report.unregistered == ()
    assert report.stale == ()


def test_registry_preserves_all_ten_non_static_closure_families() -> None:
    report = validate_repository_dispositions()
    unresolved_families = {
        disposition.family
        for disposition in report.families
        if disposition.status is MechanismStatus.UNRESOLVED
    }

    assert unresolved_families == {
        ClosureFamily.EXTERNAL_READ_AND_SETUP,
        ClosureFamily.OPENCLAW_PROVIDER_ROUTES,
        ClosureFamily.INSTALLER_ACQUISITION,
        ClosureFamily.NON_OLLAMA_DELEGATION,
        ClosureFamily.TRUSTED_RUNTIME_ROOTS,
        ClosureFamily.INSTALLATION_STATE_ROOTS,
        ClosureFamily.USER_AND_TEMP_PATHS,
        ClosureFamily.EXECUTABLE_DISCOVERY_ROOTS,
        ClosureFamily.SETUP_SHELL_FOLDERS,
        ClosureFamily.STORAGE_DIAGNOSTICS_ROOTS,
    }


def test_registry_has_no_path_wildcard_exemptions() -> None:
    report = validate_repository_dispositions()

    for disposition in report.dispositions:
        assert "*" not in disposition.site.path
        assert disposition.site.line > 0
        assert disposition.site.column >= 0
