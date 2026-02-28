from __future__ import annotations

import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
GENERAL_CHAT_PATH = PROJECT_ROOT / "src" / "skills" / "general_chat.py"
ESCALATION_POLICY_PATH = PROJECT_ROOT / "src" / "conversation" / "escalation_policy.py"


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    mods: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mods.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.add(node.module)
    return mods


def test_escalation_policy_has_no_execution_authority_imports():
    imports = _imports(ESCALATION_POLICY_PATH)
    forbidden_prefixes = (
        "src.governor",
        "src.actions",
        "src.executors",
        "requests",
        "httpx",
    )
    offenders = [imp for imp in imports if any(imp == p or imp.startswith(p + ".") for p in forbidden_prefixes)]
    assert not offenders, f"Escalation policy imports execution/network authority modules: {offenders}"


def test_general_chat_escalation_path_does_not_invoke_capabilities():
    text = GENERAL_CHAT_PATH.read_text(encoding="utf-8", errors="replace")
    forbidden_tokens = [
        "handle_governed_invocation(",
        "ActionRequest(",
        "capability_id=",
        "execute_tts(",
        "WebSearchExecutor(",
        "WebpageLaunchExecutor(",
    ]
    offenders = [tok for tok in forbidden_tokens if tok in text]
    assert not offenders, f"General chat escalation path touches capability execution surface: {offenders}"
