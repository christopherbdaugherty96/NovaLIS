from __future__ import annotations

from tests.adversarial._helpers import SRC_ROOT, ast_imports


FORBIDDEN_PREFIXES = {
    "src.archive",
    "src.archive_quarantine",
    "src.archive_phase4",
}


def test_runtime_modules_do_not_import_archive_or_quarantine():
    offenders: list[tuple[str, list[str]]] = []

    for py in SRC_ROOT.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        imports = ast_imports(py)
        bad = [imp for imp in imports if any(imp == pref or imp.startswith(pref + ".") for pref in FORBIDDEN_PREFIXES)]
        if bad:
            offenders.append((str(py), sorted(set(bad))))

    assert not offenders, "Archive/quarantine imports detected in runtime surface:\n" + "\n".join(
        f"- {path}: {mods}" for path, mods in offenders
    )
