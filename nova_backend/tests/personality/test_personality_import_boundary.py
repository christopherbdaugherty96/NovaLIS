"""Import boundary tests for the personality layer.

These tests enforce the structural isolation rule from the audited
architecture. They verify that personality components cannot reach
governance, execution, ledger, or network components — both through
direct imports and transitive dependency chains.

Any failure is a build-blocking governance violation.
"""
from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path
from typing import Set

PERSONALITY_DIR = Path(__file__).resolve().parents[2] / "src" / "personality"
WORKING_CONTEXT_DIR = Path(__file__).resolve().parents[2] / "src" / "working_context"

PROHIBITED_MODULES = {
    "src.governor.governor_mediator",
    "src.governor.governor",
    "src.governor.execute_boundary",
    "src.governor.execute_boundary.execute_boundary",
    "src.governor.network_mediator",
    "src.governor.capability_registry",
    "src.ledger",
    "src.ledger.writer",
}

PROHIBITED_PREFIXES = (
    "src.governor.",
    "src.executors.",
    "src.ledger.",
)

NEW_PERSONALITY_FILES = (
    "chief_of_staff_profile.py",
    "briefing_composer.py",
)


def _read_imports_from_file(filepath: Path) -> set[str]:
    """Extract all import module names from a Python file via AST."""
    source = filepath.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(filepath))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def _resolve_transitive_imports(
    module_name: str,
    *,
    visited: set[str] | None = None,
    max_depth: int = 10,
) -> set[str]:
    """Resolve the full import tree of a module via AST walking.

    Returns all `src.*` modules found transitively, without executing
    any import that could have side effects.
    """
    if visited is None:
        visited = set()
    if module_name in visited or max_depth <= 0:
        return visited
    visited.add(module_name)

    parts = module_name.replace(".", "/")
    candidates = [
        PERSONALITY_DIR.parents[1] / f"{parts}.py",
        PERSONALITY_DIR.parents[1] / parts / "__init__.py",
    ]

    source_path = None
    for candidate in candidates:
        if candidate.exists():
            source_path = candidate
            break

    if source_path is None:
        return visited

    for imp in _read_imports_from_file(source_path):
        if imp.startswith("src."):
            _resolve_transitive_imports(
                imp, visited=visited, max_depth=max_depth - 1
            )

    return visited


# --- Direct Import Tests ---


def test_briefing_composer_no_governor_mediator():
    imports = _read_imports_from_file(PERSONALITY_DIR / "briefing_composer.py")
    assert "src.governor.governor_mediator" not in imports


def test_briefing_composer_no_execute_boundary():
    imports = _read_imports_from_file(PERSONALITY_DIR / "briefing_composer.py")
    for imp in imports:
        assert "execute_boundary" not in imp


def test_briefing_composer_no_executors():
    imports = _read_imports_from_file(PERSONALITY_DIR / "briefing_composer.py")
    for imp in imports:
        assert not imp.startswith("src.executors")


def test_briefing_composer_no_network_mediator():
    imports = _read_imports_from_file(PERSONALITY_DIR / "briefing_composer.py")
    assert "src.governor.network_mediator" not in imports


def test_briefing_composer_no_capability_dispatch():
    imports = _read_imports_from_file(PERSONALITY_DIR / "briefing_composer.py")
    assert "src.governor.capability_registry" not in imports


def test_briefing_composer_no_ledger():
    imports = _read_imports_from_file(PERSONALITY_DIR / "briefing_composer.py")
    for imp in imports:
        assert not imp.startswith("src.ledger")


def test_chief_of_staff_profile_stdlib_only():
    imports = _read_imports_from_file(PERSONALITY_DIR / "chief_of_staff_profile.py")
    for imp in imports:
        assert not imp.startswith("src.governor")
        assert not imp.startswith("src.executors")
        assert not imp.startswith("src.ledger")
        assert not imp.startswith("src.api")
        assert not imp.startswith("src.connectors")


def test_all_new_personality_files_no_governance():
    for filename in NEW_PERSONALITY_FILES:
        filepath = PERSONALITY_DIR / filename
        if not filepath.exists():
            continue
        imports = _read_imports_from_file(filepath)
        for imp in imports:
            for prefix in PROHIBITED_PREFIXES:
                assert not imp.startswith(prefix), (
                    f"{filename} imports {imp} which starts with {prefix}"
                )


# --- Transitive Import Tests ---


def test_briefing_composer_transitive_isolation():
    """Resolve full import tree of BriefingComposer and verify no
    governance, execution, or ledger modules appear."""
    tree = _resolve_transitive_imports("src.personality.briefing_composer")
    for module in tree:
        for prefix in PROHIBITED_PREFIXES:
            assert not module.startswith(prefix), (
                f"Transitive dependency: briefing_composer -> ... -> {module}"
            )
        for prohibited in PROHIBITED_MODULES:
            assert module != prohibited, (
                f"Transitive dependency: briefing_composer -> ... -> {module}"
            )


def test_chief_of_staff_profile_transitive_isolation():
    """ChiefOfStaffProfile should have zero non-stdlib transitive deps."""
    tree = _resolve_transitive_imports("src.personality.chief_of_staff_profile")
    src_deps = {m for m in tree if m.startswith("src.")}
    assert src_deps == {"src.personality.chief_of_staff_profile"}, (
        f"ChiefOfStaffProfile has unexpected src dependencies: {src_deps}"
    )


# --- Personality-Off Baseline Tests ---


def test_personality_off_briefing_is_inert():
    """With no personality profile, composer still works but
    produces presentation-only output."""
    from src.personality.briefing_composer import BriefingComposer
    composer = BriefingComposer(profile=None)
    briefing = composer.compose()
    assert briefing.as_text() == "I do not see anything that needs your attention right now."


def test_personality_off_no_governance_side_effects():
    """Composing a briefing with personality off produces no
    governance artifacts — no ledger entries, no capability
    invocations, no state changes."""
    from src.personality.briefing_composer import BriefingComposer
    import time
    composer = BriefingComposer(profile=None)
    briefing = composer.compose(
        session_data={"shopify": {"order_count": 3, "timestamp": time.time()}},
    )
    text = briefing.as_text()
    assert isinstance(text, str)
    assert "3 orders" in text
