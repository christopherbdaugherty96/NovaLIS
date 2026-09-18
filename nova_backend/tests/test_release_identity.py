from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_checker():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "check_release_identity.py"
    spec = importlib.util.spec_from_file_location("release_identity_checker", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _copy_release_surfaces(checker, root: Path) -> None:
    for relative in (
        "pyproject.toml",
        "nova_backend/src/nova_config.py",
        "nova_backend/src/skills/__init__.py",
        "installer/windows/nova_setup.iss",
        "README.md",
        "installer/README.md",
    ):
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            (checker.ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8"
        )


def test_repository_release_identity_is_consistent():
    checker = _load_checker()

    assert checker.canonical_version() == "0.5.0"
    assert checker.check_release_identity() == []


def test_release_identity_rejects_runtime_version_drift(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    config = tmp_path / "nova_backend/src/nova_config.py"
    config.write_text(
        config.read_text(encoding="utf-8").replace(
            '__version__ = "0.5.0"', '__version__ = "9.9.9"'
        ),
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("nova_backend/src/nova_config.py version '9.9.9'" in error for error in errors)


def test_release_identity_rejects_installer_artifact_drift(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    installer = tmp_path / "installer/windows/nova_setup.iss"
    installer.write_text(
        installer.read_text(encoding="utf-8").replace("NovaSetup-0.5.0", "NovaSetup-9.9.9"),
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("installer artifact '9.9.9'" in error for error in errors)


def test_release_identity_rejects_conflicting_active_readme_version(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace(
            "Version 0.5 Alpha — Current State", "Version 9.9 Alpha — Current State", 1
        ),
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("README.md release version '9.9'" in error for error in errors)


def test_release_identity_rejects_unrecognized_active_readme_label(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace(
            "Version 0.5 Alpha — Current State", "Version 9.9 Beta — Current State", 1
        ),
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any(
        "README.md release banner 'Version 9.9 Beta — Current State'" in error for error in errors
    )


def test_release_identity_rejects_full_semver_readme_version_drift(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace(
            "Version 0.5 Alpha is", "Version 9.9.9 Alpha is", 1
        ),
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("README.md release version '9.9.9'" in error for error in errors)


def test_release_identity_rejects_conflicting_installer_readme_artifact(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    installer_readme = tmp_path / "installer/README.md"
    installer_readme.write_text(
        installer_readme.read_text(encoding="utf-8").replace(
            "NovaSetup-0.5.0.exe", "NovaSetup-9.9.9.exe", 1
        ),
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("installer README artifact version '9.9.9'" in error for error in errors)


def test_release_identity_rejects_unpublished_installer_advertising(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    installer_readme = tmp_path / "installer/README.md"
    installer_readme.write_text(
        installer_readme.read_text(encoding="utf-8")
        + "\nDownload `NovaSetup-0.5.0.exe` from GitHub Releases.\n",
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("must not advertise an unpublished installer download" in error for error in errors)


def test_release_identity_rejects_unpublished_markdown_installer_download(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    installer_readme = tmp_path / "installer/README.md"
    installer_readme.write_text(
        installer_readme.read_text(encoding="utf-8")
        + "\n[Download `NovaSetup-0.5.0.exe`](https://example.invalid/releases)\n",
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("must not advertise an unpublished installer download" in error for error in errors)


def test_release_identity_rejects_descriptive_markdown_installer_link(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    installer_readme = tmp_path / "installer/README.md"
    installer_readme.write_text(
        installer_readme.read_text(encoding="utf-8")
        + "\n[Get Nova for Windows](https://example.invalid/NovaSetup-0.5.0.exe)\n",
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("must not advertise an unpublished installer download" in error for error in errors)
