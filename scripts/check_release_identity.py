"""Enforce Nova's release identity across its active release surfaces.

``pyproject.toml`` [project].version is the canonical source. Runtime metadata,
the Windows installer, and current user-facing release references are projections
that must match it. This is declaration validation only: it does not build an
installer, publish a release, or certify any platform.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = Path("pyproject.toml")
RUNTIME_VERSION_SURFACES = (
    Path("nova_backend/src/nova_config.py"),
    Path("nova_backend/src/skills/__init__.py"),
)
INSTALLER = Path("installer/windows/nova_setup.iss")
README = Path("README.md")
INSTALLER_README = Path("installer/README.md")
UNPUBLISHED_INSTALLER_NOTICE = "No `{version}` installer artifact is currently published."
INSTALLER_ARTIFACT_PATTERN = re.compile(r"\bNovaSetup-(?P<version>\d+\.\d+\.\d+)\.exe\b")
ALLOWED_LOCAL_INSTALLER_PATTERN = re.compile(
    r"`dist[\\/]NovaSetup-(?P<version>\d+\.\d+\.\d+)\.exe`"
)


def canonical_version(root: Path = ROOT) -> str:
    source = (root / PYPROJECT).read_text(encoding="utf-8")
    project = re.search(r"^\[project\]$(.*?)(?=^\[|\Z)", source, re.MULTILINE | re.DOTALL)
    if project is None:
        raise ValueError("[project] section not found in pyproject.toml")
    match = re.search(r'^version\s*=\s*"(?P<version>[^"]+)"\s*$', project.group(1), re.MULTILINE)
    if match is None:
        raise ValueError("[project].version not found in pyproject.toml")
    return match.group("version")


def _single_match(source: str, pattern: str, *, label: str) -> str:
    matches = re.findall(pattern, source, re.MULTILINE)
    if len(matches) != 1:
        raise ValueError(f"{label} must appear exactly once")
    return matches[0]


def _all_matches(source: str, pattern: str, *, label: str) -> tuple[str, ...]:
    matches = tuple(re.findall(pattern, source, re.MULTILINE))
    if not matches:
        raise ValueError(f"{label} must appear at least once")
    return matches


def check_release_identity(root: Path = ROOT) -> list[str]:
    try:
        version = canonical_version(root)
    except (OSError, ValueError) as exc:
        return [str(exc)]

    errors: list[str] = []
    for path in RUNTIME_VERSION_SURFACES:
        try:
            actual = _single_match(
                (root / path).read_text(encoding="utf-8"),
                r'^__version__\s*=\s*"(?P<version>[^"]+)"\s*$',
                label=path.as_posix() + " __version__",
            )
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue
        if actual != version:
            errors.append(
                f"{path.as_posix()} version {actual!r} must match pyproject.toml {version!r}"
            )

    try:
        installer = (root / INSTALLER).read_text(encoding="utf-8")
        app_version = _single_match(
            installer, r"^AppVersion=(?P<version>[^\r\n]+)$", label="installer AppVersion"
        )
        artifact_version = _single_match(
            installer,
            r"^OutputBaseFilename=NovaSetup-(?P<version>[^\r\n]+)$",
            label="installer OutputBaseFilename",
        )
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    else:
        for label, actual in (
            ("installer AppVersion", app_version),
            ("installer artifact", artifact_version),
        ):
            if actual != version:
                errors.append(f"{label} {actual!r} must match pyproject.toml {version!r}")

    try:
        readme = (root / README).read_text(encoding="utf-8")
        release_banner = _single_match(
            readme,
            r"^\*\*(?P<label>Version\s+[^\r\n]+)\*\*$",
            label="README release banner",
        )
        status_declaration = _single_match(
            readme,
            r"^(?P<declaration>Version\s+\d+(?:\.\d+)+\s+[A-Za-z][A-Za-z0-9/+.-]*)\s+is\b",
            label="README current status release declaration",
        )
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    else:
        major_minor = ".".join(version.split(".")[:2])
        expected_banner = f"Version {major_minor} Alpha — Current State"
        expected_status = f"Version {major_minor} Alpha"
        if release_banner != expected_banner:
            errors.append(
                f"README.md release banner {release_banner!r} must match {expected_banner!r}"
            )
        if status_declaration != expected_status:
            errors.append(
                f"README.md current status release declaration {status_declaration!r} "
                f"must match {expected_status!r}"
            )

    try:
        installer_readme = (root / INSTALLER_README).read_text(encoding="utf-8")
        installer_artifacts = tuple(INSTALLER_ARTIFACT_PATTERN.finditer(installer_readme))
        if not installer_artifacts:
            raise ValueError("installer README artifact version must appear at least once")
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
    else:
        allowed_local_installers = tuple(ALLOWED_LOCAL_INSTALLER_PATTERN.finditer(installer_readme))
        for artifact in installer_artifacts:
            actual = artifact.group("version")
            if actual != version:
                errors.append(
                    f"installer README artifact version {actual!r} must match "
                    f"pyproject.toml {version!r}"
                )
            if not any(
                allowed.start() <= artifact.start() and artifact.end() <= allowed.end()
                for allowed in allowed_local_installers
            ):
                errors.append(
                    "installer/README.md must not advertise an unpublished installer "
                    "download; artifacts must be explicit local dist build-output references"
                )
        notice = UNPUBLISHED_INSTALLER_NOTICE.format(version=version)
        if notice not in installer_readme:
            errors.append(
                f"installer/README.md must state {notice!r} until a candidate is published"
            )

    return errors


def main() -> int:
    errors = check_release_identity()
    if errors:
        print("Release identity check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Release identity check passed.")
    print(f"Canonical source: {PYPROJECT} [project].version = {canonical_version()}")
    print(
        "Validated projections: runtime metadata, Windows installer, active README versions, installer README"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
