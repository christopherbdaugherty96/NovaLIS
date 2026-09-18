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

    assert any(
        "README.md release banner 'Version 9.9 Alpha — Current State'" in error for error in errors
    )


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


def test_release_identity_rejects_non_banner_readme_release_label_drift(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace(
            "Version 0.5 Alpha is", "Version 0.5 Beta is", 1
        ),
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any(
        "README.md current status release declaration 'Version 0.5 Beta'" in error
        for error in errors
    )


def test_release_identity_rejects_readme_release_label_suffixes(tmp_path):
    checker = _load_checker()
    for malformed_label in ("Alpha/Beta", "Alpha2"):
        root = tmp_path / malformed_label.replace("/", "_")
        _copy_release_surfaces(checker, root)
        readme = root / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8").replace(
                "Version 0.5 Alpha is", f"Version 0.5 {malformed_label} is", 1
            ),
            encoding="utf-8",
        )

        errors = checker.check_release_identity(root)

        assert any(
            f"README.md current status release declaration 'Version 0.5 {malformed_label}'" in error
            for error in errors
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

    assert any(
        "README.md current status release declaration 'Version 9.9.9 Alpha'" in error
        for error in errors
    )


def test_release_identity_scopes_readme_status_to_current_status_section(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    readme = tmp_path / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").replace(
            "Version 0.5 Alpha is a technical-user / early-adopter state, not a finished mainstream release.",
            "The current status declaration is intentionally absent.",
            1,
        )
        + "\nVersion 0.5 Alpha is a decoy outside Current Status.\n",
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any(
        "README current status release declaration must appear exactly once" in error
        for error in errors
    )


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

    assert any("installer README artifact name '9.9.9'" in error for error in errors)


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


def test_release_identity_rejects_reference_style_installer_link(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    installer_readme = tmp_path / "installer/README.md"
    installer_readme.write_text(
        installer_readme.read_text(encoding="utf-8")
        + "\n[Get Nova for Windows][installer]\n\n[installer]: https://example.invalid/NovaSetup-0.5.0.exe\n",
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("must not advertise an unpublished installer download" in error for error in errors)


def test_release_identity_rejects_html_installer_link(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    installer_readme = tmp_path / "installer/README.md"
    installer_readme.write_text(
        installer_readme.read_text(encoding="utf-8")
        + '\n<a class="download" href="https://example.invalid/NovaSetup-0.5.0.exe">Get Nova</a>\n',
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("must not advertise an unpublished installer download" in error for error in errors)


def test_release_identity_rejects_bare_and_autolink_installer_urls(tmp_path):
    checker = _load_checker()
    for installer_url in (
        "https://example.invalid/NovaSetup-0.5.0.exe",
        "<https://example.invalid/NovaSetup-0.5.0.exe>",
    ):
        root = tmp_path / ("autolink" if installer_url.startswith("<") else "bare")
        _copy_release_surfaces(checker, root)
        installer_readme = root / "installer/README.md"
        installer_readme.write_text(
            installer_readme.read_text(encoding="utf-8") + f"\n{installer_url}\n",
            encoding="utf-8",
        )

        errors = checker.check_release_identity(root)

        assert any(
            "must not advertise an unpublished installer download" in error for error in errors
        )


def test_release_identity_rejects_nonsemver_installer_artifact_names(tmp_path):
    checker = _load_checker()
    for artifact_name in ("0.5.0-beta", "latest"):
        root = tmp_path / artifact_name
        _copy_release_surfaces(checker, root)
        installer_readme = root / "installer/README.md"
        installer_readme.write_text(
            installer_readme.read_text(encoding="utf-8")
            + f"\nDownload `NovaSetup-{artifact_name}.exe` from GitHub Releases.\n",
            encoding="utf-8",
        )

        errors = checker.check_release_identity(root)

        assert any(f"installer README artifact name {artifact_name!r}" in error for error in errors)
        assert any(
            "must not advertise an unpublished installer download" in error for error in errors
        )


def test_release_identity_rejects_unsupported_beta_boundary_claims(tmp_path):
    checker = _load_checker()
    support_claim_mutations = (
        (
            "README.md",
            "they are not certified or supported beta",
            "they are certified and supported beta",
            "README Windows beta-support boundary",
        ),
        (
            "installer/README.md",
            "clean-machine certification remains a later acceptance gate.",
            "clean-machine certification is complete.",
            "installer README Windows beta-support boundary",
        ),
        (
            "installer/README.md",
            "macOS and Linux do not have supported beta installer paths.",
            "macOS and Linux have supported beta installer paths.",
            "installer README other-platforms beta-support boundary",
        ),
    )
    for relative, expected, replacement, error_fragment in support_claim_mutations:
        root = tmp_path / error_fragment.replace(" ", "_")
        _copy_release_surfaces(checker, root)
        surface = root / relative
        surface.write_text(
            surface.read_text(encoding="utf-8").replace(expected, replacement, 1),
            encoding="utf-8",
        )

        errors = checker.check_release_identity(root)

        assert any(error_fragment in error for error in errors)


def test_release_identity_ignores_hidden_support_boundary_text(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    readme = tmp_path / "README.md"
    approved = (
        "Windows is Nova's primary beta-support target. The Windows installer path exists, but\n"
        "clean-machine certification is still a later acceptance gate. macOS and Linux may be\n"
        "used for source-based development only; they are not certified or supported beta\n"
        "platforms."
    )
    visible_false = (
        "Windows is Nova's primary beta-support target. The Windows installer path exists, but\n"
        "clean-machine certification is complete. macOS and Linux are supported beta\n"
        "platforms."
    )
    readme.write_text(
        readme.read_text(encoding="utf-8").replace(
            approved, f"<!--\n{approved}\n-->\n{visible_false}", 1
        ),
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("README Windows beta-support boundary" in error for error in errors)


def test_release_identity_rejects_installer_artifact_outside_build_lines(tmp_path):
    checker = _load_checker()
    _copy_release_surfaces(checker, tmp_path)
    installer_readme = tmp_path / "installer/README.md"
    installer_readme.write_text(
        installer_readme.read_text(encoding="utf-8")
        + "\nDownload `dist/NovaSetup-0.5.0.exe` from the source checkout.\n",
        encoding="utf-8",
    )

    errors = checker.check_release_identity(tmp_path)

    assert any("must not advertise an unpublished installer download" in error for error in errors)
