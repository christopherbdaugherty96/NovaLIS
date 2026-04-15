"""Contract tests for the Obsidian overlay generator."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "generate_obsidian_overlay.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("_obsidian_overlay", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["_obsidian_overlay"] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def overlay(tmp_path, monkeypatch):
    module = _load_module()
    repo = tmp_path / "repo"
    docs = repo / "docs"
    automations = repo / "automations"
    github = repo / ".github" / "workflows"
    gov_repo = repo / "NovaLIS-Governance"
    verification = repo / "verification"
    (docs / "design" / "Phase 4.5").mkdir(parents=True)
    (docs / "design" / "Phase-9").mkdir(parents=True)
    (docs / "PROOFS").mkdir(parents=True)
    (docs / "GOVERNANCE").mkdir(parents=True)
    (docs / "current_runtime").mkdir(parents=True)
    (docs / "archive" / "phase 2").mkdir(parents=True)
    (repo / "scripts").mkdir(parents=True)
    (repo / "nova_backend" / "src" / "governor").mkdir(parents=True)
    (repo / "nova_backend" / "src" / "agents").mkdir(parents=True)
    (repo / "nova_backend" / "static").mkdir(parents=True)
    automations.mkdir(parents=True)
    github.mkdir(parents=True)
    gov_repo.mkdir(parents=True)
    verification.mkdir(parents=True)

    (docs / "design" / "Phase 4.5" / "note_a.md").write_text(
        "# UX Friction Roadmap\n\nThis plan reduces friction in the product surface.\n",
        encoding="utf-8",
    )
    (docs / "design" / "Phase-9" / "note_b.md").write_text(
        "# Intelligence Layer Spec\n\nDefines OpenClaw intelligence boundaries.\n",
        encoding="utf-8",
    )
    (docs / "PROOFS" / "proof_one.md").write_text(
        "# Governor Bypass Proof\n\nProof of enforcement.\n",
        encoding="utf-8",
    )
    (docs / "GOVERNANCE" / "rule.md").write_text(
        "# Governance Rule\n\nAuthoritative rule document.\n",
        encoding="utf-8",
    )
    (docs / "current_runtime" / "RUNTIME.md").write_text(
        "# Runtime\n\nCurrent runtime snapshot.\n",
        encoding="utf-8",
    )
    (docs / "archive" / "phase 2" / "old.md").write_text(
        "# Old Note\n\nArchived content.\n",
        encoding="utf-8",
    )
    (docs / "design" / "Phase 4.5" / "README.md").write_text(
        "# Overview\n\nPhase 4.5 overview.\n",
        encoding="utf-8",
    )
    (docs / "design" / "Phase-9" / "README.md").write_text(
        "# Overview\n\nPhase 9 overview.\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "helper.py").write_text(
        '"""Helper utility for generated overlays."""\n',
        encoding="utf-8",
    )
    (github / "runtime-docs.yml").write_text("name: runtime docs\n", encoding="utf-8")
    (automations / "README.md").write_text(
        "# Weekly automation\n\nTracked automation guidance.\n",
        encoding="utf-8",
    )
    (gov_repo / "README.md").write_text(
        "# Governance Repo\n\nGovernance companion docs.\n",
        encoding="utf-8",
    )
    (verification / "governor_proof.py").write_text(
        '"""Verification helper."""\n',
        encoding="utf-8",
    )
    (repo / "README.md").write_text(
        "# Nova Root\n\nTop-level project introduction.\n",
        encoding="utf-8",
    )
    (repo / "nova_backend" / "src" / "governor" / "policy.py").write_text(
        '"""Governor policy helpers."""\n',
        encoding="utf-8",
    )
    (repo / "nova_backend" / "src" / "agents" / "_llm_agent.py").write_text(
        "from __future__ import annotations\n\nclass LLMBackedAgent:\n    pass\n",
        encoding="utf-8",
    )
    (repo / "nova_backend" / "static" / "dashboard.js").write_text(
        '/* Dashboard behavior */\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(module, "REPO_ROOT", repo)
    monkeypatch.setattr(module, "DOCS_ROOT", docs)
    monkeypatch.setattr(module, "AUTOMATIONS_ROOT", automations)
    monkeypatch.setattr(module, "VAULT_CONFIG_DIR", repo / ".obsidian")
    monkeypatch.setattr(module, "MOC_DIR", repo / "_MOCs")
    monkeypatch.setattr(
        module,
        "_tracked_repo_paths",
        lambda: [
            path
            for path in repo.rglob("*")
            if path.is_file() and ".obsidian" not in path.parts and "_MOCs" not in path.parts
        ],
    )
    return module, repo, docs


def test_generator_indexes_docs_and_code_with_path_categories(overlay):
    module, _repo, _docs = overlay
    notes = module.scan_notes()
    by_rel = {note.rel.as_posix(): note for note in notes}

    assert "docs/PROOFS/proof_one.md" in by_rel
    assert by_rel["docs/PROOFS/proof_one.md"].category == "proofs"
    assert by_rel["docs/GOVERNANCE/rule.md"].category == "governance"
    assert by_rel["docs/current_runtime/RUNTIME.md"].category == "runtime"
    assert by_rel["docs/archive/phase 2/old.md"].category == "archive"
    assert by_rel["docs/design/Phase 4.5/note_a.md"].category == "phase"
    assert by_rel["nova_backend/src/governor/policy.py"].category == "governance"
    assert by_rel["nova_backend/src/agents/_llm_agent.py"].category == "runtime"
    assert by_rel["nova_backend/static/dashboard.js"].category == "frontend"
    assert by_rel["automations/README.md"].category == "scripts"
    assert by_rel["README.md"].category == "reference"
    assert by_rel[".github/workflows/runtime-docs.yml"].category == "scripts"
    assert by_rel["NovaLIS-Governance/README.md"].category == "governance"
    assert by_rel["verification/governor_proof.py"].category == "tests"


def test_phase_detection_normalizes_hyphen_and_space_variants(overlay):
    module, _repo, _docs = overlay
    phases = {note.phase for note in module.scan_notes() if note.phase}

    assert "Phase 9" in phases
    assert "Phase-9" not in phases
    assert "Phase 4.5" in phases


def test_duplicate_titles_are_disambiguated(overlay):
    module, _repo, _docs = overlay
    overviews = [note for note in module.scan_notes() if note.title.startswith("Overview")]

    assert len(overviews) == 2
    assert overviews[0].title != overviews[1].title
    assert all(" - " in note.title for note in overviews)


def test_main_writes_all_overlay_outputs(overlay):
    module, repo, _docs = overlay

    assert module.main() == 0

    for moc in (
        "HOME.md",
        "USER_PATHS.md",
        "REPO_BY_FOLDER.md",
        "BY_PHASE.md",
        "BY_TOPIC.md",
        "BY_TYPE.md",
        "CODE_BY_LAYER.md",
        "CODE_MODULES.md",
        "CODE_IMPORTS.md",
        "TEST_MAP.md",
        "RECENT.md",
    ):
        body = (repo / "_MOCs" / moc).read_text(encoding="utf-8")
        assert body.startswith("---\n")
        assert module.GENERATED_MARKER in body

    for config_name in ("graph.json", "starred.json", "app.json", "appearance.json", "core-plugins.json"):
        assert (repo / ".obsidian" / config_name).exists()


def test_test_map_always_written_even_when_no_pairs(overlay):
    """HOME and USER_PATHS link unconditionally to TEST_MAP — the file must exist
    so the wikilink resolves even when a trimmed vault produces zero pairs."""
    module, repo, _docs = overlay
    module.main()

    test_map = (repo / "_MOCs" / "TEST_MAP.md").read_text(encoding="utf-8")
    # The fixture has no `nova_backend/tests/test_*.py`, so the map is empty.
    assert "Paired tests: 0" in test_map
    assert "_No test ↔ source pairs resolved in this vault._" in test_map


def test_code_modules_skips_root_src_init(overlay):
    """`nova_backend/src/__init__.py` is the package marker, not a module.

    A bogus `## __init__` section with one file would clutter CODE_MODULES
    and confuse the graph, so the generator must drop it."""
    module, repo, _docs = overlay
    # Add the real-world root init that used to create the bogus section.
    (repo / "nova_backend" / "src" / "__init__.py").write_text("", encoding="utf-8")
    module.main()

    code_modules = (repo / "_MOCs" / "CODE_MODULES.md").read_text(encoding="utf-8")
    assert "## `__init__`" not in code_modules


def test_test_pairing_ignores_init_and_conftest(overlay):
    """Only `test_<name>.py` files should pair — init/conftest/helpers are noise."""
    module, repo, _docs = overlay
    tests_dir = repo / "nova_backend" / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    # Real pair: test_policy.py -> nova_backend/src/governor/policy.py
    (tests_dir / "test_policy.py").write_text(
        "def test_it():\n    assert True\n", encoding="utf-8"
    )
    # Noise that should be ignored by the pairer.
    (tests_dir / "__init__.py").write_text("", encoding="utf-8")
    (tests_dir / "conftest.py").write_text("", encoding="utf-8")
    (tests_dir / "helpers.py").write_text(
        "def helper():\n    return 1\n", encoding="utf-8"
    )

    notes = module.scan_notes()
    by_module, _ = module._build_import_index(notes)
    pairs = module._pair_tests_to_sources(notes, by_module)

    paired_names = {p.name for p in pairs.keys()}
    assert "test_policy.py" in paired_names
    assert "__init__.py" not in paired_names
    assert "conftest.py" not in paired_names
    assert "helpers.py" not in paired_names


def test_import_graph_resolves_longest_prefix(overlay):
    """An import like `from src.governor.policy import X` must attribute to
    `src.governor.policy`, not the shorter ancestor `src`. The longest-prefix
    rule is how CODE_IMPORTS avoids collapsing every edge to the package root."""
    module, repo, _docs = overlay
    # Rewrite the existing agent note to import the governor policy file.
    agent = repo / "nova_backend" / "src" / "agents" / "_llm_agent.py"
    agent.write_text(
        "from __future__ import annotations\n"
        "from src.governor.policy import something\n"
        "class LLMBackedAgent:\n    pass\n",
        encoding="utf-8",
    )

    notes = module.scan_notes()
    _by_module, imports_by_file = module._build_import_index(notes)

    from pathlib import Path as _P
    rel = _P("nova_backend/src/agents/_llm_agent.py")
    assert rel in imports_by_file
    assert "src.governor.policy" in imports_by_file[rel]
    # The bare `src` root must never appear as a resolved target.
    assert "src" not in imports_by_file[rel]


def test_runtime_graph_queries_cover_runtime_subdirectories(overlay):
    module, repo, _docs = overlay

    module.main()

    graph = (repo / ".obsidian" / "graph.json").read_text(encoding="utf-8")
    assert "path:nova_backend/src/agents" in graph
    assert "path:nova_backend/src/governor" in graph


def test_generated_moc_links_resolve(overlay):
    module, repo, _docs = overlay
    module.main()

    import re

    pattern = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]")
    for moc_path in (repo / "_MOCs").glob("*.md"):
        text = moc_path.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            assert (repo / target).exists() or (repo / f"{target}.md").exists()


def test_generator_never_modifies_source_notes(overlay):
    module, _repo, docs = overlay
    source = docs / "design" / "Phase 4.5" / "note_a.md"
    before = source.read_text(encoding="utf-8")

    module.main()

    assert source.read_text(encoding="utf-8") == before
