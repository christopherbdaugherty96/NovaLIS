"""Verify Nova's compatibility requirements against canonical project metadata.

``pyproject.toml`` is the authoritative runtime dependency definition. The
requirements files remain compatibility surfaces for existing tooling, so this
checker prevents their independently maintained pins from drifting away from
the canonical project dependency set.

This checker intentionally does not resolve packages from an index, update
dependencies, or validate optional-provider environments. It checks only the
repository declarations and compatibility relationships named below.
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = Path("pyproject.toml")
RUNTIME_REQUIREMENTS = Path("nova_backend/requirements.txt")
OPTIONAL_WAKEWORD_REQUIREMENTS = Path(
    "nova_backend/requirements-optional-wakeword.txt"
)
RUNTIME_REQUIREMENTS_SHIM = Path("nova_backend/src/requirements.txt")
OPTIONAL_WAKEWORD_SHIM = Path(
    "nova_backend/src/requirements-optional-wakeword.txt"
)

REQUIREMENTS_HEADER = (
    "# Compatibility projection of `pyproject.toml` [project].dependencies.\n"
    "# Do not edit dependency pins here independently.\n"
    "# Verify with: python scripts/check_dependency_consistency.py\n"
)

_NAME_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)")


@dataclass(frozen=True)
class DependencyAudit:
    exact_duplicates: dict[str, str]
    conflicts: dict[str, tuple[str, str]]
    canonical_only: dict[str, str]
    requirements_only: dict[str, str]
    optional_only: dict[str, str]


def _read_project_dependencies(path: Path) -> list[str]:
    """Read the simple string array used by ``[project].dependencies``.

    Nova supports Python 3.10, where ``tomllib`` is unavailable. Keeping this
    reader deliberately narrow avoids adding a parser dependency merely to
    verify the repository's existing multiline string-array shape.
    """

    lines = path.read_text(encoding="utf-8").splitlines()
    in_project = False
    collecting = False
    array_lines: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project = stripped == "[project]"
            if collecting:
                raise ValueError("unterminated [project].dependencies array")
            continue
        if not in_project:
            continue
        if not collecting:
            match = re.match(r"dependencies\s*=\s*(\[.*)$", stripped)
            if not match:
                continue
            collecting = True
            array_lines.append(match.group(1))
            if stripped.endswith("]"):
                break
            continue

        array_lines.append(line)
        if stripped == "]":
            break

    if not array_lines or array_lines[-1].strip() != "]":
        raise ValueError("[project].dependencies string array not found")

    parsed = ast.literal_eval("\n".join(array_lines))
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError("[project].dependencies must be a string array")
    return parsed


def _requirement_entries(path: Path) -> tuple[list[str], list[str]]:
    includes: list[str] = []
    entries: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r "):
            includes.append(line[3:].strip())
            continue
        entries.append(line)
    return includes, entries


def _dependency_name(declaration: str) -> str:
    match = _NAME_RE.match(declaration)
    if not match:
        raise ValueError(f"unsupported dependency declaration: {declaration!r}")
    return re.sub(r"[-_.]+", "-", match.group(1)).lower()


def _index(entries: list[str], *, label: str) -> dict[str, str]:
    indexed: dict[str, str] = {}
    for entry in entries:
        name = _dependency_name(entry)
        if name in indexed:
            raise ValueError(f"duplicate {label} declaration for {name}")
        indexed[name] = entry
    return indexed


def render_runtime_requirements(dependencies: list[str]) -> str:
    return REQUIREMENTS_HEADER + "".join(f"{item}\n" for item in dependencies)


def audit_dependency_sources(root: Path = ROOT) -> DependencyAudit:
    canonical_entries = _read_project_dependencies(root / PYPROJECT)
    _, requirements_entries = _requirement_entries(root / RUNTIME_REQUIREMENTS)
    optional_includes, optional_entries = _requirement_entries(
        root / OPTIONAL_WAKEWORD_REQUIREMENTS
    )

    if optional_includes != ["requirements.txt"]:
        raise ValueError(
            "optional wake-word requirements must include requirements.txt exactly once"
        )

    canonical = _index(canonical_entries, label="canonical")
    requirements = _index(requirements_entries, label="requirements")
    optional = _index(optional_entries, label="optional")

    shared = canonical.keys() & requirements.keys()
    exact_duplicates = {
        name: canonical[name]
        for name in sorted(shared)
        if canonical[name] == requirements[name]
    }
    conflicts = {
        name: (canonical[name], requirements[name])
        for name in sorted(shared)
        if canonical[name] != requirements[name]
    }
    canonical_only = {
        name: canonical[name] for name in sorted(canonical.keys() - requirements.keys())
    }
    requirements_only = {
        name: requirements[name]
        for name in sorted(requirements.keys() - canonical.keys())
    }
    optional_only = {name: optional[name] for name in sorted(optional)}
    return DependencyAudit(
        exact_duplicates=exact_duplicates,
        conflicts=conflicts,
        canonical_only=canonical_only,
        requirements_only=requirements_only,
        optional_only=optional_only,
    )


def check_dependency_consistency(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        canonical_entries = _read_project_dependencies(root / PYPROJECT)
        audit = audit_dependency_sources(root)
    except (OSError, SyntaxError, ValueError) as exc:
        return [str(exc)]

    requirements_path = root / RUNTIME_REQUIREMENTS
    expected = render_runtime_requirements(canonical_entries)
    if requirements_path.read_text(encoding="utf-8") != expected:
        errors.append(
            "nova_backend/requirements.txt is not the exact compatibility "
            "projection of pyproject.toml [project].dependencies"
        )

    for name, (canonical, requirements) in audit.conflicts.items():
        errors.append(
            f"dependency conflict for {name}: pyproject={canonical!r}, "
            f"requirements={requirements!r}"
        )
    for name, declaration in audit.canonical_only.items():
        errors.append(
            f"canonical dependency missing from compatibility requirements: "
            f"{name} ({declaration})"
        )
    for name, declaration in audit.requirements_only.items():
        errors.append(
            f"compatibility requirement missing from canonical dependencies: "
            f"{name} ({declaration})"
        )

    optional_overlap = set(audit.optional_only) & {
        _dependency_name(item) for item in canonical_entries
    }
    for name in sorted(optional_overlap):
        errors.append(
            f"optional wake-word requirements duplicate canonical dependency: {name}"
        )

    expected_shims = {
        RUNTIME_REQUIREMENTS_SHIM: "-r ../requirements.txt",
        OPTIONAL_WAKEWORD_SHIM: "-r ../requirements-optional-wakeword.txt",
    }
    for path, expected_include in expected_shims.items():
        includes, entries = _requirement_entries(root / path)
        if includes != [expected_include[3:]] or entries:
            errors.append(
                f"{path.as_posix()} must remain a compatibility shim containing "
                f"only {expected_include!r}"
            )

    return errors


def main() -> int:
    errors = check_dependency_consistency()
    if errors:
        print("Dependency consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    audit = audit_dependency_sources()
    print("Dependency consistency check passed.")
    print(f"Canonical source: {PYPROJECT} [project].dependencies")
    print(f"Compatibility projection: {RUNTIME_REQUIREMENTS}")
    print(f"Exact duplicate declarations: {len(audit.exact_duplicates)}")
    print(f"Conflicts: {len(audit.conflicts)}")
    print(f"Canonical-only declarations: {len(audit.canonical_only)}")
    print(f"Requirements-only declarations: {len(audit.requirements_only)}")
    print("Optional-only declarations:")
    for name, declaration in audit.optional_only.items():
        print(f"- {name}: {declaration}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
