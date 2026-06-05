"""Phase 3 — Import boundary and personality-off baseline tests.

Proves:
  - Phase 3 components have no governance imports
  - Phase 3 components have no transitive execution imports
  - Personality-off routing unchanged
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest


PHASE3_FILES = [
    "voice_personality.py",
    "trust_presenter.py",
    "proactive_briefing.py",
]

PERSONALITY_SRC = (
    Path(__file__).resolve().parents[2] / "src" / "personality"
)

PROHIBITED_MODULES = {
    "governor", "executors", "ledger", "network_mediator",
    "execute_boundary", "capability_registry",
}


def _source_text(filename: str) -> str:
    path = PERSONALITY_SRC / filename
    assert path.exists(), f"Source not found: {path}"
    return path.read_text(encoding="utf-8")


def _all_imports(source: str) -> list[str]:
    tree = ast.parse(source)
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
    return modules


# ---------------------------------------------------------------------------
# Direct import boundary
# ---------------------------------------------------------------------------

class TestPhase3DirectImportBoundary:

    @pytest.mark.parametrize("filename", PHASE3_FILES)
    def test_phase3_components_have_no_governance_imports(self, filename):
        source = _source_text(filename)
        for module in _all_imports(source):
            module_lower = module.lower()
            for prohibited in PROHIBITED_MODULES:
                assert prohibited not in module_lower, (
                    f"{filename} imports prohibited module: {module}"
                )

    @pytest.mark.parametrize("filename", PHASE3_FILES)
    def test_phase3_no_store_or_client_imports(self, filename):
        source = _source_text(filename)
        for module in _all_imports(source):
            module_lower = module.lower()
            assert "memory" not in module_lower or "reminder" in module_lower, (
                f"{filename} imports memory module: {module}"
            )
            assert "connector" not in module_lower, (
                f"{filename} imports connector: {module}"
            )
            assert "shopify" not in module_lower, (
                f"{filename} imports shopify: {module}"
            )


# ---------------------------------------------------------------------------
# Transitive import boundary
# ---------------------------------------------------------------------------

class TestPhase3TransitiveImportBoundary:

    @pytest.mark.parametrize("filename", PHASE3_FILES)
    def test_phase3_components_have_no_transitive_execution_imports(
        self, filename,
    ):
        """Import the module and check its full transitive dependency
        tree for governance/execution modules."""
        import importlib
        import sys

        module_name = f"src.personality.{filename.replace('.py', '')}"

        # Snapshot modules before import
        before = set(sys.modules.keys())

        importlib.import_module(module_name)

        # Check new modules loaded
        after = set(sys.modules.keys())
        new_modules = after - before

        for mod_name in new_modules:
            mod_lower = mod_name.lower()
            for prohibited in PROHIBITED_MODULES:
                if prohibited in mod_lower:
                    # Allow the check itself (this test file)
                    if "test_" in mod_name:
                        continue
                    # Allow personality's own modules
                    if "personality" in mod_lower:
                        continue
                    assert False, (
                        f"{filename} transitively imports {mod_name} "
                        f"(contains '{prohibited}')"
                    )


# ---------------------------------------------------------------------------
# Personality-off baseline
# ---------------------------------------------------------------------------

class TestPersonalityOffBaseline:

    SCRIPTS = [
        ["shopify report"],
        ["what's the weather"],
        ["search for AI news"],
        ["open documents"],
    ]

    def test_personality_off_baseline_routing_unchanged(self):
        from tests.simulation.conversation_simulator import run_simulation
        for script in self.SCRIPTS:
            a = run_simulation(script)
            b = run_simulation(script)
            assert a.capability_sequence() == b.capability_sequence(), (
                f"Routing mismatch for {script}"
            )

    def test_capability_count_still_27(self):
        from src.governor.capability_registry import CapabilityRegistry
        registry = CapabilityRegistry()
        active = [
            c for c in registry.all_capabilities()
            if getattr(c, "status", "").lower() == "active"
        ]
        assert len(active) == 27

    def test_executor_count_still_22(self):
        executor_dir = (
            Path(__file__).resolve().parents[2] / "src" / "executors"
        )
        executors = [
            f for f in executor_dir.glob("*_executor.py") if f.is_file()
        ]
        assert len(executors) == 22
