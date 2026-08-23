from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_checker():
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "check_dependency_consistency.py"
    spec = importlib.util.spec_from_file_location("dependency_consistency_checker", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write_fixture(
    root: Path,
    *,
    canonical: list[str],
    requirements: list[str],
    optional: list[str] | None = None,
) -> None:
    checker = _load_checker()
    (root / "nova_backend/src").mkdir(parents=True)
    rendered_dependencies = "".join(f'    "{item}",\n' for item in canonical)
    (root / "pyproject.toml").write_text(
        f"[project]\nname = \"fixture\"\ndependencies = [\n{rendered_dependencies}]\n",
        encoding="utf-8",
    )
    (root / "nova_backend/requirements.txt").write_text(
        checker.REQUIREMENTS_HEADER + "".join(f"{item}\n" for item in requirements),
        encoding="utf-8",
    )
    optional_entries = optional or ["openwakeword==0.6.0"]
    (root / "nova_backend/requirements-optional-wakeword.txt").write_text(
        "-r requirements.txt\n"
        + "".join(f"{item}\n" for item in optional_entries),
        encoding="utf-8",
    )
    (root / "nova_backend/src/requirements.txt").write_text(
        "-r ../requirements.txt\n", encoding="utf-8"
    )
    (root / "nova_backend/src/requirements-optional-wakeword.txt").write_text(
        "-r ../requirements-optional-wakeword.txt\n", encoding="utf-8"
    )


def test_repository_dependency_surfaces_are_consistent():
    checker = _load_checker()

    assert checker.check_dependency_consistency() == []

    audit = checker.audit_dependency_sources()
    assert len(audit.exact_duplicates) == 13
    assert audit.conflicts == {}
    assert audit.canonical_only == {}
    assert audit.requirements_only == {}
    assert audit.optional_only == {"openwakeword": "openwakeword==0.6.0"}


def test_checker_reports_conflicting_pin(tmp_path):
    checker = _load_checker()
    _write_fixture(
        tmp_path,
        canonical=["python-multipart==0.0.21"],
        requirements=["python-multipart==0.0.29"],
    )

    errors = checker.check_dependency_consistency(tmp_path)

    assert any("dependency conflict for python-multipart" in error for error in errors)
    assert any("not the exact compatibility projection" in error for error in errors)


def test_checker_reports_one_sided_runtime_declarations(tmp_path):
    checker = _load_checker()
    _write_fixture(
        tmp_path,
        canonical=["fastapi==1.0", "httpx==1.0"],
        requirements=["fastapi==1.0", "aiofiles==1.0"],
    )

    errors = checker.check_dependency_consistency(tmp_path)

    assert any("canonical dependency missing" in error and "httpx" in error for error in errors)
    assert any(
        "compatibility requirement missing" in error and "aiofiles" in error
        for error in errors
    )


def test_checker_rejects_optional_overlap_with_canonical_runtime(tmp_path):
    checker = _load_checker()
    _write_fixture(
        tmp_path,
        canonical=["fastapi==1.0"],
        requirements=["fastapi==1.0"],
        optional=["fastapi==1.0"],
    )

    errors = checker.check_dependency_consistency(tmp_path)

    assert any("optional wake-word requirements duplicate" in error for error in errors)
