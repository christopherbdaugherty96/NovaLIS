from __future__ import annotations

from pathlib import Path

from tests.adversarial._helpers import SRC_ROOT, ast_imports, read_text

CONVERSATION_ROOT = SRC_ROOT / "conversation"

FORBIDDEN_SNIPPETS = (
    "ActionRequest(",
    "handle_governed_invocation(",
    "TTSEngine",
)

FORBIDDEN_IMPORT_PREFIXES = (
    "requests",
    "httpx",
    "src.executors",
)


def test_conversation_layer_has_no_authority_surface_calls():
    offenders: list[tuple[Path, str]] = []

    for py in CONVERSATION_ROOT.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        text = read_text(py)
        for snippet in FORBIDDEN_SNIPPETS:
            if snippet in text:
                offenders.append((py, snippet))

    assert not offenders, "Conversation files contain authority snippets:\n" + "\n".join(
        f"- {path}: {snippet}" for path, snippet in offenders
    )


def test_conversation_layer_has_no_direct_network_or_executor_imports():
    offenders: list[tuple[Path, str]] = []

    for py in CONVERSATION_ROOT.rglob("*.py"):
        if "__pycache__" in py.parts:
            continue
        for imp in ast_imports(py):
            if any(imp == pref or imp.startswith(pref + ".") for pref in FORBIDDEN_IMPORT_PREFIXES):
                offenders.append((py, imp))

    assert not offenders, "Conversation files contain forbidden imports:\n" + "\n".join(
        f"- {path}: {imp}" for path, imp in offenders
    )
